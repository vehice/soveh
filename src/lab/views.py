import csv
import json
from datetime import datetime, timedelta

from dateutil.parser import ParserError, parse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView

from backend.models import Exam, Organ, OrganUnit, SampleExams, Stain, Unit
from lab.models import (
    Analysis,
    Case,
    Cassette,
    CassetteOrgan,
    Process,
    Slide,
    UnitDifference,
)
from lab.services import change_case_step, generate_differences


@login_required
def home(request):
    cassettes_to_build = Unit.objects.filter(
        cassettes__isnull=True,
        organs__isnull=False,
        identification__entryform__entry_format__in=[1, 2, 6, 7],
    ).count()
    cassettes_to_process = Cassette.objects.filter(processed_at=None).count()
    differences_count = UnitDifference.objects.filter(status=0).count()
    slides_to_build = Cassette.objects.filter(
        slides=None, processed_at__isnull=False
    ).count()
    return render(
        request,
        "home.html",
        {
            "cassettes_to_build": cassettes_to_build,
            "cassettes_to_process": cassettes_to_process,
            "cassettes_differences": differences_count,
            "cassettes_workload": cassettes_to_build
            + cassettes_to_process
            + differences_count,
            "slides_to_build": slides_to_build,
        },
    )


# Case related views


@method_decorator(login_required, name="dispatch")
class CaseReadSheet(DetailView):
    """Displays format for a :model:`lab.Case` read sheet.
    A read sheet contains information for a Case's :model:`lab.Slide`
    including that slide's :model:`backend.Organ` and :model:`backend.Stain`
    """

    model = Case
    template_name = "cases/read_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        units = Unit.objects.filter(Q(identification__entryform=self.get_object()))
        slides = Slide.objects.filter(unit__in=units).order_by("correlative")
        context["slides"] = slides
        return context


@method_decorator(login_required, name="dispatch")
class CaseDetail(DetailView):
    """Displays detailed data of a Case.
    Data is displayed in a boilerplate template that can be
    embeded using javascript anywhere in a page as needed.
    """

    model = Case
    template_name = "cases/detail.html"


@login_required
def case_process_state(request, pk):
    """
    Displays general information, lab process state, and service reading availability
    for the provided pk's :model:`lab.Case`
    """

    case = get_object_or_404(Case, pk=pk)
    analysis = Analysis.objects.filter(entryform=case)

    return render(request, "cases/state.html", {"case": case, "analysis": analysis})


# Organ related views


@login_required
def organ_list(request):
    """Returns a list of all :model:`backend.Organ`"""
    organs = Organ.objects.all()

    return HttpResponse(
        serializers.serialize("json", organs), content_type="application/json"
    )


# Stain related views


@login_required
def stain_list(request):
    """Returns a list of all :model:`backend.Stain`"""
    stains = Stain.objects.all()

    return HttpResponse(
        serializers.serialize("json", stains), content_type="application/json"
    )


# Unit related views


