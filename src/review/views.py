from django.core import serializers
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View

from review.models import Analysis


def index(request):
    return render(request, "index.html")


class StageView(View):
    def get(self, request, *args, **kwargs):
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

        if self.kwargs["index"] in (0, 1, 2, 3):
            analysis = Analysis.objects.stage(self.kwargs["index"])
        else:
            analysis = Analysis.objects.pre_report_done()

        return JsonResponse(serialize_data(analysis), safe=False)

    def post(self, request, *args, **kwargs):
        pass
