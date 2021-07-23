import json
import mimetypes
from smtplib import SMTPException

from django.contrib.auth.decorators import login_required, permission_required
from django.core import serializers
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views import View

from review.models import (
    Analysis,
    AnalysisRecipient,
    File,
    MailList,
    Recipient,
    RecipientMail,
    Stage,
)


@login_required
@permission_required("review.view_stage", raise_exception=True)
def index(request):
    """
    Renders template which lists multiple :model:`review.Analysis` grouped by
    their state, allowing the user to move them accross multiple states as necessary.
    """

    recipients = Recipient.objects.all()
    return render(request, "index.html", {"recipients": recipients})


@login_required
@permission_required("review.view_stage", raise_exception=True)
def list(request, index):
    """
    Returns a JSON detailing all :model:`review.Analysis` where their :model:`review.Stage`
    state has the current index.
    """
    analysis = None

    def serialize_data(queryset):
        context = []
        for item in queryset:
            context.append(
                serializers.serialize(
                    "json", [item, item.entryform, item.exam, item.entryform.customer]
                )
            )
        return context

    if index in (1, 2, 3, 4):
        analysis = Analysis.objects.stage(index, request.user)
    else:
        analysis = Analysis.objects.waiting(request.user)

    return JsonResponse(serialize_data(analysis), safe=False)


@login_required
@permission_required(["review.change_stage"], raise_exception=True)
def update_stage(request, pk):
    """
    Updates a :model:`review.Stage`, storing the change in :model:`review.Logbook`.
    """
    analysis = get_object_or_404(Analysis, pk=pk)

    if analysis.report_code is None:
        analysis.set_report_code()

    post = json.loads(request.body)
    state = post["state"]

    stage = Stage.objects.update_or_create(
        analysis=analysis, defaults={"state": state, "created_by": request.user}
    )

    return JsonResponse(serializers.serialize("json", [stage[0], analysis]), safe=False)


@login_required
def analysis_mailing_list(request, pk):
    """
    Returns a JsonResponse with a list detailing the given
    pk's :model:`review.Analysis` its :model:`review.MailList`
    """
    analysis = get_object_or_404(Analysis, pk=pk)
    recipients = []
    for mails in analysis.mailing_lists.all():
        recipients.append(
            {
                "name": mails.name,
                "recipients": serializers.serialize("json", mails.recipients.all()),
            }
        )

    return JsonResponse(json.dumps(recipients), safe=False)


@login_required
@permission_required("review.send_email", raise_exception=True)
def send_email(request, pk):
    """
    Takes a :model:`review.Analysis`'pk and sends an email to all :model:`review.MailList`
    of that Analysis, returns a JSON with `status` according to wether all emails were send
    succesfully.
    Receives in the request an integer defining the language where 0 is english and 1 is spanish.
    It defaults to 1 when the value is invalid or not received.
    Returns a JSON with `status` which can be either OK or ERR, if ERR then it will also send a `code`
    which is either 0 for not file attachment, or 1 for bad email.
    """
    analysis = get_object_or_404(Analysis, pk=pk)
    attachment = analysis.get_sendable_file()

    if not attachment:
        return JsonResponse({"status": "ERR", "code": 0})

    language = json.loads(request.body)

    context = {"analysis": analysis}

    template_name = "email_en.html" if int(language) == 0 else "email_es.html"

    message = get_template(template_name).render(context=context)

    recipients = analysis.get_recipients()

    if len(recipients["to"]) <= 0:
        return JsonResponse({"status": "ERR", "code": 1})

    email = EmailMultiAlternatives(
        subject=analysis.email_subject,
        body=message,
        from_email='"VeHiCe"<reports@vehice.com>',
        to=recipients["to"],
        cc=recipients["cc"],
        bcc=[
            "carlos.sandoval@vehice.com",
            "felipe.fernandez@vehice.com",
            "hector.diaz@vehice.com",
        ],
    )
    email.content_subtype = "html"

    content_type = mimetypes.guess_type(attachment.path.name)[0]
    email.attach(
        f"{analysis.report_code} - {attachment.created_at}",
        attachment.path.read(),
        content_type,
    )

    try:
        email.send()
    except (BadHeaderError, SMTPException):
        return JsonResponse({"status": "ERR", "code": 2})

    stage = Stage.objects.update_or_create(
        analysis=analysis, defaults={"state": 4, "created_by": request.user}
    )
    analysis.close()

    return JsonResponse({"status": "OK"})


