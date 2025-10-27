from odoo import models, fields, api

class VolunteerActivity(models.Model):
    _name = "volunteer.activity"
    _description = "Volunteer Activity"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    event_id = fields.Many2one("event.event", required=True, ondelete="cascade", index=True, tracking=True)
    company_id = fields.Many2one(related="event_id.company_id", store=True, readonly=True)
    start = fields.Datetime(required=True)
    end = fields.Datetime(required=True)
    capacity = fields.Integer(default=0, help="0 = unlimited")
    allow_self_signup = fields.Boolean(default=True)
    notes = fields.Html()

    signup_ids = fields.One2many("volunteer.shift", "activity_id")
    volunteer_count = fields.Integer(compute="_compute_volunteer_count", store=False)
    # add inside VolunteerActivity
    x_rec_id = fields.Integer(string="Record ID", compute="_compute_rec_id")

    def _compute_rec_id(self):
        for r in self:
            r.x_rec_id = r.id

    @api.depends("signup_ids.state")
    def _compute_volunteer_count(self):
        for rec in self:
            rec.volunteer_count = len(rec.signup_ids.filtered(lambda s: s.state != 'rejected'))
