import json
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from backend.models import AnalysisForm


def serialize_data(queryset):
    """Returns a serialized queryset of :model:`backend.AnalysisForm`
    Queryset is filtered first by date range from `date_start` to `date_end`
    if not `date_start` is given then 5 months prior is assumed.
    if not `date_end` is given then current date is assumed.
    if not `pathologist` is given then all pathologist is assumed.
    """

    context = []

    for report in queryset:
        user = None
        if report.patologo is not None:
            user = report.patologo

        context.append(
            {
                "report": model_to_dict(
                    report,
                    fields=[
                        "assignment_deadline",
                        "manual_cancelled_date",
                        "manual_closing_date",
                        "assignment_done_at",
                        "pre_report_ended",
                        "pre_report_ended_at",
                        "pre_report_started",
                        "pre_report_started_at",
                        "report_code",
                        "score_diagnostic",
                        "score_report",
                        "patologo",
                    ],
                ),
                "case": model_to_dict(
                    report.entryform,
                    fields=[
                        "created_at",
                        "no_caso",
                    ],
                ),
                "exam": model_to_dict(
                    report.exam, fields=["name", "pathologist_assignment"]
                ),
                "user": model_to_dict(user, fields=["first_name", "last_name"]),
                "stain": model_to_dict(report.stain, fields=["name", "abbreviation"]),
                "samples": report.exam.sampleexams_set.filter(
                    sample__entryform_id=report.entryform_id
                ).count(),
                "workflow": model_to_dict(
                    report.forms.all().first(),
                    fields=[
                        "form_closed",
                        "cancelled",
                        "closed_at",
                        "cancelled_at",
                    ],
                ),
            }
        )

        return json.dumps(context, cls=DjangoJSONEncoder)


class ServiceView(View):
    def get(self, request):
        """Displays multiple tables and charts to generate reportability.
        This is cattered for Pathologists Users, where they can see their
        pending work, and their efficiency.
        """
        pathologists = User.objects.filter(
            Q(userprofile__profile_id__in=(4, 5)) | Q(userprofile__is_pathologist=True)
        )

        user = None

        if (
            request.user.userprofile is not None
            and request.user.userprofile.profile_id in (4, 5)
        ):
            user = request.user

        return render(
            request,
            "pathologist/service.html",
            {
                "pathologists": pathologists,
                "current_user": user,
            },
        )

    def post(self, request):
        """Returns :model:`backend.AnalysisForm` filtered by received post parameters.
        Reads the json body from the request, expecting user_id, date_start, and date_end.
        """

        body = json.loads(request.body)
        pathologist = int(body["user_id"]) if str(body["user_id"]).isnumeric() else 0
        date_start = body["date_start"]
        date_end = body["date_end"]

        date_start = (
            (date.today() + relativedelta(months=-5)) if not date_start else date_start
        )

        date_end = (date.today()) if not date_end else date_end

        reports = AnalysisForm.objects.filter(
            Q(manual_cancelled_date__isnull=True) | Q(forms__cancelled=False),
            Q(manual_closing_date__isnull=True) | Q(forms__form_closed=False),
            created_at__gte=date_start,
            created_at__lte=date_end,
        ).select_related("entryform", "patologo", "stain")

        if pathologist and pathologist > 0:
            reports = reports.filter(patologo_id=pathologist)

        context = []

        for report in reports:
            user = None
            if report.patologo is not None:
                user = report.patologo

            try:
                context.append(
                    {
                        "report": model_to_dict(
                            report,
                            fields=[
                                "assignment_deadline",
                                "manual_cancelled_date",
                                "manual_closing_date",
                                "assignment_done_at",
                                "pre_report_ended",
                                "pre_report_ended_at",
                                "pre_report_started",
                                "pre_report_started_at",
                                "report_code",
                                "score_diagnostic",
                                "score_report",
                                "patologo",
                            ],
                        ),
                        "case": model_to_dict(
                            report.entryform,
                            fields=[
                                "created_at",
                                "no_caso",
                            ],
                        ),
                        "exam": model_to_dict(
                            report.exam, fields=["name", "pathologist_assignment"]
                        ),
                        "user": model_to_dict(user, fields=["first_name", "last_name"]),
                        "stain": model_to_dict(
                            report.stain, fields=["name", "abbreviation"]
                        ),
                        "samples": report.exam.sampleexams_set.filter(
                            sample__entryform_id=report.entryform_id
                        ).count(),
                        "workflow": model_to_dict(
                            report.forms.all().first(),
                            fields=[
                                "form_closed",
                                "cancelled",
                                "closed_at",
                                "cancelled_at",
                            ],
                        ),
                    }
                )
            except AttributeError:
                continue

        return HttpResponse(
            json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json"
        )


