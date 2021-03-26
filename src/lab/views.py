import json
from datetime import datetime

from dateutil.parser import parse
from dateutil.parser import ParserError
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
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
        """

        units = Case.objects.units(entry_format__in=[1, 2, 6, 7])

        if request.is_ajax():
            data = serializers.serialize("json", units)

            return JsonResponse(data, safe=False)

        return render(request, "cassettes/build.html", {"units": units})

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
    pass
