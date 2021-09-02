from lab.models import Case, CassetteOrgan, UnitDifference
from django.db.models import Count
from workflows.models import Form
from django.shortcuts import get_object_or_404
from collections import defaultdict
from itertools import chain
from operator import methodcaller


def generate_differences(unit):
    """
    Creates :model:`lab.CassetteDifference` for any
    :model:`backend.Organ` that it's present in a Unit
    but not in any of its :model:`lab.Cassette`.
    Returns True if any difference is generated.
    """
    cassettes_pk = unit.cassettes.all().values_list("id", flat=True)
    cassettes_organs = list(
        CassetteOrgan.objects.filter(cassette_id__in=cassettes_pk)
        .values("organ")
        .annotate(organ_count=Count("organ"))
        .order_by()
    )
    unit_organs = list(
        unit.organunit_set.values("organ")
        .annotate(organ_count=Count("organ"))
        .order_by()
    )

    unit_organs = {
        unit_organ["organ"]: [unit_organ["organ_count"]] for unit_organ in unit_organs
    }
    cassettes_organs = {
        cassettes_organ["organ"]: [cassettes_organ["organ_count"]]
        for cassettes_organ in cassettes_organs
    }

    final_organs = defaultdict(list)

    dict_items = map(methodcaller("items"), (unit_organs, cassettes_organs))
    for k, v in chain.from_iterable(dict_items):
        final_organs[k].extend(v)

    has_differences = False
    for organ in final_organs:
        if len(final_organs[organ]) == 1:
            if final_organs[organ][0] > 0 or final_organs[organ][0] < 0:
                UnitDifference.objects.update_or_create(
                    unit=unit,
                    organ_id=organ,
                    defaults={"difference": final_organs[organ][0]},
                )
                has_differences = True
        else:
            difference = final_organs[organ][0] - final_organs[organ][1]
            if difference < 0 or difference > 0:
                UnitDifference.objects.update_or_create(
                    unit=unit,
                    organ_id=organ,
                    defaults={"difference": difference},
                )
                has_differences = True

    return has_differences


def change_case_step(case_pk, step):
    """
    Updates the given :model:`workflow.Form` to the given
    step, regardless of current state.
    """

    case = get_object_or_404(Case, pk=case_pk)
    form = case.forms.first()

    if form.reception_finished and int(step) in (2, 3):
        form.reception_finished = False
        form.reception_finished_at = None
    form.state_id = step
    form.save()

    return (case, form)
