from lab.models import Case, CassetteOrgan, UnitDifference
from django.db.models import Count
from workflows.models import Form
from django.shortcuts import get_object_or_404


def generate_differences(unit):
    """
    Creates :model:`lab.CassetteDifference` for any
    :model:`backend.Organ` that it's present in a Unit
    but not in any of its :model:`lab.Cassette`.
    """
    cassettes_pk = unit.cassettes.all().values_list("id", flat=True)
    cassettes_organs = (
        CassetteOrgan.objects.filter(cassette_id__in=cassettes_pk)
        .values("organ")
        .annotate(organ_count=Count("organ"))
        .order_by()
    )
    unit_organs = (
        unit.organunit_set.values("organ")
        .annotate(organ_count=Count("organ"))
        .order_by()
    )

    differences = []
    for unit_organ in unit_organs:
        for cassette_organ in cassettes_organs:
            if cassette_organ["organ"] == unit_organ["organ"]:
                if cassette_organ["organ_count"] == unit_organ["organ_count"]:
                    continue
                else:
                    difference = (
                        unit_organ["organ_count"] - cassette_organ["organ_count"]
                    )
                    obj, created = UnitDifference.objects.update_or_create(
                        unit=unit,
                        organ_id=unit_organ["organ"],
                        defaults={"difference": difference},
                    )
                    differences.append(obj)

    return differences


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