@login_required
def unit_select_options(request):
    """
    Returns a formatted JSON to be used in a Select2 input
    listing all Units with their Case.

    **REQUEST**
        `search`: Search term to look for in Units, Identifications, and Entryforms.
        `page`: Paginator's current page.

    """
    search_term = request.GET.get("search")

    if not search_term:
        return JsonResponse({})

    units = Unit.objects.filter(
        Q(correlative__icontains=search_term)
        | Q(identification__cage__icontains=search_term)
        | Q(identification__entryform__no_caso__icontains=search_term)
        | Q(
            identification__entryform__forms__cancelled=0,
            identification__entryform__forms__form_closed=0,
        )
    ).select_related("identification__entryform")

    includes_cassettes = request.GET.get("cassettes")

    cassettes = None

    if includes_cassettes:
        cassettes = Cassette.objects.filter(
            Q(correlative__icontains=search_term)
            | Q(unit__correlative__icontains=search_term)
            | Q(unit__identification__cage__icontains=search_term)
            | Q(unit__identification__entryform__no_caso__icontains=search_term)
            | Q(
                identification__entryform__forms__cancelled=0,
                identification__entryform__forms__form_closed=0,
            )
        ).select_related("unit__identification__entryform")

    page = request.GET.get("page")

    units_paginator = Paginator(units, 20)
    units_paginated = units_paginator.get_page(page)

    response = {"results": [], "pagination": {"more": units_paginated.has_next()}}

    for unit in units_paginated:
        response["results"].append(
            {
                "id": unit.id,
                "text": f"""{unit.identification.entryform.no_caso} / {unit.identification.cage} / {unit.correlative}""",
            }
        )

    if cassettes:
        cassettes_paginator = Paginator(cassettes, 20)
        cassettes_paginated = cassettes_paginator.get_page(page)

        for cassette in cassettes_paginated:
            response["results"].append(
                {
                    "id": f"""cassette.{cassette.id}""",
                    "text": f"""{cassette.unit.identification.entryform.no_caso} / {cassette.unit.identification.cage} / {cassette.unit.correlative} / {cassette.correlative}""",
                }
            )

    return JsonResponse(response)


# Cassette related views


class CassetteHome(View):
    def get_context(self):
        """
        Returns common context for the class.
        """
        build_count = Unit.objects.filter(
            cassettes__isnull=True,
            identification__entryform__entry_format__in=[1, 2, 6, 7],
        ).count()
        process_count = Cassette.objects.filter(processed_at=None).count()
        differences_count = UnitDifference.objects.filter(status=0).count()
        return {
            "build_count": build_count,
            "process_count": process_count,
            "differences_count": differences_count,
        }

    def report_created_cassettes(self, date_range, response=None):
        """
        Returns a list with :model:`lab.Cassette` which have been
        created within the given date range tuple (start, end).
        """
        cassettes = Cassette.objects.filter(
            created_at__gte=date_range[0], created_at__lte=date_range[1]
        )

        response_data = []

        if response:
            csv_writer = csv.writer(response)
            csv_writer.writerow(
                ["Caso", "Identificacion", "Unidad", "Cassette", "Organos", "Codigo"]
            )

            for cassette in cassettes:
                organs_text = ",".join(
                    [organ.abbreviation for organ in cassette.organs.all()]
                )
                csv_writer.writerow(
                    [
                        cassette.unit.identification.entryform.no_caso,
                        str(cassette.unit.identification),
                        cassette.unit.correlative,
                        cassette.correlative,
                        organs_text,
                        cassette.tag,
                    ]
                )

            return response

        return cassettes

    def report_differences_cassettes(self, date_range, include_solved, response=None):
        """
        Returns a list with :model:`lab.UnitDifferences` which have been
        created withing the given date range tuple (start, end).
        """
        differences = UnitDifference.objects.filter(
            created_at__gte=date_range[0], created_at__lte=date_range[1]
        )

        if not include_solved:
            differences = differences.filter(status=0)

        if response:
            csv_writer = csv.writer(response)
            csv_writer.writerow(
                ["Caso", "Identificacion", "Unidad", "Organo", "Cantidad"]
            )

            for difference in differences:
                csv_writer.writerow(
                    [
                        difference.unit.identification.entryform.no_caso,
                        str(difference.unit.identification),
                        difference.unit.correlative,
                        difference.organ,
                        difference.difference,
                    ]
                )

            return response

        return differences

    @method_decorator(login_required)
    def get(self, request):
        """Dashboard for Cassettes.

        Includes links to build, reports, and index.
        """
        context = self.get_context()

        return render(request, "cassettes/home.html", context)

    @method_decorator(login_required)
    def post(self, request):
        """
        Returns either a FileResponse or an HttpResponse
        from the given parameters.

        **REQUEST**
            ``report_name``: Name of the report that will be generated. ("created", "differences")
            ``from_date``: Earlier limit for the date range.
            ``to_date``: Latest limit for the date range. Defaults to current.
            ``include_solved``: Latest limit for the date range. Defaults to current.
            ``report_type``: boolean which determines if the response is a file or on-screen.
        """
        try:
            from_date = parse(request.POST.get("from_date"))
        except ParserError:
            raise Http404("Sin fecha de inicio.")
        try:
            to_date = request.POST.get("to_date")
        except ParserError:
            to_date = datetime.now()

        date_range = (from_date, to_date)

        report_name = request.POST.get("report_name")
        is_csv = int(request.POST.get("report_type"))

        if is_csv:
            response = HttpResponse(content_type="text/csv")
            filename = (
                "Cassettes creados"
                if report_name == "created"
                else "Diferencias en Unidades"
            )
            response[
                "Content-Disposition"
            ] = f"attachment; filename='Reporte {filename} {from_date} - {to_date}.csv'"

            if report_name == "created":
                return self.report_created_cassettes(date_range, response)
            elif report_name == "differences":
                return self.report_differences_cassettes(date_range, response)

            raise Http404("Tipo de reporte invalido.")

        context = self.get_context()
        context["report_name"] = report_name
        if report_name == "created":
            context["rows"] = self.report_created_cassettes(date_range)
        elif report_name == "differences":
            include_solved = bool(request.POST.get("include_solved"))
            context["rows"] = self.report_differences_cassettes(
                date_range, include_solved
            )

        return render(request, "cassettes/home.html", context)


