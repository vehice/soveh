import json
from datetime import datetime

from dateutil.parser import ParserError, parse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import InvalidPage, Paginator
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView

from backend.models import Organ, Stain, Unit
from lab.models import Case, Cassette, CassetteOrgan, Process, ProcessUnit, Slide


def home(request):
    cases = Case.objects.all()
    cassette_cases = Case.objects.units(
        kwargs_filter={"entry_format__in": [1, 2, 6, 7]}
    )
    slide_cases = Case.objects.units(kwargs_filter={"entry_format__in": [5]})
    slide_cassettes = Cassette.objects.filter(slides__isnull=True)

    cassettes = []
    slides = []
    for case in cassette_cases:
        identifications = case.identifications
        units_count = Unit.objects.filter(identification__in=identifications).count()
        cassettes.append({"case": case, "count": units_count})

    for case in slide_cases:
        identifications = case.identifications
        units_count = Unit.objects.filter(identification__in=identifications).count()
        slides.append({"case": case, "count": units_count})

    for case in slide_cassettes:
        slides.append({"case": case, "count": units_count})

    context = {"cassettes": cassettes, "slides": slides, "cases": cases}
    return render(request, "home.html", context)


# TODO obtain details from the current lab progress of any Case by their pk
def home_detail(request, pk):
    case = get_object_or_404(Case, id=pk)

    data = serializers.serialize("json", [case])

    return JsonResponse(data, safe=False)


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


# Cassette related views


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

        query_filter = {"entry_format__in": [1, 2, 6, 7]}
        unit_filter = {"cassettes": None}
        cases = Case.objects.units(kwargs_filter=query_filter, kwargs_units=unit_filter)

        organs = serializers.serialize("json", Organ.objects.all())

        return render(
            request, "cassettes/build.html", {"cases": cases, "organs": organs}
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
                correlative = unit.cassettes.count() + 1
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

        return JsonResponse(
            {"created": serializers.serialize("json", created), "errors": errors},
            safe=False,
            status=201,
        )


@login_required
def cassette_prebuild(request):
    """
    Receives a JSON with 2 keys: `selected` which is an array of unit ids;
    and `rules` which is in itself another object that dictates how the cassettes are build,

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
            "identification": unit.identification.cage,
            "unit": unit.correlative,
            "unit_id": unit.id,
            "cassette": count,
            "organs": serializers.serialize("json", unit.organs.all()),
            "cassette_organs": serializers.serialize("json", organs),
        }

    for unit in units:
        cassette_count = unit.cassettes.count()
        cassette_count = 1 if cassette_count == 0 else cassette_count
        excludes = []

        if len(rules["uniques"]) > 0:
            organs = unit.organs.filter(pk__in=rules["uniques"])

            if not organs.count() <= 0:
                for organ in organs:
                    response.append(response_format(unit, [organ], cassette_count))
                    cassette_count += 1

                excludes.extend([pk for pk in rules["uniques"]])

        if len(rules["groups"]) > 0:
            for group in rules["groups"]:
                organs = unit.organs.filter(pk__in=group).exclude(pk__in=excludes)

                if not organs.count() <= 0:
                    response.append(response_format(unit, organs, cassette_count))
                    cassette_count += 1
                    excludes.extend([pk for pk in group])

        organs = unit.organs.exclude(pk__in=excludes).order_by("-id")

        if rules["max"] > 0:
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

    queryset = Cassette.objects.all().prefetch_related("organs")
    template_name = "cassettes/index.html"
    context_object_name = "cassettes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cases"] = Case.objects.units
        return context


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
        cassettes = Cassette.objects.all().select_related(
            "unit__identification__entryform"
        )
        return render(request, "cassettes/process.html", {"cassettes": cassettes})


# Slide related views


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

        query_filter = {"entry_format__in": [5]}
        cases = Case.objects.units(kwargs_filter=query_filter)
        cassettes = Cassette.objects.filter(slides=None).select_related(
            "unit__identification__entryform"
        )
        stains = Stain.objects.all()

        slides = []

        if cases.count() > 0:
            for case in cases:
                for identification in case.identifications:
                    for unit in identification.units:
                        slides.append(
                            serializers.serialize("json", [case, identification, unit])
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

    queryset = Slide.objects.all().select_related(
        "cassette__unit__identification__entryform"
    )
    template_name = "slides/index.html"
    context_object_name = "slides"

    def get_context_data(self, *, object_list=None, **kwargs):
        query_filter = {"entry_format__in": [5]}
        cases = Case.objects.units()
        cassettes = Cassette.objects.all().select_related(
            "unit__identification__entryform"
        )

        context = super().get_context_data(**kwargs)
        context["cases"] = cases
        context["cassettes"] = cassettes

        return context


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


class ProcessTreeView(View):
    def get(self, request, pk):
        """Displays a tree view of all processes for a :model:`lab.Case`"""
        case = get_object_or_404(Case, pk=pk)
        processes = Process.objects.filter(deleted_at__isnull=True)

        return render(
            request, "process/tree.html", {"case": case, "processes": processes}
        )
