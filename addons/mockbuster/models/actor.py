from odoo import api, fields, models


class MockbusterActor(models.Model):
    _name = "mockbuster.actor"
    _description = "Actor"
    _order = "name"

    name = fields.Char(required=True)
    birth_date = fields.Date()
    movie_ids = fields.Many2many(
        "mockbuster.movie",
        "mockbuster_movie_actor_rel",
        "actor_id",
        "movie_id",
        string="Movies",
    )
    movie_count = fields.Integer(compute="_compute_movie_count")

    @api.depends("movie_ids")
    def _compute_movie_count(self):
        for actor in self:
            actor.movie_count = len(actor.movie_ids)
