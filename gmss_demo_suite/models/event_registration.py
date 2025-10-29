from odoo import api, models

class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.partner_id:
            rec.partner_id.is_devotee = True
        return rec
