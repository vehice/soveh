import json
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http.response import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
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
        case = str(analysis.entryform.no_caso[1:]).zfill(5)
        service = str(analysis.exam_id).zfill(3)
        analysis.report_code = f"VHC-{case}-{service}"
        analysis.save()

    post = json.loads(request.body)
    state = post["state"]

    stage = Stage.objects.update_or_create(
        analysis=analysis, defaults={"state": state, "created_by": request.user}
    )

    return JsonResponse(serializers.serialize("json", [stage[0], analysis]), safe=False)


class FileView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        """
        Returns a list of files that belong to a single :model:`review.Analysis`
        """
        analysis = get_object_or_404(Analysis, pk=pk)
        prereport_files = analysis.external_reports.all()
        review_files = File.objects.filter(analysis=analysis).select_related("user")

        context = {
            "prereports": serializers.serialize("json", prereport_files),
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


@login_required
def download_file(request, pk):
    """Returns a FileResponse from the given pk's :model:`review.File` """
    review_file = get_object_or_404(File, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, str(review_file.path))
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"))
    raise Http404


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