@login_required
def cassette_differences(request):
    """
    List of all :model:`lab.UnitDifference` generated during :view:`lab.CassetteBuild`
    that haven't been resolved (as in status=1).
    """
    units = Unit.objects.filter(cassettes__isnull=False)
    differences = UnitDifference.objects.filter(status=0)
    context = {"differences": differences}
    return render(request, "cassettes/differences.html", context)


@login_required
def redirect_to_workflow_edit(request, pk, step):
    """Redirects a case to it's workflow form according to the given step"""
    case, form = change_case_step(pk, step)
    return redirect(reverse("workflow_w_id", kwargs={"form_id": form.pk}))


@login_required
def update_unit_difference(request, pk):
    """
    Toggle the state for the given :model:`lab.UnitDifference` between
    0 (Unreviewed) and 1 (reviewed).
    """
    difference = get_object_or_404(UnitDifference, pk=pk)
    difference.status = not difference.status
    log_message = request.POST.get("message")
    if log_message:
        difference.status_change_log = f"{difference.status_change_log};{log_message}"
    difference.save()

    return JsonResponse(model_to_dict(difference))


@login_required
def cassette_prebuild(request):
    """
    Receives a JSON with 2 keys: `selected` which is an array of unit ids;
    and `rules` which is a dictionary that dictates how the cassettes are build,

    * rules["unique"]
        Is an array of unit ids in which all of those units are to be put by themselves
        in their own Cassette.

    * rules["groups"]
        Is an array of arrays containing unit ids, in which all of those groups must be put
        together in their own Cassettes.

    * rules["max"]
        Is an integer greater than or equal to 0, and any Cassette can't have more organs than this
        number, unless is 0, then a Cassette can have as many Organs as available.


    This returns a JSON containing Cassette prototypes.
    """
    items = json.loads(request.body)
    units_id = items["selected"]
    rules = items["rules"]

    units = Unit.objects.filter(pk__in=units_id).order_by("identification__entryform")

    response = []

    def response_format(unit, organs, count):
        return {
            "case": unit.identification.entryform.no_caso,
            "identification": str(unit.identification),
            "unit": unit.correlative,
            "unit_id": unit.id,
            "cassette": count,
            "organs": serializers.serialize("json", unit.organs.all()),
            "cassette_organs": serializers.serialize("json", organs),
        }

    for unit in units:
        last_correlative = 1
        cassette_highest_correlative = unit.cassettes.order_by("-correlative").first()
        cassette_count = 1
        if cassette_highest_correlative:
            cassette_count = cassette_highest_correlative.correlative
        excludes = []

        if rules["uniques"] and len(rules["uniques"]) > 0:
            organs = unit.organs.filter(pk__in=rules["uniques"])

            if not organs.count() <= 0:
                for organ in organs:
                    response.append(response_format(unit, [organ], cassette_count))
                    cassette_count += 1

                excludes.extend([pk for pk in rules["uniques"]])

        if rules["groups"] and len(rules["groups"]) > 0:
            for group in rules["groups"]:
                organs = unit.organs.filter(pk__in=group).exclude(pk__in=excludes)

                if not organs.count() <= 0:
                    response.append(response_format(unit, organs, cassette_count))
                    cassette_count += 1
                    excludes.extend([pk for pk in group])

        organs = unit.organs.exclude(pk__in=excludes).order_by("-id")

        if rules["max"] and rules["max"] > 0:
            organs_pages = Paginator(organs, rules["max"], allow_empty_first_page=False)

            for page in organs_pages.page_range:
                try:
                    current_page = response_format(
                        unit, organs_pages.get_page(page), cassette_count
                    )
                except InvalidPage:
                    continue
                else:
                    response.append(current_page)
                    cassette_count += 1
        elif organs.count() > 0:
            response.append(response_format(unit, organs, cassette_count))

    return HttpResponse(json.dumps(response), content_type="application/json")


