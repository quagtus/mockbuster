from odoo import _, api, fields, models

GENRES = [
    ("action", "Action"),
    ("comedy", "Comedy"),
    ("drama", "Drama"),
    ("horror", "Horror"),
    ("scifi", "Sci-Fi"),
    ("family", "Family"),
]


class MockbusterMovie(models.Model):
    _name = "mockbuster.movie"
    _description = "Movie"
    _order = "title"
    _rec_name = "title"

    title = fields.Char(required=True)
    year = fields.Integer()
    genre = fields.Selection(GENRES)
    director = fields.Char()
    duration = fields.Integer(string="Duration (min)")
    description = fields.Text()
    poster = fields.Image(max_width=512, max_height=512)
    actor_ids = fields.Many2many(
        "mockbuster.actor",
        "mockbuster_movie_actor_rel",
        "movie_id",
        "actor_id",
        string="Cast",
    )
    dvd_ids = fields.One2many("mockbuster.dvd", "movie_id", string="Copies")
    copy_count = fields.Integer(compute="_compute_availability", store=True)
    available_count = fields.Integer(
        string="Available copies", compute="_compute_availability", store=True
    )
    rental_count = fields.Integer(compute="_compute_rental_count")

    _sql_constraints = [
        (
            "year_check",
            "CHECK(year IS NULL OR year > 1880)",
            "Year must be after 1880.",
        ),
    ]

    @api.depends("dvd_ids", "dvd_ids.state")
    def _compute_availability(self):
        for movie in self:
            movie.copy_count = len(movie.dvd_ids)
            movie.available_count = len(
                movie.dvd_ids.filtered(lambda d: d.state == "available")
            )

    def _compute_rental_count(self):
        groups = self.env["mockbuster.rental"]._read_group(
            [("movie_id", "in", self.ids), ("state", "!=", "draft")],
            ["movie_id"],
            ["__count"],
        )
        counts = {movie.id: count for movie, count in groups}
        for movie in self:
            movie.rental_count = counts.get(movie.id, 0)

    def action_view_rentals(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Rentals of %s", self.title),
            "res_model": "mockbuster.rental",
            "view_mode": "tree,form",
            "domain": [("movie_id", "=", self.id)],
        }