class EfficiencyView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Displays multiples tables detailing :model:`backend.AnalysisForm` grouped
        by their state.
        """
        pathologists = User.objects.filter(
            Q(userprofile__profile_id__in=(4, 5)) | Q(userprofile__is_pathologist=True)
        )

        user = None

        if (
            request.user.userprofile is not None
            and request.user.userprofile.profile_id in (4, 5)
        ):
            user = request.user

        return render(
            request,
            "pathologist/efficiency.html",
            {
                "pathologists": pathologists,
                "current_user": user,
            },
        )

    def post(self, request):
        """
        Returns a JSON containing detailed information list of :model:`backend.AnalysisForm`
        filtered by request parameters of `date_start`, `date_end`, and `pathologist`.
        """
        body = json.loads(request.body)
        pathologist = int(body["user_id"]) if str(body["user_id"]).isnumeric() else 0
        date_start = body["date_start"]
        date_end = body["date_end"]

        date_start = (
            (date.today() + relativedelta(months=-5)) if not date_start else date_start
        )

        date_end = (date.today()) if not date_end else date_end

        reports = AnalysisForm.objects.filter(
            Q(manual_cancelled_date__isnull=True) | Q(forms__cancelled=False),
            Q(manual_closing_date__isnull=False) | Q(forms__form_closed=True),
            created_at__gte=date_start,
            created_at__lte=date_end,
        ).select_related("entryform", "patologo", "stain")

        if pathologist and pathologist > 0:
            reports = reports.filter(patologo_id=pathologist)

        context = []

        for report in reports:
            user = None
            if report.patologo is not None:
                user = report.patologo

            try:
                context.append(
                    {
                        "report": model_to_dict(
                            report,
                            fields=[
                                "assignment_deadline",
                                "manual_cancelled_date",
                                "manual_closing_date",
                                "assignment_done_at",
                                "pre_report_ended",
                                "pre_report_ended_at",
                                "pre_report_started",
                                "pre_report_started_at",
                                "report_code",
                                "score_diagnostic",
                                "score_report",
                                "patologo",
                            ],
                        ),
                        "case": model_to_dict(
                            report.entryform,
                            fields=[
                                "created_at",
                                "no_caso",
                            ],
                        ),
                        "exam": model_to_dict(
                            report.exam, fields=["name", "pathologist_assignment"]
                        ),
                        "user": model_to_dict(user, fields=["first_name", "last_name"]),
                        "stain": model_to_dict(
                            report.stain, fields=["name", "abbreviation"]
                        ),
                        "samples": report.exam.sampleexams_set.filter(
                            sample__entryform_id=report.entryform_id
                        ).count(),
                        "workflow": model_to_dict(
                            report.forms.all().first(),
                            fields=[
                                "form_closed",
                                "cancelled",
                                "closed_at",
                                "cancelled_at",
                            ],
                        ),
                    }
                )
            except AttributeError:
                continue

        return HttpResponse(
            json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json"
        )


class ControlView(View):
    def serialize_data(self, queryset):
        context = []
        for row in queryset:
            user = (
                serializers.serialize("json", [row.patologo])
                if row.patologo is not None
                else json.dumps([])
            )
            context.append(
                {
                    "report": serializers.serialize("json", [row]),
                    "case": serializers.serialize("json", [row.entryform]),
                    "exam": serializers.serialize("json", [row.exam]),
                    "user": user,
                    "stain": serializers.serialize("json", [row.stain]),
                    "samples": row.exam.sampleexams_set.filter(
                        sample__entryform_id=row.entryform_id
                    ).count(),
                    "workflow": serializers.serialize("json", row.forms.all()),
                }
            )
        return context

    def get(self, request):
        """Displays multiple tables and charts to generate reportability.
        This is cattered for Administration Users, where they can see their
        current workload.
        """
        return render(
            request,
            "control/home.html",
        )

    def post(self, request):
        date_start = date.today() + relativedelta(months=-5)
        date_end = date.today()

        analysis = AnalysisForm.objects.filter(
            Q(forms__form_closed=False) | Q(manual_closing_date__isnull=True),
        )

        pending = analysis.filter(
            pre_report_started=True,
            pre_report_ended=True,
        ).select_related("entryform", "patologo", "stain")

        unassigned = analysis.filter(
            patologo__isnull=True,
            exam__service_id__in=(1, 4),
        ).select_related("entryform", "patologo", "stain")

        finished = analysis.filter(
            Q(forms__form_closed=True) | Q(manual_closing_date__isnull=False),
            pre_report_started=True,
            pre_report_ended=True,
        ).select_related("entryform", "patologo", "stain")

        return HttpResponse(
            json.dumps(
                {
                    "pending": self.serialize_data(pending),
                    "unassigned": self.serialize_data(unassigned),
                    "finished": self.serialize_data(finished),
                }
            ),
            content_type="application/json",
        )
