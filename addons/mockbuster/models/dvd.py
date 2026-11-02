from odoo import api, fields, models


class MockbusterDvd(models.Model):
    _name = "mockbuster.dvd"
    _description = "DVD copy"
    _order = "movie_id, barcode"

    barcode = fields.Char(required=True, copy=False)
    movie_id = fields.Many2one(
        "mockbuster.movie", required=True, ondelete="restrict", index=True
    )
    medium = fields.Selection(
        [("dvd", "DVD"), ("bluray", "Blu-ray"), ("vhs", "VHS")],
        default="dvd",
        required=True,
    )
    state = fields.Selection(
        [("available", "Available"), ("rented", "Rented"), ("lost", "Lost")],
        default="available",
        required=True,
    )
    rental_ids = fields.One2many("mockbuster.rental", "dvd_id")

    _sql_constraints = [
        ("barcode_unique", "UNIQUE(barcode)", "Barcode must be unique."),
    ]

    @api.depends("barcode", "movie_id.title")
    def _compute_display_name(self):
        for dvd in self:
            dvd.display_name = f"{dvd.movie_id.title or ''} [{dvd.barcode or ''}]"
