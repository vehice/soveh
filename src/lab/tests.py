import json
import datetime

from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from lab.models import Case, Cassette


class CassetteBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.client.login(username="jmonagas", password="vehice1234")
        cls.fake = Faker()

    # CassetteBuildView GET
    def test_shows_correct_units(self):
        """
        Whereas correct Units are those that it's entry type are Cassette, or Fish, and
        that it doesn't have any Cassette.
        """

        response = self.client.get(reverse("lab:cassette_build"))
        self.assertIn(
            "units", response.context, "Response context should contain units."
        )
        units = response.context["units"]
        self.assertFalse(
            units.filter(entry_format__in=[3, 4, 5]).exists(),
            "Units shouldn't contain entry types `3`, `4`, or `5`.",
        )

    def test_returns_json_when_ajax(self):
        response = self.client.get(
            reverse("lab:cassette_build"), None, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        units = json.loads(response.json())

        self.assertTemplateNotUsed(
            response,
            "cassette/process.html",
            "Response should not use template.",
        )

        self.assertGreaterEqual(
            len(units), 0, "Response should contain JSON unit list when ajax"
        )

    def test_returns_template(self):
        response = self.client.get(reverse("lab:cassette_build"))

        self.assertTemplateUsed(
            response,
            "cassettes/build.html",
            "Response should use the defined template.",
        )

    # CassetteBuildView POST
    def test_create_with_data(self):
        build_date = self.fake.date_time()
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": build_date,
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
                    ]
                ),
            },
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
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
                    ]
                ),
            },
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

        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": "not a datetime",
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
                    ]
                ),
            },
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
        build_date = self.fake.date_time()
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": build_date,
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": None, "organs": [49]},
                        {"id": 3, "organs": [49, 51]},
                    ]
                ),
            },
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
        response = self.client.post(
            reverse("lab:cassette_build"),
            {},
        )

        self.assertEquals(
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
        )

    def test_unit_not_found_error(self):
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": self.fake.date_time(),
                "units": json.dumps(
                    [
                        {"id": 999999, "correlative": 1, "organs": [49, 50, 51]},
                    ]
                ),
            },
        )

        self.assertEquals(
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
        )

    def test_organ_not_found_error(self):
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": self.fake.date_time(),
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [9999999]},
                    ]
                ),
            },
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


class CassetteProcessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.client.login(username="jmonagas", password="vehice1234")
        cls.fake = Faker()

        build_date = cls.fake.date_time()
        response = cls.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": build_date,
                "units": json.dumps(
                    [
                        {"id": 1, "correlative": 1, "organs": [49, 50, 51]},
                        {"id": 1, "correlative": 2, "organs": [49, 50, 51]},
                        {"id": 2, "correlative": 1, "organs": [49]},
                        {"id": 3, "correlative": 1, "organs": [49, 51]},
                    ]
                ),
            },
        )

        cls.cassettes = Cassette.objects.all()
        cls.cassettes[0].process_at = datetime.datetime.now()
        cls.cassettes[0].save()

    # CassetteProcessView GET
    def test_shows_correct_cassettes(self):
        response = self.client.get(reverse("lab:cassette_process"))

        cassettes = response.context["cassettes"]

        self.assertEqual(
            self.cassettes[1:],
            cassettes,
            "Response context should contain expected Cassettes",
        )

    def test_returns_json_when_ajax(self):
        response = self.client.get(
            reverse("lab:cassette_build"), None, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        cassettes = json.loads(response.json())

        self.assertTemplateNotUsed(
            response,
            "cassette/process.html",
            "Response should not use template.",
        )

        self.assertGreaterEqual(
            0, len(cassettes), "Response should contain a JSON with cassette list."
        )
        self.assertEqual(
            self.cassettes[1:],
            cassettes,
            "Response should contain expected Cassettes.",
        )

    def test_returns_expected_template(self):
        response = self.client.get(reverse("lab:cassette_process"))

        self.assertTemplateUsed(
            response, "cassette/process.html", "Response should use expected template."
        )

    # CassetteProcessView POST
    def test_updates_with_data(self):
        process_date = datetime.datetime.now()
        response = self.client.post(
            reverse("lab:cassette_process"),
            {"process_date": process_date, "cassettes": self.cassettes[1:]},
        )

        cassettes = json.loads(response.json())

        for cassette in cassettes:
            self.assertEqual(
                process_date.strftime("%Y-%m-%dT%H:%M:%S"),
                cassette["fields"]["process_at"],
                "All Cassettes must have the same process_date as expected.",
            )

    def test_updates_with_default(self):
        process_date = datetime.datetime.now()
        response = self.client.post(
            reverse("lab:cassette_process"),
            {"cassettes": self.cassettes[1:]},
        )

        cassettes = json.loads(response.json())

        for cassette in cassettes:
            self.assertEqual(
                process_date.strftime("%Y-%m-%dT%H:%M:%S"),
                cassette["fields"]["process_at"],
                "All Cassettes must have the same process_date as expected.",
            )

        response = self.client.post(
            reverse("lab:cassette_process"),
            {"process_date": "not a date", "cassettes": self.cassettes[1:]},
        )

        cassettes = json.loads(response.json())

        for cassette in cassettes:
            self.assertEqual(
                datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                cassette["fields"]["process_at"],
                "All Cassettes must have the same process_date as expected.",
            )

    def test_no_data_error(self):
        response = self.client.post(
            reverse("lab:cassette_process"),
            {},
        )

        self.assertEquals(
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
        )

    def test_cassette_not_found_error(self):
        response = self.client.post(
            reverse("lab:cassette_process"),
            {
                "process_at": self.fake.date_time(),
                "cassettes": json.dumps([999999]),
            },
        )

        self.assertEquals(
            400, response.status_code, "Response status code should be as expected."
        )
        self.assertDictContainsSubset(
            {"status": "ERROR"}, response.json(), "Response JSON should be as expected."
        )
