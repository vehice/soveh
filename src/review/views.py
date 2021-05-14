from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render

from review.models import Analysis, Stage
import json


@login_required
def index(request):
    """
    Renders template which lists multiple :model:`review.Analysis` grouped by
    their state, allowing the user to move them accross multiple states as necessary.
    """
    return render(request, "index.html")


@login_required
def list(request, index):
    """
    Returns a JSON detailing all :model:`review.Analysis` where their :model:`review.Stage`
    state has the current index.
    """
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

    if index in (1, 2, 3, 4):
        analysis = Analysis.objects.stage(index)
    else:
        analysis = Analysis.objects.waiting()

    return JsonResponse(serialize_data(analysis), safe=False)


@login_required
def update_stage(request, pk):
    """
    Updates a :model:`review.Stage`, storing the change in :model:`review.Logbook`.
    """
    analysis = get_object_or_404(Analysis, pk=pk)
    post = json.loads(request.body)
    state = post["state"]

    stage = Stage.objects.update_or_create(
        analysis=analysis, defaults={"state": state, "created_by": request.user}
    )

    return JsonResponse(serializers.serialize("json", [stage[0]]), safe=False)


@login_required
def get_files(request, pk):
    """
    Returns a list of files that belong to a single :model:`review.Analysis`
    """
    analysis = get_object_or_404(Analysis, pk=pk)
    files = analysis.external_reports.all()

    return JsonResponse(serializers.serialize("json", files), safe=False)
