import json
from datetime import datetime

from dateutil.parser import ParserError, parse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import InvalidPage, Paginator
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers
from django.views.generic.detail import DetailView

from backend.models import Organ, Unit
from lab.models import Case, Cassette


class CaseDetail(DetailView):
    model = Case
    template_name = "cassettes/detail.html"


class CassetteBuild(View):
    @method_decorator(vary_on_headers("X-Requested-With"))
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

        cases = Case.objects.units(entry_format__in=[1, 2, 6, 7])

        organs = serializers.serialize("json", Organ.objects.all())

        if request.is_ajax():
            return HttpResponse(
                serializers.serialize("json", cases), content_type="application/json"
            )

        return render(
            request, "cassettes/build.html", {"cases": cases, "organs": organs}
        )

    def post(self, request):
        """
        Creates a new Cassette storing build_at date and their correlative
        according to their :model:`backend.Unit` and :model:`backend.EntryForm`
        """

        form_request = json.loads(request.body)
        build_at = form_request["build_at"]
        units = form_request["units"]

        if not units:
            return JsonResponse(
                {"status": "ERROR", "message": "units is empty"}, status=400
            )

        if not build_at:
            build_at = datetime.now()
        else:
            try:
                build_at = parse(build_at)
            except ParserError:
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

            for organ in row["organs"]:
                try:
                    cassette.organs.add(organ)
                except IntegrityError:
                    errors.append(
                        {
                            "status": "ERROR",
                            "message": "Organ id %d does not exists" % organ,
                        }
                    )
                else:
                    created.append(cassette)

        return JsonResponse(
            {"created": serializers.serialize("json", created), "errors": errors},
            safe=False,
            status=201,
        )


class CassetteProcess(View):
    @method_decorator(vary_on_headers("X-Requested-With"))
    def get(self, request):
        """
        Displays a list of all :model:`lab.Cassette` that
        do not have a processed_at date set.

        **Context**

        ``cassettes``
            A list of :model:`lab.Cassette`.

        **Template**
            :template:`lab/cassette/process.html`.
        """
        cassettes = Cassette.objects.filter(processed_at__isnull=True)

        if request.is_ajax():
            return JsonResponse(serializers.serialize("json", cassettes), safe=False)

        return render(request, "cassettes/build.html", {"cassettes": cassettes})

    def post(self, request):
        """
        Updates all given :model:`lab.Cassette` with the
        parameter ``process_date``, if no ``process_date`` is
        given then it defaults to current datetime.
        """
        processed_at = request.POST.get("processed_at")
        cassettes = request.POST.get("cassettes")

        if not cassettes:
            return JsonResponse(
                {"status": "ERROR", "message": "cassettes is empty"}, status=400
            )
        else:
            cassettes = json.loads(cassettes)

        if not processed_at:
            processed_at = datetime.now()
        else:
            try:
                processed_at = parse(processed_at)
            except ParserError:
                processed_at = datetime.now()

        updated = Cassette.objects.filter(pk__in=cassettes).update(
            processed_at=processed_at
        )

        return JsonResponse({"status": "DONE", "message": "%d rows updated" % updated})


@csrf_exempt
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