class CassetteBuild(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Displays list of available :model:`lab.Cassette` to build,
        from :model:`backend.Unit` where their :model:`backend.EntryForm`.entry_format
        is either (1, "Tubo"), (2, "Cassette"), (6, "Vivo"), (7, "Muerto").

        If the request is done through Ajax then response is a Json
        with the same list, this is used to update the table.

        **Context**
        ``units``
            A list of :model:`backend.EntryForm`
            with prefetched :model:`backend.Identification`
            and :model:`backend.Unit`

        **Template**
        ``lab/cassettes/build.html``
        """

        units = (
            Unit.objects.filter(
                cassettes__isnull=True,
                organs__isnull=False,
                identification__entryform__entry_format__in=[1, 2, 6, 7],
            )
            .select_related("identification__entryform")
            .distinct()
        )

        organs = serializers.serialize("json", Organ.objects.all())

        return render(
            request, "cassettes/build.html", {"units": units, "organs": organs}
        )

    @method_decorator(login_required)
    def post(self, request):
        """
        Creates a new Cassette storing build_at date and their correlative
        according to their :model:`backend.Unit` and :model:`backend.EntryForm`
        """

        request_input = json.loads(request.body)

        if "units" not in request_input or not request_input["units"]:
            return JsonResponse(
                {"status": "ERROR", "message": "units is empty"}, status=400
            )

        units = request_input["units"]

        try:
            build_at = parse(request_input["build_at"])
        except (KeyError, ParserError):
            build_at = datetime.now()

        created = []
        errors = []
        differences = False
        for row in units:
            try:
                unit = Unit.objects.get(pk=row["id"])
            except ObjectDoesNotExist:
                return JsonResponse(
                    {
                        "status": "ERROR",
                        "message": "Unit id %d does not exists" % row["id"],
                    },
                    status=400,
                )

            if "correlative" in row and row["correlative"]:
                cassette = unit.cassettes.create(
                    build_at=build_at, correlative=row["correlative"]
                )
            else:
                cassette_highest_correlative = unit.cassettes.order_by(
                    "-correlative"
                ).first()
                correlative = 1
                if cassette_highest_correlative:
                    correlative = cassette_highest_correlative.correlative
                cassette = unit.cassettes.create(
                    build_at=build_at, correlative=correlative
                )

            for organ_id in row["organs"]:
                try:
                    organ = Organ.objects.get(pk=organ_id)
                except Organ.DoesNotExist:
                    errors.append(
                        {
                            "status": "ERROR",
                            "message": "Organ id %d does not exists" % organ_id,
                        }
                    )
                else:
                    CassetteOrgan.objects.create(organ=organ, cassette=cassette)
                    created.append(cassette)

            if not differences:
                differences = generate_differences(unit)

        return JsonResponse(
            {
                "created": serializers.serialize("json", created),
                "errors": errors,
                "differences": differences,
            },
            safe=False,
            status=201,
        )


@method_decorator(login_required, name="dispatch")
class CassetteIndex(ListView):
    """Displays a list of Cassettes.
    Render a template list with all Cassettes including access to edit and reprocess
    buttons.

        **Context**
        ``cassettes``
            A list of :model:`lab.Cassette`
            with prefetched :model:`backend.Organ`

        **Template**
        ``lab/cassettes/index.html``

    """

    template_name = "cassettes/index.html"
    context_object_name = "cassettes"

    def get_queryset(self):
        cassette_range = self.request.GET.get("range")
        now = datetime.now()

        time_delta = timedelta(days=7)
        if cassette_range == "2":
            time_delta = timedelta(days=30)
        elif cassette_range == "3":
            time_delta = timedelta(days=90)
        elif cassette_range == "4":
            time_delta = timedelta(days=180)

        date_range = now - time_delta

        cassettes = (
            Cassette.objects.filter(
                created_at__gte=date_range,
                unit__identification__entryform__forms__cancelled=0,
                unit__identification__entryform__forms__form_closed=0,
            )
            .select_related("unit__identification__entryform")
            .prefetch_related("organs")
        )

        return cassettes


class CassetteDetail(View):
    def serialize_data(self, cassette):
        return {
            "cassette": serializers.serialize("json", [cassette]),
            "organs": serializers.serialize("json", cassette.organs.all()),
        }

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Returns a JSON detailing Cassette.

        **CONTEXT**

        ``cassette``
            Detailed data for the requested :model:`lab.Cassette`
        ``organs``
            List of :model:`backend.Organ` that belongs to requested Cassette.

        """
        cassette = get_object_or_404(Cassette, pk=kwargs["pk"])
        data = self.serialize_data(cassette)
        return HttpResponse(json.dumps(data), content_type="application/json")

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Updates a Cassette.
        Returns serialized data of the updated Cassette.

        **REQUEST**

            ``build_at``
                Updated build_at date. Optional.
            ``correlative``
                Updated correlative. Optional.
            ``organs``
                List of :model:`backend.Organ`. This will set the current
                organs for this Cassette. Optional.

        """
        cassette = get_object_or_404(Cassette, pk=kwargs["pk"])

        request_input = json.loads(request.body)

        if "build_at" in request_input:
            try:
                build_at = parse(request_input["build_at"])
            except (ParserError):
                build_at = cassette.build_at
            else:
                cassette.build_at = build_at
        if "correlative" in request_input:
            cassette.correlative = request_input["correlative"]
        if "organs" in request_input:
            CassetteOrgan.objects.filter(cassette=cassette).delete()
            for organ_id in request_input["organs"]:
                try:
                    CassetteOrgan.objects.create(cassette=cassette, organ_id=organ_id)
                except IntegrityError:
                    raise Http404("Organ not found.")

        if "build_at" in request_input or "correlative" in request_input:
            cassette.save()

        data = self.serialize_data(cassette)

        return HttpResponse(json.dumps(data), content_type="application/json")


class CassetteProcess(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Displays a list of :model:`lab.Cassette` which ``processed_at`` date is null.
        """
        cassettes = Cassette.objects.filter(processed_at=None).select_related(
            "unit__identification__entryform"
        )
        return render(request, "cassettes/process.html", {"cassettes": cassettes})

    @method_decorator(login_required)
    def post(self, request):
        """
        Updates the given :model:`lab.Cassette` with the given date for `processed_at`.
        """
        request_data = json.loads(request.body)

        try:
            processed_at = parse(request_data["processed_at"])
        except (ParserError):
            processed_at = datetime.now()

        cassettes_updated = Cassette.objects.filter(
            pk__in=request_data["cassettes"]
        ).update(processed_at=processed_at)

        return JsonResponse(cassettes_updated, safe=False)


# Slide related views


class SlideHome(View):
    def get_context(self):
        """
        Returns common context for the class.
        """

        units_count = Unit.objects.filter(
            identification__entryform__entry_format=5,
            identification__entryform__forms__cancelled=0,
            identification__entryform__forms__form_closed=0,
        ).count()
        cassettes_count = Cassette.objects.filter(
            slides=None, processed_at__isnull=False
        ).count()
        build_count = units_count + cassettes_count
        differences_count = UnitDifference.objects.filter(status=0).count()
        return {
            "build_count": build_count,
        }

    def report_created_slides(self, date_range, response=None):
        """
        Returns a list with :model:`lab.Cassette` which have been
        created within the given date range tuple (start, end).
        """
        slides = Slide.objects.filter(
            created_at__gte=date_range[0], created_at__lte=date_range[1]
        )

        response_data = []

        if response:
            csv_writer = csv.writer(response)
            csv_writer.writerow(
                ["Caso", "Identificacion", "Unidad", "Correlativo", "Organos", "Codigo"]
            )

            for slide in slides:
                organs_text = ",".join([organ.abbreviation for organ in slide.organs])
                csv_writer.writerow(
                    [
                        slide.unit.identification.entryform.no_caso,
                        str(slide.unit.identification),
                        slide.unit.correlative,
                        slide.correlative,
                        organs_text,
                        slide.tag,
                    ]
                )

            return response

        return slides

    @method_decorator(login_required)
    def get(self, request):
        """Dashboard for Slides.

        Includes links to build, reports, and index.
        """
        context = self.get_context()

        return render(request, "slides/home.html", context)

    @method_decorator(login_required)
    def post(self, request):
        """
        Returns either a FileResponse or an HttpResponse
        from the given parameters.

        **REQUEST**
            ``from_date``: Earlier limit for the date range.
            ``to_date``: Latest limit for the date range. Defaults to current.
            ``report_type``: boolean which determines if the response is a file or on-screen.
        """
        try:
            from_date = parse(request.POST.get("from_date"))
        except ParserError:
            raise Http404("Sin fecha de inicio.")
        try:
            to_date = request.POST.get("to_date")
        except ParserError:
            to_date = datetime.now()

        date_range = (from_date, to_date)

        is_csv = int(request.POST.get("report_type"))

        if is_csv:
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"
            ] = f"attachment; filename=Reporte Slides Generados {from_date} - {to_date}.csv"

            return self.report_created_slides(date_range, response)

        context = self.get_context()
        context["show_report"] = True
        context["rows"] = self.report_created_slides(date_range)

        return render(request, "slides/home.html", context)


