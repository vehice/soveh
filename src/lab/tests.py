import datetime
import json

from django.test import Client, TestCase
from django.urls import reverse

from backend.models import Identification, Organ, OrganUnit, Unit
from lab.models import Case, Cassette, CassetteOrgan, Slide


class VariantTest(TestCase):
    """Includes test that don't fit into any particular class"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_organ_list_no_id(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:organ_index"))

        self.assertEquals(Organ.objects.all().count(), len(response.json()))


class HomeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_home_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:home"))

        self.assertTemplateUsed(
            response, "home.html", "Response must use expected template."
        )

    def test_home_context(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:home"))

        self.assertIn(
            "cassettes",
            response.context,
            "Response context must contain expected data.",
        )

        self.assertIn(
            "cases",
            response.context,
            "Response context must contain expected data.",
        )

    def test_home_detail(self):
        self.client.login(username="jmonagas", password="vehice1234")
        case = Case.objects.all().last()
        response = self.client.get(reverse("lab:home_detail", kwargs={"pk": case.id}))

        self.assertTrue(
            response.json(),
            "Response context must contain expected data.",
        )


class CaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_detail_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        case = Case.objects.all().last()
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": case.id}))

        self.assertTemplateUsed(
            response, "cases/detail.html", "Response must use expected template."
        )

    def test_detail_returns_case(self):
        self.client.login(username="jmonagas", password="vehice1234")
        case = Case.objects.all().last()
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": case.id}))

        self.assertTrue(
            response.context["case"].id == case.id,
            "Response must return expected Case.",
        )

    def test_generate_read_page(self):
        self.client.login(username="jmonagas", password="vehice1234")
        case = Case.objects.all().last()
        response = self.client.get(
            reverse("lab:case_read_sheet", kwargs={"pk": case.id})
        )

        self.assertTemplateUsed(
            response, "cases/read_sheet.html", "Response should use expected template."
        )
        self.assertContains(response, case.no_caso)


class CassetteBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.cases = Case.objects.bulk_create(
            [
                Case(entry_format=1),
                Case(entry_format=2),
                Case(entry_format=3),
                Case(entry_format=4),
                Case(entry_format=5),
            ]
        )
        cls.identifications = []

        for case in cls.cases:
            cls.identifications.append(Identification.objects.create())

        cls.units = []

        for identification in cls.identifications:
            cls.units.append(Unit.objects.create())

    # CassetteBuildView GET
    def test_shows_correct_units(self):
        """
        Whereas correct Units are those that it's entry type are Cassette, or Fish, and
        that it doesn't have any Cassette.
        """

        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_build"))
        self.assertIn("cases", response.context, "Response context must contain Cases.")
        units = response.context["cases"]
        self.assertFalse(
            units.filter(entry_format__in=[3, 4, 5]).exists(),
            "Cases mustn't contain entry types `3`, `4`, or `5`.",
        )

    def test_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_build"))

        self.assertTemplateUsed(
            response,
            "cassettes/build.html",
            "Response must use the defined template.",
        )

    # CassetteBuildView POST
    def test_create_with_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        build_date = datetime.datetime.now()
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": build_date.isoformat(),
                    "units": [
                        {
                            "id": self.units[0].id,
                            "correlative": 1,
                            "organs": [49, 50, 51],
                        },
                        {
                            "id": self.units[0].id,
                            "correlative": 2,
                            "organs": [49, 50, 51],
                        },
                        {"id": self.units[1].id, "correlative": 1, "organs": [49]},
                        {"id": self.units[2].id, "correlative": 1, "organs": [49, 51]},
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(response.json(), "Response must return a json.")

        cassettes = json.loads(response.json()["created"])

        for cassette in cassettes:
            self.assertGreaterEqual(cassette["pk"], 1, "All Cassettes must have a PK.")
            self.assertEqual(
                build_date.strftime("%Y-%m-%dT%H:%M:%S"),
                cassette["fields"]["build_at"][:-4],
                "All Cassettes must have the same build_date as expected.",
            )

    def test_create_with_default_date(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "units": [
                        {
                            "id": self.units[0].id,
                            "correlative": 1,
                            "organs": [49, 50, 51],
                        },
                        {
                            "id": self.units[0].id,
                            "correlative": 2,
                            "organs": [49, 50, 51],
                        },
                        {"id": self.units[1].id, "correlative": 1, "organs": [49]},
                        {"id": self.units[2].id, "correlative": 1, "organs": [49, 51]},
                    ]
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(response.json(), "Response must return a json.")

        cassettes = json.loads(response.json()["created"])

        for cassette in cassettes:
            self.assertGreaterEqual(cassette["pk"], 1, "All Cassettes must have a PK.")
            self.assertEqual(
                datetime.datetime.now().isoformat(timespec="minutes"),
                cassette["fields"]["build_at"][:-7],
                "All Cassettes must have the same build_date as expected.",
            )

        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": "not a datetime",
                    "units": [
                        {
                            "id": self.units[0].id,
                            "correlative": 1,
                            "organs": [49, 50, 51],
                        },
                        {
                            "id": self.units[0].id,
                            "correlative": 2,
                            "organs": [49, 50, 51],
                        },
                        {"id": self.units[1].id, "correlative": 1, "organs": [49]},
                        {"id": self.units[2].id, "correlative": 1, "organs": [49, 51]},
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(response.json(), "Response must return a json.")

        cassettes = json.loads(response.json()["created"])

        for cassette in cassettes:
            self.assertGreaterEqual(cassette["pk"], 1, "All Cassettes must have a PK.")
            self.assertEqual(
                datetime.datetime.now().isoformat(timespec="seconds"),
                cassette["fields"]["build_at"][:-4],
                "All Cassettes must have the same build_date as expected.",
            )

    def test_create_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")
        build_date = datetime.datetime.now()
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": build_date.isoformat(),
                    "units": [
                        {
                            "id": self.units[0].id,
                            "correlative": 1,
                            "organs": [49, 50, 51],
                        },
                        {"id": self.units[0].id, "organs": [49, 50, 51]},
                        {"id": self.units[1].id, "correlative": None, "organs": [49]},
                        {"id": self.units[2].id, "organs": [49, 51]},
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(response.json(), "Response must return a json.")

        cassettes = json.loads(response.json()["created"])

        for cassette in cassettes:
            self.assertGreaterEqual(cassette["pk"], 1, "All Cassettes must have a PK.")
            self.assertEqual(
                build_date.strftime("%Y-%m-%dT%H:%M:%S"),
                cassette["fields"]["build_at"][:-4],
                "All Cassettes must have the same build_date as expected.",
            )
            self.assertGreaterEqual(
                cassette["fields"]["correlative"],
                0,
                "All Cassettes must have a correlative greater than 0.",
            )

    def test_no_data_error(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:cassette_build"), {}, content_type="application/json"
        )

        self.assertEquals(
            400, response.status_code, "Response status code must be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON must be as expected."
        )

    def test_unit_not_found_error(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "units": [
                        {"id": 999999, "correlative": 1, "organs": [49, 50, 51]},
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertEquals(
            400, response.status_code, "Response status code must be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON must be as expected."
        )

    def test_organ_not_found_error(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "units": [
                        {"id": self.units[0].id, "correlative": 1, "organs": [9999999]},
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertEquals(
            201, response.status_code, "Response status code must be as expected."
        )
        self.assertDictContainsSubset(
            {
                "errors": [
                    {
                        "status": "ERROR",
                        "message": "Organ id 9999999 does not exists",
                    }
                ]
            },
            response.json(),
            "Response JSON must be as expected.",
        )


class CassettePrebuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.cases = []
        for entry in range(1, 5):
            case = Case.objects.create(entry_format=entry, no_caso=f"V000{entry}")
            cls.cases.append(case)

        cls.identifications = []

        for case in cls.cases:
            identification = Identification.objects.create(entryform=case)
            cls.identifications.append(identification)

        cls.units = []

        for identification in cls.identifications:
            unit = Unit.objects.create(identification=identification)
            cls.units.append(unit)

            for organ in Organ.objects.filter(id__gt=46):
                OrganUnit.objects.create(unit=unit, organ=organ)

    def test_no_rules(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [], "max": 0},
                }
            ),
        )

        self.assertGreaterEqual(
            len(response.json()),
            2,
            "Response must contain as many items as units given.",
        )

        self.assertDictContainsSubset(
            {"unit_id": self.units[0].id},
            response.json()[0],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"unit_id": self.units[1].id},
            response.json()[1],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"cassette": 1},
            response.json()[0],
            "Response must contain expected data.",
        )

    def test_rule_unique(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [59], "groups": [], "max": 0},
                }
            ),
        )

        self.assertEquals(
            59,
            json.loads(response.json()[0]["cassette_organs"])[0].get("pk"),
            "Response must contain expected data.",
        )

    def test_rule_groups(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [[59, 57], [58, 56]], "max": 0},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

    def test_rule_max(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [], "max": 2},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

    def test_rule_all(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [55], "groups": [[56, 57]], "max": 2},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            1,
            "Response must contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[1]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[2]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )


class CassetteIndexTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_expected_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_index"))

        self.assertTemplateUsed(
            response, "cassettes/index.html", "Response must use expected template."
        )

    def test_expected_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_index"))
        cassette = Cassette.objects.all()

        self.assertEqual(
            len(cassette),
            len(response.context["object_list"]),
            "Response must contain as many Cassettes as expected.",
        )


class CassetteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.case = Case.objects.create()
        cls.identification = Identification.objects.create(entryform=cls.case)
        cls.unit = Unit.objects.create(identification=cls.identification)
        cls.cassette = Cassette.objects.create(unit=cls.unit, correlative=1)

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(
            reverse("lab:cassette_detail", kwargs={"pk": self.cassette.id})
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_cassette(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": self.cassette.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "correlative": 1,
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_no_build_at(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": self.cassette.id}),
            json.dumps(
                {
                    "correlative": 1,
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": self.cassette.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_no_organs(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": self.cassette.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "correlative": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )


class CassetteProcessedAtTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.case = Case.objects.create()
        cls.identification = Identification.objects.create(entryform=cls.case)
        cls.unit = Unit.objects.create(identification=cls.identification)
        cls.cassette = Cassette.objects.create(unit=cls.unit, correlative=1)

    def test_expected_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_process"))

        self.assertTemplateUsed(
            response, "cassettes/process.html", "Response must use expected template."
        )

        cassettes = Cassette.objects.all()

        self.assertTrue(
            response.context["cassettes"].first() == cassettes.first(),
            "Response must contain expected context.",
        )


class SlideBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.case = Case.objects.create()
        cls.identification = Identification.objects.create(entryform=cls.case)
        cls.unit = Unit.objects.create(identification=cls.identification)
        cls.cassette = Cassette.objects.create(unit=cls.unit, correlative=1)

    # SlideBuild GET
    def test_context_includes_slides(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:slide_build"))

        self.assertIn("slides", response.context, "Context must contain Slides.")

    def test_context_includes_stains(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:slide_build"))

        self.assertIn("stains", response.context, "Context must contain Slides.")

    def test_shows_expected_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:slide_build"))

        self.assertTemplateUsed(
            response, "slides/build.html", "Response must contain expected template."
        )

    # SlideBuild POST
    def test_stores_slides_with_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 2,
                        },
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

    def test_stores_slides_with_no_cassette(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {"unit_id": self.unit.id, "stain_id": 1, "correlative": 1},
                        {"unit_id": self.unit.id, "stain_id": 1, "correlative": 2},
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

    def test_stores_slides_with_no_unit(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "stain_id": 1,
                            "correlative": 2,
                        },
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

    def test_stores_slides_with_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                        },
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

    def test_stores_slides_with_default_date(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 2,
                        },
                    ],
                    "build_at": "",
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )
        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 2,
                        },
                    ],
                    "build_at": "Not a date",
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": self.cassette.id,
                            "unit_id": self.unit.id,
                            "stain_id": 1,
                            "correlative": 2,
                        },
                    ],
                }
            ),
            content_type="application/json",
        )

        self.assertIn(
            "created", response.json(), "Response must contain created Slide."
        )

        self.assertGreaterEqual(
            len(response.json()["created"]),
            2,
            "Response must contain as many created as send.",
        )

    def test_stores_error_when_no_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps({}),
            content_type="application/json",
        )

        self.assertIn("status", response.json(), "Response must contain expected item.")

    def test_stores_error_when_cassette_not_found(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": 9999999,
                            "unit_id": 7,
                            "stain_id": 1,
                            "correlative": 1,
                        }
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn("status", response.json(), "Response must contain expected item.")

    def test_stores_error_when_stain_not_found(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:slide_build"),
            json.dumps(
                {
                    "slides": [
                        {
                            "cassette_id": 1,
                            "unit_id": 7,
                            "stain_id": 999999,
                            "correlative": 1,
                        }
                    ],
                    "build_at": datetime.datetime.now().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn("status", response.json(), "Response must contain expected item.")


class CassettePrebuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.cases = []
        for entry in range(1, 5):
            case = Case.objects.create(entry_format=entry, no_caso=f"V000{entry}")
            cls.cases.append(case)

        cls.identifications = []

        for case in cls.cases:
            identification = Identification.objects.create(entryform=case)
            cls.identifications.append(identification)

        cls.units = []

        for identification in cls.identifications:
            unit = Unit.objects.create(identification=identification)
            cls.units.append(unit)

            for organ in Organ.objects.filter(id__gt=46):
                OrganUnit.objects.create(unit=unit, organ=organ)

    def test_no_rules(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [], "max": 0},
                }
            ),
        )

        self.assertGreaterEqual(
            len(response.json()),
            2,
            "Response must contain as many items as units given.",
        )

        self.assertDictContainsSubset(
            {"unit_id": self.units[0].id},
            response.json()[0],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"unit_id": self.units[1].id},
            response.json()[1],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"cassette": 1},
            response.json()[0],
            "Response must contain expected data.",
        )

    def test_rule_unique(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [59], "groups": [], "max": 0},
                }
            ),
        )

        self.assertEquals(
            59,
            json.loads(response.json()[0]["cassette_organs"])[0].get("pk"),
            "Response must contain expected data.",
        )

    def test_rule_groups(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [[59, 57], [58, 56]], "max": 0},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

    def test_rule_max(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [], "groups": [], "max": 2},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

    def test_rule_all(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [self.units[0].id, self.units[1].id],
                    "rules": {"uniques": [55], "groups": [[56, 57]], "max": 2},
                }
            ),
        )

        self.assertEquals(
            len(json.loads(response.json()[0]["cassette_organs"])),
            1,
            "Response must contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[1]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[2]["cassette_organs"])),
            2,
            "Response must contain expected data.",
        )


class SlideIndexTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_expected_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:slide_index"))

        self.assertTemplateUsed(
            response, "slides/index.html", "Response must use expected template."
        )

    def test_expected_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:slide_index"))
        slides = Slide.objects.all()

        self.assertEqual(
            len(slides),
            len(response.context["object_list"]),
            "Response must contain as many Slide as expected.",
        )


class SlideDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.client = Client()
        cls.case = Case.objects.create()
        cls.identification = Identification.objects.create(entryform=cls.case)
        cls.unit = Unit.objects.create(identification=cls.identification)
        cls.cassette = Cassette.objects.create(unit=cls.unit, correlative=1)
        cls.slide = Slide.objects.create(
            cassette=cls.cassette, unit=cls.unit, stain_id=1, correlative=1
        )

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(
            reverse("lab:slide_detail", kwargs={"pk": self.slide.id})
        )

        self.assertTrue(
            response.json()[0]["pk"] == self.slide.id,
            "Response should contain expected Slide.",
        )

    def test_detail_updates_slide(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": self.slide.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "correlative": 1,
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == self.slide.id,
            "Response should contain expected Slide.",
        )

    def test_detail_updates_no_build_at(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": self.slide.id}),
            json.dumps(
                {
                    "correlative": 2,
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == self.slide.id,
            "Response should contain expected Slide.",
        )

    def test_detail_updates_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": self.slide.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == self.slide.id,
            "Response should contain expected Slide.",
        )

    def test_detail_no_stain(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": self.slide.id}),
            json.dumps(
                {
                    "build_at": datetime.datetime.now().isoformat(),
                    "correlative": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == self.slide.id,
            "Response should contain expected Slide.",
        )


class SlidePrebuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.cases = []
        for entry in range(1, 5):
            case = Case.objects.create(entry_format=entry, no_caso=f"V000{entry}")
            cls.cases.append(case)

        cls.identifications = []

        for case in cls.cases:
            identification = Identification.objects.create(entryform=case)
            cls.identifications.append(identification)

        cls.units = []

        for identification in cls.identifications:
            unit = Unit.objects.create(identification=identification)
            cls.units.append(unit)

            for organ in Organ.objects.filter(id__gt=46):
                OrganUnit.objects.create(unit=unit, organ=organ)

        count = 0
        cls.cassettes = []
        for unit in cls.units:
            count += 1
            cassette = Cassette.objects.create(unit=unit, correlative=count)

            cls.cassettes.append(cassette)

            for organ in unit.organs.all():
                CassetteOrgan.objects.create(cassette=cassette, organ=organ)

    def test_no_rules(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "POST",
            reverse("lab:slide_prebuild"),
            json.dumps([self.cassettes[0].id]),
        )

        print(response.json())

        self.assertGreaterEqual(
            len(response.json()),
            1,
            "Response must contain as many items as cassettes given.",
        )

        self.assertDictContainsSubset(
            {"unit_id": self.units[0]["pk"]},
            response.json()[0],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"slide": 1},
            response.json()[0],
            "Response must contain expected data.",
        )
