from odoo import fields, models, tools

from ..models.movie import GENRES


class MockbusterRentalReport(models.Model):
    _name = "mockbuster.rental.report"
    _description = "Rental analysis"
    _auto = False
    _order = "date_start desc"

    movie_id = fields.Many2one("mockbuster.movie", readonly=True)
    genre = fields.Selection(GENRES, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    date_start = fields.Date(string="Rented on", readonly=True)
    rental_count = fields.Integer(string="# Rentals", readonly=True)
    days_rented = fields.Integer(readonly=True, group_operator="avg")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    r.id               AS id,
                    r.movie_id         AS movie_id,
                    m.genre            AS genre,
                    r.partner_id       AS partner_id,
                    r.date_start       AS date_start,
                    1                  AS rental_count,
                    COALESCE(r.date_returned, CURRENT_DATE) - r.date_start AS days_rented
                FROM mockbuster_rental r
                JOIN mockbuster_movie m ON m.id = r.movie_id
                WHERE r.state != 'draft'
            )
            """
        )