@login_required
def slide_prebuild(request):
    """
    Returns a JSON response detailing :model:`lab.Slide` prototypes that
    could be generated from the request's Cassette or Units list.
    """
    try:
        items = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({})

    slides = []
    prev_case = None
    slide_correlative = 1
    for item in items:
        cassette = None
        unit = None
        organs_subject = None

        # Cassette is an optional parameter, Unit is required, if no Cassette is given
        # then use the unit_id to prototype the Slide
        if item["cassette"] > 0:
            cassette = Cassette.objects.get(pk=item["cassette"])
            unit = cassette.unit
            organs_subject = cassette.organs.all()
        else:
            unit = Unit.objects.get(pk=item["unit"])
            organs_subject = unit.organunit_set.all().values_list("id", flat=True)

        identification = unit.identification
        case = identification.entryform
        organ_unit = unit.organunit_set.all().values_list("id", flat=True)
        sample_exams = (
            SampleExams.objects.filter(
                unit_organ__in=organ_unit, organ__in=organs_subject
            )
            .values("stain_id")
            .annotate(stain_count=Count("stain_id"))
            .order_by("stain_id")
        )

        if prev_case != case:
            slide_correlative = cassette.correlative if cassette else unit.correlative
            prev_case = case

        for sample_exam in sample_exams:
            stain = Stain.objects.get(pk=sample_exam["stain_id"])
            row = {
                "case": model_to_dict(case, fields=["id", "no_caso"]),
                "identification": model_to_dict(
                    identification,
                    fields=["id", "cage", "group", "extra_features_detail"],
                ),
                "unit": model_to_dict(unit, fields=["id", "correlative"]),
                "stain": model_to_dict(stain, fields=["id", "abbreviation"]),
                "slide": slide_correlative,
            }
            if cassette:
                row["cassette"] = (
                    model_to_dict(cassette, fields=["id", "correlative"]),
                )
                row["organs"] = ",".join(
                    [organ.abbreviation for organ in cassette.organs.all()]
                )
            else:
                row["organs"] = ",".join(
                    [organ.abbreviation for organ in unit.organs.all()]
                )

            slides.append(row)
            slide_correlative += 1

    return JsonResponse(slides, safe=False)


