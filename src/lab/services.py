from lab.models import Case, CassetteOrgan, UnitDifference
from django.db.models import Count
from workflows.models import Form
from django.shortcuts import get_object_or_404


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

    if cassettes_organs != unit_organs:
        organ_differences = [
            organ
            for organ in cassettes_organs + unit_organs
            if organ not in cassettes_organs or organ not in unit_organs
        ]

        for difference in organ_differences:
            UnitDifference.objects.update_or_create(
                unit=unit,
                organ_id=difference["organ"],
                defaults={"difference": difference["organ_count"]},
            )

        return True

    return False


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
