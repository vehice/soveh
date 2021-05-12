from django.shortcuts import render

from review.models import Analysis
from django.http.response import JsonResponse
from django.core import serializers


def index(request):
    return render(request, "index.html")


def list(request, index):
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

    if index in (0, 1, 2, 3):
        analysis = Analysis.objects.stage(index)
    else:
        analysis = Analysis.objects.pre_report_done()

    return JsonResponse(serialize_data(analysis), safe=False)