class SlideBuild(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Displays list of available :model:`lab.Slide` to build,
        from :model:`lab.Cassettte` where they don't already
        have at least one slide built.

        **Context**
        ``cassettes``
            A list of :model:`lab.Cassette`

        **Template**
        ``lab/slides/build.html``
        """

        units = (
            Unit.objects.filter(
                identification__entryform__entry_format=5,
                identification__entryform__forms__cancelled=0,
                identification__entryform__forms__form_closed=0,
            )
            .distinct()
            .select_related("identification__entryform")
        )
        cassettes = (
            Cassette.objects.filter(slides=None, processed_at__isnull=False)
            .distinct()
            .select_related("unit__identification__entryform")
        )
        stains = Stain.objects.all()

        slides = []

        if units.count() > 0:
            for unit in units:
                slides.append(
                    serializers.serialize(
                        "json",
                        [unit.identification.entryform, unit.identification, unit],
                    )
                )

        if cassettes.count() > 0:
            for cassette in cassettes:
                case = cassette.unit.identification.entryform
                identification = cassette.unit.identification
                unit = cassette.unit
                slides.append(
                    serializers.serialize(
                        "json", [case, identification, unit, cassette]
                    )
                )

        return render(
            request, "slides/build.html", {"slides": slides, "stains": stains}
        )

    @method_decorator(login_required)
    def post(self, request):
        """
        Creates a new Slide storing build_at date and their correlative
        according to their :model:`backend.Unit` and :model:`backend.EntryForm`
        """

        request_input = json.loads(request.body)

        if not "slides" in request_input or not request_input["slides"]:
            return JsonResponse(
                {"status": "ERROR", "message": "slides is empty"}, status=400
            )

        slides = request_input["slides"]

        try:
            build_at = parse(request_input["build_at"])
        except (KeyError, ParserError):
            build_at = datetime.now()

        created = []
        errors = []

        for slide in slides:
            parameters = {}

            if "stain_id" not in slide:
                return JsonResponse(
                    {"status": "ERROR", "message": "Stain not found"},
                    status=400,
                )
            else:
                try:
                    stain = Stain.objects.get(pk=slide["stain_id"])
                except Stain.DoesNotExist:
                    return JsonResponse(
                        {"status": "ERROR", "message": "Stain not found"},
                        status=400,
                    )

            # If not unit is received use the Cassette's unit,
            # if neither Cassette nor Unit is given return error
            if "unit_id" not in slide:
                if "cassette_id" not in slide:
                    return JsonResponse(
                        {"status": "ERROR", "message": "Unit/Cassette not found"},
                        status=400,
                    )
                else:
                    try:
                        cassette = Cassette.objects.get(pk=slide["cassette_id"])
                    except Cassette.DoesNotExist:
                        return JsonResponse(
                            {"status": "ERROR", "message": "Cassette not found"},
                            status=400,
                        )
                    else:
                        unit = cassette.unit
                        parameters["cassette"] = cassette
            else:
                try:
                    unit = Unit.objects.get(pk=slide["unit_id"])
                except Unit.DoesNotExist:
                    if "cassette" not in parameters:
                        return JsonResponse(
                            {"status": "ERROR", "message": "Unit not found"},
                            status=400,
                        )
                    else:
                        unit = cassette.unit

            parameters = {
                "unit": unit,
                "stain": stain,
                "build_at": build_at,
            }

            if "correlative" in slide:
                parameters["correlative"] = slide["correlative"]
            else:
                case = unit.identification.entryform
                units = Unit.objects.filter(Q(identification__entryform=case))
                slides = Slide.objects.filter(unit__in=units)
                parameters["correlative"] = slides.count() + 1

            if (
                "cassette_id" in slide and slide["cassette_id"]
            ) and "cassette" not in parameters:
                try:
                    cassette = Cassette.objects.get(pk=slide["cassette_id"])
                except Cassette.DoesNotExist:
                    return JsonResponse(
                        {"status": "ERROR", "message": "Cassette not found"},
                        status=400,
                    )
                parameters["cassette"] = cassette

            try:
                slide = Slide.objects.create(**parameters)
            except IntegrityError:
                errors.append(parameters)
            else:
                created.append(slide)

        return JsonResponse(
            {"created": serializers.serialize("json", created), "errors": errors},
            safe=False,
        )


@method_decorator(login_required, name="dispatch")
class SlideIndex(ListView):
    """Displays a list of Slides.
    Render a template list with all Slides including access to edit and reprocess
    buttons.

        **Context**
        ``slides``
            A list of :model:`lab.Slide`

        **Template**
        ``lab/slides/index.html``

    """

    template_name = "slides/index.html"
    context_object_name = "slides"

    def get_queryset(self):
        slide_range = self.request.GET.get("range")
        now = datetime.now()

        time_delta = timedelta(days=7)
        if slide_range == "2":
            time_delta = timedelta(days=30)
        elif slide_range == "3":
            time_delta = timedelta(days=90)
        elif slide_range == "4":
            time_delta = timedelta(days=180)

        date_range = now - time_delta

        slides = Slide.objects.filter(
            created_at__gte=date_range,
            unit__identification__entryform__forms__cancelled=0,
            unit__identification__entryform__forms__form_closed=0,
        ).select_related("unit__identification__entryform")

        return slides


class SlideDetail(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Returns a JSON detailing Slide.

        **CONTEXT**

        ``slide``
            Detailed data for the requested :model:`lab.Slide`
        ``organs``
            List of :model:`backend.Organ` that belongs to requested Slide.

        """
        slide = get_object_or_404(Slide, pk=kwargs["pk"])

        return HttpResponse(
            serializers.serialize("json", [slide]), content_type="application/json"
        )

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Updates a Slide.
        Returns serialized data of the updated Slide.

        **REQUEST**

            ``build_at``
                Updated build_at date. Optional.
            ``correlative``
                Updated correlative. Optional.
            ``stain``
                Related :model:`backend.Stain`.

        """
        slide = get_object_or_404(Slide, pk=kwargs["pk"])

        request_input = json.loads(request.body)

        if "build_at" in request_input:
            try:
                build_at = parse(request_input["build_at"])
            except (ParserError):
                build_at = slide.build_at
            else:
                slide.build_at = build_at
        if "correlative" in request_input:
            slide.correlative = request_input["correlative"]
        if "stain_id" in request_input:
            slide.stain_id = request_input["stain_id"]

        try:
            slide.save()
        except IntegrityError:
            return JsonResponse(
                {"status": "ERROR", "message": "Couldn't save Slide"}, status=400
            )

        return HttpResponse(
            serializers.serialize("json", [slide]), content_type="application/json"
        )


# Process related views


class ProcessList(View):
    def get(self, request):
        processes = Process.objects.all()
        return render(request, "process/index.html", {"processes": processes})
