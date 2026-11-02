from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MockbusterRental(models.Model):
    _name = "mockbuster.rental"
    _description = "Rental"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(default=lambda self: _("New"), readonly=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True
    )
    dvd_id = fields.Many2one(
        "mockbuster.dvd",
        string="Copy",
        required=True,
        tracking=True,
        domain="[('state', '=', 'available')]",
    )
    movie_id = fields.Many2one(related="dvd_id.movie_id", store=True, index=True)
    date_start = fields.Date(
        string="Rented on", default=fields.Date.context_today, required=True
    )
    rental_days = fields.Integer(default=7, required=True)
    date_due = fields.Date(
        string="Due back",
        compute="_compute_date_due",
        precompute=True,
        store=True,
        readonly=False,
        required=True,
        tracking=True,
    )
    
    date_returned = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ongoing", "Ongoing"), ("returned", "Returned")],
        default="draft",
        required=True,
        tracking=True,
    )
    is_overdue = fields.Boolean(
        compute="_compute_is_overdue", search="_search_is_overdue"
    )
    reminder_sent = fields.Boolean(copy=False)

    # computes and constraints

    @api.depends("date_start", "rental_days")
    def _compute_date_due(self):
        for rental in self:
            if rental.date_start:
                rental.date_due = rental.date_start + timedelta(days=rental.rental_days)

    @api.depends("state", "date_due")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for rental in self:
            rental.is_overdue = (
                rental.state == "ongoing"
                and bool(rental.date_due)
                and rental.date_due < today
            )

    def _search_is_overdue(self, operator, value):
        # depends on "today", must compute
        today = fields.Date.context_today(self)
        if (operator == "=") == bool(value):
            return [("state", "=", "ongoing"), ("date_due", "<", today)]
        return ["|", ("state", "!=", "ongoing"), ("date_due", ">=", today)]

    @api.constrains("date_start", "date_due")
    def _check_dates(self):
        for rental in self:
            if rental.date_due and rental.date_due < rental.date_start:
                raise ValidationError(
                    _("The due date cannot be before the start date.")
                )

    # CRUD

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "mockbuster.rental"
                ) or _("New")
        return super().create(vals_list)

    # actions

    def action_start(self):
        for rental in self:
            if rental.state != "draft":
                raise UserError(_("Only draft rentals can be handed out."))
            if rental.dvd_id.state != "available":
                raise UserError(
                    _("Copy %s is not available.", rental.dvd_id.display_name)
                )
            rental.dvd_id.state = "rented"
            rental.state = "ongoing"

    def action_return(self):
        today = fields.Date.context_today(self)
        for rental in self.filtered(lambda r: r.state == "ongoing"):
            rental.write({"state": "returned", "date_returned": today})
            rental.dvd_id.state = "available"

    # cron

    @api.model
    def _cron_send_overdue_reminders(self):
        template = self.env.ref("mockbuster.mail_template_rental_overdue")
        overdue = self.search(
            [("is_overdue", "=", True), ("reminder_sent", "=", False)]
        )
        for rental in overdue:
            template.send_mail(rental.id)
            rental.reminder_sent = True
            rental.message_post(
                body=_("Overdue reminder sent to %s.", rental.partner_id.name)
            )
        return True
