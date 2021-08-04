from lab.models import CassetteOrgan, UnitDifference
from django.db.models import Count


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
                    differences.append(
                        {
                            "organ": unit_organ["organ"],
                            "difference": difference,
                        }
                    )
                    UnitDifference.objects.create(
                        unit=unit, organ_id=unit_organ["organ"], difference=difference
                    )

    return differences
