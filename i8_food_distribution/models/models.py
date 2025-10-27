from odoo import models, fields

class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    meal_quantity = fields.Integer(string="Meal Quantity", default=1)


class EventEvent(models.Model):
    _inherit = "event.event"

    is_meal_service = fields.Boolean(string="Enable Meal Service", default=False)

    total_meals_requested = fields.Integer(
        string="Total Meals Requested",
        compute="_compute_total_meals_requested",
        compute_sudo=True,   # ensure ACLs do not hide shifts
        store=False,
    )

    def _compute_total_meals_requested(self):
        Shift = self.env["volunteer.shift"].sudo()
        for event in self:
            # count meal requests for this event (exclude rejected)
            shifts = Shift.search([("event_id", "=", event.id), ("state", "!=", "rejected")])
            event.total_meals_requested = sum(s.meal_quantity or 0 for s in shifts)
