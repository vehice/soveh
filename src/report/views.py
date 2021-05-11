import json
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core import serializers
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View

from backend.models import AnalysisForm, Sample


class PathologistView(View):
    def request_data(self, request, pathologist=None, date_start=None, date_end=None):
        """Returns a serialized queryset of :model:`backend.AnalysisForm`
        Queryset is filtered first by date range from `date_start` to `date_end`
        if not `date_start` is given then 3 months prior is assumed.
        if not `date_end` is given then current date is assumed.
        if not `pathologist` is given then all pathologist is assumed.
        """
        date_start = (
            (date.today() + relativedelta(months=-3)) if not date_start else date_start
        )

        date_end = (date.today()) if not date_end else date_end

        reports = AnalysisForm.objects.filter(
            created_at__gte=date_start, created_at__lte=date_end
        ).select_related("entryform", "patologo", "stain")

        if pathologist and pathologist > 0:
            reports = reports.filter(patologo_id=pathologist)

        context = []

        for report in reports.iterator():
            user = (
                serializers.serialize("json", [report.patologo])
                if report.patologo is not None
                else json.dumps([])
            )
            context.append(
                {
                    "report": serializers.serialize("json", [report]),
                    "case": serializers.serialize("json", [report.entryform]),
                    "exam": serializers.serialize("json", [report.exam]),
                    "user": user,
                    "stain": serializers.serialize("json", [report.stain]),
                    "workflow": serializers.serialize("json", report.forms.all()),
                }
            )

        return json.dumps(context)

    def get(self, request):
        """Displays multiple tables and charts to generate reportability.
        This is cattered for Pathologists Users, where they can see their
        pending work, and their efficiency.
        """
        pathologists = User.objects.filter(userprofile__profile_id__in=(4, 5))

        user = None

        if (
            request.user.userprofile is not None
            and request.user.userprofile.profile_id in (4, 5)
        ):
            user = request.user

        return render(
            request,
            "pathologist/home.html",
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

        context = self.request_data(request, pathologist, date_start, date_end)

        return HttpResponse(json.dumps(context), content_type="application/json")


class ControlView(View):
    def serialize_data(self, queryset):
        context = []
        for row in queryset.iterator():
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
        date_start = date.today() + relativedelta(months=-3)
        date_end = date.today()

        analysis = AnalysisForm.objects.filter(
            created_at__gte=date_start,
            created_at__lte=date_end,
        )

        pending = analysis.filter(
            pre_report_started=True,
            pre_report_ended=True,
            forms__form_closed=False,
        ).select_related("entryform", "patologo", "stain")

        unassigned = analysis.filter(
            patologo__isnull=True,
            exam__service_id__in=(1, 4),
        ).select_related("entryform", "patologo", "stain")

        finished = analysis.filter(
            forms__form_closed=True,
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
