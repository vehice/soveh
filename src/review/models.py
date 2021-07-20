from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from backend.models import AnalysisForm, Customer
from accounts.models import UserArea
from datetime import datetime


class AnalysisManager(models.Manager):
    """
    Custom Manager for Case, where it mainly filters all :model:`backend.Entryform`
    according to it's current :model:`workflows.Form` state. Alongside some helper
    functions.
    """

    def get_queryset(self, user=None):
        queryset = (
            super()
            .get_queryset()
            .filter(
                forms__form_closed=0,
                forms__cancelled=0,
                manual_cancelled_date__isnull=True,
                manual_closing_date__isnull=True,
                exam__pathologists_assignment=True,
                pre_report_started=True,
                pre_report_ended=True,
            )
            .order_by("entryform__created_at")
        )

        if user is not None and user.userprofile.profile_id not in (1, 2):
            pathologists = User.objects.filter(
                Q(userprofile__profile_id__in=(4, 5))
                | Q(userprofile__is_pathologist=True)
            )

            assigned_areas = UserArea.objects.filter(user=user, role=0)
            pks = [user.id]

            for user_area in assigned_areas:
                users = (
                    UserArea.objects.filter(area=user_area.area)
                    .exclude(user=user)
                    .values_list("user", flat=True)
                )
                pks.extend(users)

            pathologists = pathologists.filter(pk__in=pks)

            return queryset.filter(patologo_id__in=pathologists)

        return queryset

    def waiting(self, user):
        """
        Returns all :model:`backend.AnalysisForm` which a Pathologist
        has finished studying but hasn't being reviewed yet.
        """
        return (
            self.get_queryset(user)
            .filter(
                Q(stages__isnull=True) | Q(stages__state=0),
            )
            .select_related("entryform", "exam", "stain")
        )

    def stage(self, state_index, user):
        """
        Returns all :model:`backend.AnalysisForm` according to it's
        :model:`review.Stage`.STATE index.
        """

        return (
            self.get_queryset(user)
            .filter(stages__state=state_index)
            .select_related("entryform", "exam", "stain")
        )


class UndeletedManager(models.Manager):
    """Custom manager for models with deleted_at fields.
    It's main purpouse is to scope the queryset to all
    instances that haven't been deleted.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Analysis(AnalysisForm):
    """
    Proxy class for :model:`backend.AnalysisForm`, it's used in the Review app to filter
    AnalysisForm according to their status, and order them by priorities,
    without touching the other app's implementation.
    """

    objects = AnalysisManager()

    @property
    def email_subject(self):
        """Returns a string of key data for an email's subject"""
        subject = []
        case = self.entryform

        if case.customer:
            subject.append(case.customer.name)

        if case.center:
            subject.append(case.center)

        subject.append(self.exam.name)
        subject.append(self.report_code)

        return "/".join(subject)

    def set_report_code(self):
        """Stores a report code following the format VHC-00000-000"""
        case = str(self.entryform.no_caso[1:]).zfill(5)
        service = str(self.exam_id).zfill(3)
        self.report_code = f"VHC-{case}-{service}"
        self.save()

    def get_recipients(self):
        """Returns a dictionary containing all emails from self's MailLists, separated by To and CC."""
        to = []
        cc = []
        for mails in self.mailing_lists.all():
            mail_dict = mails.recipients_email
            to.extend(mail_dict["to"])
            cc.extend(mail_dict["cc"])
        return {"to": to, "cc": cc}

    def get_sendable_file(self):
        """Returns self's :model:`review.File` which is available to be send."""
        sendable = None
        try:
            sendable = File.objects.filter(analysis=self, state=3).latest("created_at")
        except File.DoesNotExist:
            pass
        return sendable

    def close(self):
        form = self.forms.get()
        form.form_closed = True
        form.closed_at = datetime.now()
        form.save()

    class Meta:
        proxy = True
        permissions = (("send_email", "Can send an email"),)


class Stage(models.Model):
    """
    Details a single stage in which an :model:`review.Analysis` is currently at.
    """

    STATES = (
        (0, "ESPERA"),
        (1, "FORMATO"),
        (2, "REVISION"),
        (3, "ENVIO"),
        (4, "FINALIZADO"),
    )

    analysis = models.ForeignKey(
        AnalysisForm, on_delete=models.CASCADE, related_name="stages"
    )
    state = models.CharField(max_length=1, choices=STATES, default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="review_stages", null=True
    )
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Logbook.objects.create(stage=self, state=self.state, user=self.created_by)


class Logbook(models.Model):
    """
    Stores detailed information relate to a :model:`review.Stage` changes.
    """

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="logbooks")

    state = models.CharField(max_length=1, choices=Stage.STATES)

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="logbooks", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class File(models.Model):
    """Stores a single file path in the database alognside it's related :model:`review.Stage`"""

    path = models.FileField("reviews/%Y_%m_%d/")
    analysis = models.ForeignKey(
        Analysis, on_delete=models.CASCADE, related_name="files"
    )
    state = models.CharField(max_length=1, choices=Stage.STATES)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="files", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Recipient(models.Model):
    """
    Stores a single resource which will receive an email with :model:`review.File` for it's related
    :model:`review.Analysis` whenever this it's moved to a :model:`review.Stage` finished.
    """

    objects = UndeletedManager()
    items = models.Manager()

    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Desactivado")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class MailList(models.Model):
    """
    Allows grouping multiple :model:`review.Recipient` under the same :model:`backend.Customer`
    """

    objects = UndeletedManager()
    items = models.Manager()

    name = models.CharField(max_length=255)
    customer = models.ForeignKey(
        to=Customer, on_delete=models.CASCADE, related_name="mailing_lists"
    )
    recipients = models.ManyToManyField(
        to=Recipient, related_name="mailing_lists", through="RecipientMail"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Desactivado")

    @property
    def recipients_email(self):
        """Returns a list of email for all Recipients."""
        to = []
        cc = []

        for entry in RecipientMail.objects.filter(mail_list=self, is_main=True):
            to.append(entry.recipient.email)

        for entry in RecipientMail.objects.filter(mail_list=self, is_main=False):
            cc.append(entry.recipient.email)

        return {"to": to, "cc": cc}

    def __str__(self):
        return self.name


class RecipientMail(models.Model):
    recipient = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, related_name="mail_lists"
    )
    mail_list = models.ForeignKey(
        MailList, on_delete=models.CASCADE, related_name="recipients_emails"
    )
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = "review_recipient_mail"

    def __str__(self):
        return f"{self.mail_list.name} {self.recipient.first_name}"


class AnalysisRecipient(models.Model):
    """
    A :model:`review.Analysis` may contain multiple :model:`review.Recipient` and vice-versa thus this model works
    as a middle-man to join them.
    """

    analysis = models.ForeignKey(to=Analysis, on_delete=models.CASCADE)
    recipient = models.ForeignKey(to=Recipient, on_delete=models.CASCADE)
    is_main = models.BooleanField(
        verbose_name="Is primary recipient (TO)", default=True
    )
