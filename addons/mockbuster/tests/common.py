from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class MockbusterCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rental = cls.env["mockbuster.rental"]
        cls.today = fields.Date.today()
        cls.actor = cls.env["mockbuster.actor"].create({"name": "Test Actor Murray"})
        cls.movie = cls.env["mockbuster.movie"].create(
            {
                "title": "Test Movie",
                "year": 1993,
                "actor_ids": [(6, 0, cls.actor.ids)],
            }
        )
        cls.dvd1, cls.dvd2 = cls.env["mockbuster.dvd"].create(
            [
                {"barcode": "TEST-001", "movie_id": cls.movie.id},
                {"barcode": "TEST-002", "movie_id": cls.movie.id},
            ]
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "email": "customer@example.com",
            }
        )

    def rent(self, dvd, days_ago=0):
        rental = self.Rental.create(
            {
                "partner_id": self.customer.id,
                "dvd_id": dvd.id,
                "date_start": self.today - timedelta(days=days_ago),
            }
        )
        rental.action_start()
        return rental
