import json
import datetime

from django.contrib import auth
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from lab.models import Case, Cassette, Slide
from backend.models import Organ


class VariantTest(TestCase):
    """Includes test that don't fit into any particular class"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_organ_list_no_id(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:organ_index"))

        self.assertEquals(Organ.objects.all().count(), len(response.json()))


class HomeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

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
        response = self.client.get(reverse("lab:home_detail", kwargs={"pk": 973}))

        self.assertTrue(
            response.json(),
            "Response context must contain expected data.",
        )


class CaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_detail_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTemplateUsed(
            response, "cases/detail.html", "Response must use expected template."
        )

    def test_detail_returns_case(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTrue(
            response.context["case"].id == 983, "Response must return expected Case."
        )

    def test_generate_read_page(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_read_sheet", kwargs={"pk": 983}))

        self.assertEquals(response.get("Content-Disposition"), "attachment;")


class CassetteBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

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
        build_date = self.fake.date_time()
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": build_date.isoformat(),
                    "units": [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
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
                cassette["fields"]["build_at"],
                "All Cassettes must have the same build_date as expected.",
            )

    def test_create_with_default_date(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "units": [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
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
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
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
        build_date = self.fake.date_time()
        response = self.client.post(
            reverse("lab:cassette_build"),
            json.dumps(
                {
                    "build_at": build_date.isoformat(),
                    "units": [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": None, "organs": [49]},
                        {"id": 3, "organs": [49, 51]},
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
                cassette["fields"]["build_at"],
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
                    "build_at": self.fake.date_time().isoformat(),
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
                    "build_at": self.fake.date_time().isoformat(),
                    "units": [
                        {"id": 1, "correlative": 1, "organs": [9999999]},
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
        cls.fake = Faker()

    def test_no_rules(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [13, 12],
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
            {"unit_id": 13},
            response.json()[0],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"unit_id": 12},
            response.json()[1],
            "Response must contain expected data.",
        )

        self.assertDictContainsSubset(
            {"cassette": 1},
            response.json()[0],
            "Response must contain expected data.",
        )

        self.assertEqual(
            response.json()[0]["cassette_organs"],
            response.json()[0]["organs"],
            "Response must contain expected data.",
        )

    def test_rule_unique(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.generic(
            "GET",
            reverse("lab:cassette_prebuild"),
            json.dumps(
                {
                    "selected": [2, 12],
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
                    "selected": [2, 12],
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
                    "selected": [2, 12],
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
                    "selected": [2, 12],
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
        cls.fake = Faker()

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
        cls.fake = Faker()

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(reverse("lab:cassette_detail", kwargs={"pk": 1}))

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_cassette(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
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
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "correlative": self.fake.pyint(),
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
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
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
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )


class SlideBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

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
                            "cassette_id": 1,
                            "unit_id": 14,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": 2,
                            "unit_id": 7,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                    ],
                    "build_at": self.fake.date_time().isoformat(),
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
                        {"unit_id": 14, "stain_id": 1, "correlative": 1},
                        {"unit_id": 7, "stain_id": 1, "correlative": 1},
                    ],
                    "build_at": self.fake.date_time().isoformat(),
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
                        {"cassette_id": 1, "stain_id": 1, "correlative": 1},
                        {"cassette_id": 1, "stain_id": 1, "correlative": 1},
                    ],
                    "build_at": self.fake.date_time().isoformat(),
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
                            "cassette_id": 1,
                            "unit_id": 14,
                            "stain_id": 1,
                        },
                        {
                            "cassette_id": 2,
                            "unit_id": 7,
                            "stain_id": 1,
                        },
                    ],
                    "build_at": self.fake.date_time().isoformat(),
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
                            "cassette_id": 1,
                            "unit_id": 14,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": 2,
                            "unit_id": 7,
                            "stain_id": 1,
                            "correlative": 1,
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
                            "cassette_id": 1,
                            "unit_id": 14,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": 2,
                            "unit_id": 7,
                            "stain_id": 1,
                            "correlative": 1,
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
                            "cassette_id": 1,
                            "unit_id": 14,
                            "stain_id": 1,
                            "correlative": 1,
                        },
                        {
                            "cassette_id": 2,
                            "unit_id": 7,
                            "stain_id": 1,
                            "correlative": 1,
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
                    "build_at": self.fake.date_time().isoformat(),
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
                    "build_at": self.fake.date_time().isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn("status", response.json(), "Response must contain expected item.")


class SlideIndexTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

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
        cls.fake = Faker()

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(reverse("lab:slide_detail", kwargs={"pk": 1}))

        self.assertTrue(
            response.json()[0]["pk"] == 1, "Response should contain expected Slide."
        )

    def test_detail_updates_slide(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == 1, "Response should contain expected Slide."
        )

    def test_detail_updates_no_build_at(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "correlative": self.fake.pyint(),
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == 1, "Response should contain expected Slide."
        )

    def test_detail_updates_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "stain_id": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == 1, "Response should contain expected Slide."
        )

    def test_detail_no_stain(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:slide_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
                }
            ),
            content_type="application/json",
        )

        self.assertTrue(
            response.json()[0]["pk"] == 1, "Response should contain expected Slide."
        )
