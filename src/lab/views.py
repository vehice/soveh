from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.vary import vary_on_headers
from django.views.generic.detail import SingleObjectMixin

from lab.models import Case


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
        pass


class CassetteProcessView(View):
    pass
