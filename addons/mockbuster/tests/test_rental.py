from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import MockbusterCase


@tagged("post_install", "-at_install", "mockbuster")
class TestRental(MockbusterCase):
    def test_sequence_is_assigned(self):
        rental = self.rent(self.dvd1)
        self.assertTrue(rental.name.startswith("RENT/"))

    def test_due_date_defaults_to_seven_days(self):
        rental = self.Rental.create(
            {
                "partner_id": self.customer.id,
                "dvd_id": self.dvd1.id,
                "date_start": date(2026, 1, 1),
            }
        )
        self.assertEqual(rental.date_due, date(2026, 1, 8))

    def test_due_date_before_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.Rental.create(
                {
                    "partner_id": self.customer.id,
                    "dvd_id": self.dvd1.id,
                    "date_start": date(2026, 1, 10),
                    "date_due": date(2026, 1, 5),
                }
            )

    def test_rent_and_return_updates_availability(self):
        self.assertEqual(self.movie.available_count, 2)
        rental = self.rent(self.dvd1)
        self.assertEqual(self.dvd1.state, "rented")
        self.assertEqual(self.movie.available_count, 1)

        rental.action_return()
        self.assertEqual(rental.state, "returned")
        self.assertEqual(rental.date_returned, self.today)
        self.assertEqual(self.dvd1.state, "available")
        self.assertEqual(self.movie.available_count, 2)

    def test_cannot_rent_a_copy_twice(self):
        self.rent(self.dvd1)
        second = self.Rental.create(
            {"partner_id": self.customer.id, "dvd_id": self.dvd1.id}
        )
        with self.assertRaises(UserError):
            second.action_start()

    def test_search_movie_by_actor(self):
        Movie = self.env["mockbuster.movie"]
        self.assertIn(self.movie, Movie.search([("actor_ids.name", "ilike", "murray")]))
        self.assertNotIn(
            self.movie, Movie.search([("actor_ids.name", "ilike", "nobody")])
        )

    def test_available_filter(self):
        Movie = self.env["mockbuster.movie"]
        self.rent(self.dvd1)
        self.rent(self.dvd2)
        self.assertNotIn(self.movie, Movie.search([("available_count", ">", 0)]))

    def test_overdue_compute_and_search(self):
        late = self.rent(self.dvd1, days_ago=10)
        on_time = self.rent(self.dvd2)
        self.assertTrue(late.is_overdue)
        self.assertFalse(on_time.is_overdue)
        found = self.Rental.search([("is_overdue", "=", True)])
        self.assertIn(late, found)
        self.assertNotIn(on_time, found)

    def test_rental_count(self):
        self.rent(self.dvd1).action_return()
        self.rent(self.dvd1)
        self.movie.invalidate_recordset(["rental_count"])
        self.assertEqual(self.movie.rental_count, 2)

    def test_receipt_report_renders(self):
        rental = self.rent(self.dvd1)
        html, _fmt = self.env["ir.actions.report"]._render_qweb_html(
            "mockbuster.action_report_rental", rental.ids
        )
        self.assertIn(b"Test Movie", html)
        self.assertIn(rental.name.encode(), html)
