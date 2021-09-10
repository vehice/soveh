import json
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from backend.models import AnalysisForm, SampleExams
from accounts.models import Area, UserArea
from django.core.paginator import Paginator
from django.db.models.aggregates import Count


def get_pathologists(user):
    """Returns a queryset of pathologists.
    This queryset filter the User model according to it's profile, where a profile id of 4 and 5
    indicates a Pathologist, the userprofile also includes a boolean check for wether that user is
    pathologists, in cases where a user doesn't have the profile of a pathologists but it should be
    considered as one.
    It also filters for an Area's Lead to be able to see al Pathologists under their Area.
    """
    pathologists = User.objects.filter(
        Q(userprofile__profile_id__in=(4, 5)) | Q(userprofile__is_pathologist=True)
    )

    if not user.userprofile.profile_id in (1, 2):
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

    return pathologists


@login_required
def service_report(request):
    """Displays multiple tables and charts to generate reportability.
    This is cattered for Pathologists Users, where they can see their
    pending work.
    """
    assigned_areas = UserArea.objects.filter(user=request.user).values_list(
        "area", flat=True
    )

    areas = Area.objects.filter(id__in=assigned_areas)

    if request.user.userprofile.profile_id in (1, 2):
        areas = Area.objects.all()

    pathologists = get_pathologists(request.user)

    return render(
        request,
        "pathologist/service.html",
        {"pathologists": pathologists, "areas": areas},
    )


@login_required
def services_table(request):
    """
    Returns a JSON contaning preformatted data to be display in
    a DataTable filtered by unstarted services.
    """

    draw = int(request.GET.get("draw"))
    length = int(request.GET.get("length"))
    search = request.GET.get("search[value]")
    start = int(request.GET.get("start")) + 1

    pathologist = request.GET.get("pathologists")
    area = request.GET.get("areas")
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    table = request.GET.get("table")

    date_start = (
        (date.today() + relativedelta(weeks=-1)) if not date_start else date_start
    )

    date_end = (date.today()) if not date_end else date_end

    if area:
        area = area.split(";")
        pathologist = UserArea.objects.filter(area_id__in=area).values_list(
            "user_id", flat=True
        )
    elif pathologist:
        pathologist = pathologist.split(";")
    else:
        pathologist = get_pathologists(request.user)

    services = AnalysisForm.objects.filter(
        Q(manual_cancelled_date__isnull=True) | Q(forms__cancelled=False),
        Q(manual_closing_date__isnull=True) | Q(forms__form_closed=False),
        created_at__gte=date_start,
        created_at__lte=date_end,
        patologo__in=pathologist,
    )

    # The table parameter dictates which "state" filter will be applied
    # whereas `pending` it's for non started services, `reading` for
    # started and unfinished services, `reviewing` for
    # started and finished services but unclosed.
    if table == "PENDING":
        services = (
            services.filter(
                pre_report_started=False,
                pre_report_ended=False,
            )
            .order_by("created_at")
            .select_related("entryform__customer", "patologo", "stain", "exam")
        )
    elif table == "READING":
        services = (
            services.filter(
                pre_report_started=True,
                pre_report_ended=False,
            )
            .order_by("created_at")
            .select_related("entryform__customer", "patologo", "stain", "exam")
        )
    elif table == "REVIEWING":
        services = (
            services.filter(
                pre_report_started=True,
                pre_report_ended=True,
            )
            .order_by("created_at")
            .select_related("entryform__customer", "patologo", "stain", "exam")
        )

    if search:
        services = services.filter(
            Q(entryform__no_caso__icontains=search)
            | Q(entryform__customer__name__icontains=search)
            | Q(exam__name__icontains=search)
            | Q(stain__abbreviation__icontains=search)
        )

    services_paginator = Paginator(services, length)

    context_response = {
        "draw": draw + 1,
        "recordsTotal": services.count(),
        "recordsFiltered": services_paginator.count,
        "data": [],
    }

    for page in services_paginator.page_range:
        page_start = services_paginator.get_page(page).start_index()
        if page_start == start:
            services_page = services_paginator.get_page(page).object_list
            for service in services_page:
                samples_count = SampleExams.objects.filter(
                    exam=service.exam,
                    stain=service.stain,
                    sample__entryform=service.entryform,
                ).count()

                row = {
                    "case": model_to_dict(
                        service.entryform, fields=["no_caso", "created_at"]
                    ),
                    "customer": model_to_dict(service.entryform.customer),
                    "exam": model_to_dict(service.exam),
                    "stain": model_to_dict(service.stain),
                    "pathologist": model_to_dict(
                        service.patologo, fields=["first_name", "last_name"]
                    ),
                    "service": model_to_dict(service, exclude=["external_reports"]),
                    "samples_count": samples_count,
                }

                context_response["data"].append(row)

            # Row data should only include current page
            break

    return JsonResponse(context_response)


class EfficiencyView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Displays multiples tables detailing :model:`backend.AnalysisForm` grouped
        by their state.
        """
        assigned_areas = UserArea.objects.filter(user=request.user).values_list(
            "area", flat=True
        )

        areas = Area.objects.filter(id__in=assigned_areas)
        if request.user.userprofile.profile_id in (1, 2):
            areas = Area.objects.all()

        return render(
            request,
            "pathologist/efficiency.html",
            {
                "pathologists": get_pathologists(request.user),
                "areas": areas,
            },
        )

    def post(self, request):
        """
        Returns a JSON containing detailed information list of :model:`backend.AnalysisForm`
        filtered by request parameters of `date_start`, `date_end`, and `pathologist`.
        """
        body = json.loads(request.body)
        pathologist = (
            int(body["user_id"])
            if str(body["user_id"]).isnumeric()
            else get_pathologists(request.user).values_list("id", flat=True)
        )
        area = int(body["area_id"]) if str(body["area_id"]).isnumeric() else 0
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
        else:
            reports = reports.filter(
                patologo_id__in=get_pathologists(request.user).values_list(
                    "id", flat=True
                )
            )

        if area and area > 0:
            users = area.users
            reports = reports.filter(patologo_id__in=users)

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
                        "customer": model_to_dict(
                            report.entryform.customer,
                            fields=[
                                "name",
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
    def get(self, request):
        """Displays multiple tables and charts to generate reportability.
        This is cattered for Administration Users, where they can see their
        current workload.
        """

        services = (
            AnalysisForm.objects.filter(
                Q(manual_cancelled_date__isnull=True) | Q(forms__cancelled=False),
                Q(manual_closing_date__isnull=True) | Q(forms__form_closed=False),
                exam__pathologists_assignment=True,
                patologo__isnull=True,
                pre_report_started=False,
                pre_report_ended=False,
            )
            .annotate(samples=Count("entryform__sample"))
            .select_related("entryform", "exam", "stain", "patologo")
        )

        return render(request, "control/home.html", {"services": services})
