import json
import datetime

from django.contrib import auth
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from lab.models import Case, Cassette
from backend.models import Organ


class CaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_detail_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTemplateUsed(
            response, "cases/detail.html", "Response should use expected template."
        )

    def test_detail_returns_case(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTrue(
            response.context["case"].id == 983, "Response should return expected Case."
        )


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
        self.assertIn(
            "cases", response.context, "Response context should contain Cases."
        )
        units = response.context["cases"]
        self.assertFalse(
            units.filter(entry_format__in=[3, 4, 5]).exists(),
            "Cases shouldn't contain entry types `3`, `4`, or `5`.",
        )

    def test_returns_json_when_ajax(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(
            reverse("lab:cassette_build"), None, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        units = response.json()

        self.assertTemplateNotUsed(
            response,
            "cassette/process.html",
            "Response should not use template.",
        )

        self.assertGreaterEqual(
            len(units), 0, "Response should contain JSON unit list when ajax"
        )

    def test_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_build"))

        self.assertTemplateUsed(
            response,
            "cassettes/build.html",
            "Response should use the defined template.",
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

        self.assertTrue(response.json(), "Response should return a json.")

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

        self.assertTrue(response.json(), "Response should return a json.")

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

        self.assertTrue(response.json(), "Response should return a json.")

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

        self.assertTrue(response.json(), "Response should return a json.")

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
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
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
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
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
            201, response.status_code, "Response status code should be as expected."
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
            "Response JSON should be as expected.",
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
            "Response should contain as many items as units given.",
        )

        self.assertDictContainsSubset(
            {"unit_id": 13},
            response.json()[0],
            "Response should contain expected data.",
        )

        self.assertDictContainsSubset(
            {"unit_id": 12},
            response.json()[1],
            "Response should contain expected data.",
        )

        self.assertDictContainsSubset(
            {"cassette": 1},
            response.json()[0],
            "Response should contain expected data.",
        )

        self.assertEqual(
            response.json()[0]["cassette_organs"],
            response.json()[0]["organs"],
            "Response should contain expected data.",
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
            "Response should contain expected data.",
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
            "Response should contain expected data.",
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
            "Response should contain expected data.",
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
            "Response should contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[1]["cassette_organs"])),
            2,
            "Response should contain expected data.",
        )

        self.assertEquals(
            len(json.loads(response.json()[2]["cassette_organs"])),
            2,
            "Response should contain expected data.",
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
            response, "cassettes/index.html", "Response should use expected template."
        )

    def test_expected_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_index"))
        cassette = Cassette.objects.all()

        self.assertEqual(
            len(cassette),
            len(response.context["object_list"]),
            "Response should contain as many Cassettes as expected.",
        )


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


class CassetteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(reverse("lab:cassette_detail", kwargs={"pk": 1}))

        self.assertIn("cassette", response.json(), "Response should contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response should contain Cassette's organs."
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

        self.assertIn("cassette", response.json(), "Response should contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response should contain Cassette's organs."
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

        self.assertIn("cassette", response.json(), "Response should contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response should contain Cassette's organs."
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

        self.assertIn("cassette", response.json(), "Response should contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response should contain Cassette's organs."
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

        self.assertIn("cassette", response.json(), "Response should contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response should contain Cassette's organs."
        )
