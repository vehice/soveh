from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from lab.models import Case


class CassetteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.client.login(username="jmonagas", password="vehice1234")
        cls.fake = Faker()

    def test_build_list_shows_correct_units(self):
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

    def test_build_list_returns_json_when_ajax(self):
        response = self.client.get(
            reverse("lab:cassette_build"), None, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertTrue(response.json(), "Response should contain a json.")

    def test_build_list_returns_template(self):
        response = self.client.get(reverse("lab:cassette_build"))

        self.assertTemplateUsed(
            response,
            "cassettes/build.html",
            "Response should use the defined template.",
        )

    def test_build_post_creates_cassette_with_defaults(self):
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": self.fake.date_time(),
                "units": [1, 2, 3],
            },
        )

        self.assertContains(response.json(), "units")

    def test_build_post_creates_cassette_with_data(self):
        response = self.client.post(
            reverse("lab:cassette_build"),
            {
                "build_at": self.fake.date_time(),
                "units": [
                    {"id": 1, "correlative": 1, "organs": [1, 2, 3]},
                    {"id": 1, "correlative": 2, "organs": [1, 2, 3]},
                    {"id": 2, "correlative": 1, "organs": [3]},
                    {"id": 3, "correlative": 1, "organs": [1, 3]},
                ],
            },
        )

        self.assertContains(response.json(), "units")
