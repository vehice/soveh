import json
import mimetypes
import os
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http.response import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views import View

from review.models import Analysis, AnalysisMailList, File, MailList, Stage


@login_required
def index(request):
    """
    Renders template which lists multiple :model:`review.Analysis` grouped by
    their state, allowing the user to move them accross multiple states as necessary.
    """
    return render(request, "index.html")


@login_required
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
                {
                    "analysis": serializers.serialize("json", [item]),
                    "case": serializers.serialize("json", [item.entryform]),
                    "exam": serializers.serialize("json", [item.exam]),
                }
            )
        return context

    if index in (1, 2, 3, 4):
        analysis = Analysis.objects.stage(index)
    else:
        analysis = Analysis.objects.waiting()

    return JsonResponse(serialize_data(analysis), safe=False)


@login_required
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
def download_file(request, pk):
    """Returns a FileResponse from the given pk's :model:`review.File` """
    review_file = get_object_or_404(File, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, str(review_file.path))
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"))
    raise Http404


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

    email = EmailMultiAlternatives(
        analysis.email_subject,
        message,
        "report@vehice.com",
        analysis.get_recipients(),
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
        return JsonResponse({"status": "ERR", "code": 1})

    stage = Stage.objects.update_or_create(
        analysis=analysis, defaults={"state": 4, "created_by": request.user}
    )
    return JsonResponse({"status": "OK"})


class FileView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        """
        Returns a list of files that belong to a single :model:`review.Analysis`
        """
        analysis = get_object_or_404(Analysis, pk=pk)
        prereport_files = analysis.entryform.attached_files.all()
        files = []
        for prefile in prereport_files:
            filename = prefile.file.name.split("/")
            files.append({"name": filename[1], "download": prefile.file.url})

        review_files = File.objects.filter(analysis=analysis).select_related("user")

        context = {
            "prereports": files,
            "reviews": serializers.serialize("json", review_files),
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


class MailView(View):
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
        current_lists = AnalysisMailList.objects.filter(analysis=analysis)
        return JsonResponse(
            {
                "mail_lists": serializers.serialize("json", mail_lists),
                "current_lists": serializers.serialize("json", current_lists),
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

        mail_list_pk = json.loads(request.body)

        AnalysisMailList.objects.filter(analysis=analysis).delete()

        errors = []
        for pk in mail_list_pk:
            try:
                mail_list = MailList.objects.get(pk=pk)
            except MailList.DoesNotExist:
                errors.append(pk)
                continue
            AnalysisMailList.objects.create(analysis=analysis, mail_list=mail_list)

        if len(errors) > 0:
            return JsonResponse({"status": "ERR", "errors": errors})

        return JsonResponse({"status": "OK"})
