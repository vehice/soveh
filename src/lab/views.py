import json
from datetime import datetime

from dateutil.parser import ParserError, parse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers
from django.views.generic.detail import SingleObjectMixin

from backend.models import Unit
from lab.models import Case, Cassette


class CassetteDetailView(SingleObjectMixin):
    pass


class CassetteBuildView(View):
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
        ``lab/build.html``
        """

        cases = Case.objects.units(entry_format__in=[1, 2, 6, 7])

        if request.is_ajax():
            return HttpResponse(
                serializers.serialize("json", cases), content_type="application/json"
            )

        return render(request, "cassettes/build.html", {"cases": cases})

    def post(self, request):
        """
        Creates a new Cassette storing build_at date and their correlative
        according to their :model:`backend.Unit` and :model:`backend.EntryForm`
        """

        build_at = request.POST.get("build_at")
        units = request.POST.get("units")

        if not units:
            return JsonResponse(
                {"status": "ERROR", "message": "units is empty"}, status=400
            )
        else:
            units = json.loads(units)

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


class CassetteProcessView(View):
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
    Receives an array of unit ids, and returns an array of `pseudo` Cassettes,
    grouped by :model:`lab.Case` with their own correlatives.
    """
    unit_ids = json.loads(request.body)
    units = Unit.objects.filter(pk__in=unit_ids).order_by("identification__entryform")

    response = []

    for unit in units:
        cassette_count = unit.cassettes.count()
        cassette_count = 1 if cassette_count == 0 else cassette_count
        unit_organs = unit.organs.all()
        response.append(
            {
                "case": unit.identification.entryform.no_caso,
                "identification": unit.identification.cage,
                "unit": unit.correlative,
                "unit_id": unit.id,
                "cassette": cassette_count,
                "organs": serializers.serialize("json", unit_organs),
                "cassette_organs": serializers.serialize("json", unit_organs),
            }
        )

    return HttpResponse(json.dumps(response), content_type="application/json")