class MailListView(View):
    def get(self, request, pk):
        """Returns a JSON list with all :model:`review.Recipients` from a single :model:`review.MailList`."""
        mail_list = get_object_or_404(MailList, pk=pk)

        recipients_lists = RecipientMail.objects.filter(mail_list=mail_list)

        context = []
        for recipient_list in recipients_lists:
            row = model_to_dict(
                recipient_list.recipient,
                fields=["id", "first_name", "last_name", "email"],
            )
            row["is_main"] = recipient_list.is_main
            context.append(row)

        return JsonResponse(context, safe=False)

    def post(self, request, pk):
        """
        Stores a single new :model:`review.MailList`
        and returns the created resource in JSON.

        Required:
            - name
            - recipients
        """
        form_data = json.loads(request.body)

        analysis = get_object_or_404(Analysis, pk=pk)
        customer = analysis.entryform.customer

        mail_list = MailList.objects.create(name=form_data["name"], customer=customer)

        for recipient in form_data["recipients"]:
            RecipientMail.objects.create(
                mail_list=mail_list,
                recipient_id=recipient["id"],
                is_main=recipient["is_main"],
            )

        return JsonResponse(model_to_dict(mail_list, fields=["id", "name"]), safe=False)

    def put(self, request, pk):
        """Updates a single existing :model:`review.MailList`
        and returns a JSON detailing the created resource."""
        form_data = json.loads(request.body)

        mail_list = get_object_or_404(MailList, pk=pk)

        RecipientMail.objects.filter(mail_list=mail_list).delete()

        for recipient in form_data:
            RecipientMail.objects.create(
                mail_list=mail_list,
                recipient_id=recipient["id"],
                is_main=recipient["is_main"],
            )

        return JsonResponse(model_to_dict(mail_list, fields=["id", "name"]), safe=False)


@login_required
def new_recipient(request):
    """
    Stores a single new :model:`lab.Recipient`
    and returns the created resource in JSON.

    Required:
        - first_name
        - email
    Optional:
        - last_name
        - role
    """
    form_data = json.loads(request.body)

    recipient = Recipient.objects.create(
        first_name=form_data["first_name"],
        last_name=form_data["last_name"],
        role=form_data["role"],
        email=form_data["email"],
    )

    return JsonResponse(model_to_dict(recipient), safe=False)


class FileView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        """
        Returns a list of files that belong to a single :model:`review.Analysis`
        """
        analysis = get_object_or_404(Analysis, pk=pk)

        prereport_files = []
        for prefile in analysis.external_reports.all():
            filename = prefile.file.name.split("/")
            prereport_files.append({"name": filename[1], "download": prefile.file.url})

        review_files = []
        for review in File.objects.filter(analysis=analysis):
            review_files.append(
                {
                    "name": review.path.name,
                    "download": review.path.url,
                    "state": review.state,
                    "created_at": review.created_at,
                }
            )

        context = {
            "prereports": prereport_files,
            "reviews": review_files,
        }

        return JsonResponse(context)

    @method_decorator(login_required)
    def post(self, request, pk):
        """
        Stores a file resource and creates a :model:`review.File` to bind it to
        an :model:`review.Stage`
        """

        analysis = get_object_or_404(Analysis, pk=pk)
        stage = Stage.objects.filter(analysis=analysis).first()
        review_file = File(
            path=request.FILES.get("file"),
            analysis=analysis,
            state=stage.state if stage else 0,
            user=request.user,
        )

        review_file.save()

        return JsonResponse(serializers.serialize("json", [review_file]), safe=False)


class AnalysisRecipientView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        """
        Returns a JSON containing a list of all :model:`review.MailList` for the given pk's
        :model:`review.Analysis`'s entryform's customer, including as well the current selected
        ones.
        """
        analysis = get_object_or_404(Analysis, pk=pk)
        customer = analysis.entryform.customer
        mail_lists = MailList.objects.filter(customer=customer)
        current_recipients = AnalysisRecipient.objects.filter(analysis=analysis)
        return JsonResponse(
            {
                "mail_lists": serializers.serialize("json", mail_lists),
                "current_recipients": serializers.serialize("json", current_recipients),
            }
        )

    @method_decorator(login_required)
    def post(self, request, pk):
        """
        Updates the given pk's :model:`review.Analysis`'s related :model:`review.MailList`.
        Returns a JSON containing the status between OK or ERR, in which case will also include
        and array containing ids which caused the error.
        """
        analysis = get_object_or_404(Analysis, pk=pk)

        recipients = json.loads(request.body)

        AnalysisRecipient.objects.filter(analysis=analysis).delete()

        errors = []
        for recipient in recipients:
            try:
                recipient_instace = Recipient.objects.get(pk=recipient["pk"])
            except Recipient.DoesNotExist:
                errors.append(recipient)
                continue
            else:
                AnalysisRecipient.objects.create(
                    analysis=analysis,
                    recipient=recipient_instace,
                    is_main=recipient["is_main"],
                )

        if len(errors) > 0:
            return JsonResponse({"status": "ERR", "errors": errors})

        return JsonResponse({"status": "OK"})
