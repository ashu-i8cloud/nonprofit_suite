from odoo import models, fields

class EventBroadcastWizard(models.TransientModel):
    _name = "event.broadcast.wizard"
    _description = "Broadcast Message to Event Volunteers"

    event_id = fields.Many2one("event.event", required=True)
    message_body = fields.Html(required=True)

    def action_broadcast(self):
        self.ensure_one()
        self.event_id.message_post(body=self.message_body, subtype_xmlid="mail.mt_comment")
        shifts = self.env["volunteer.shift"].search([
            ("event_id", "=", self.event_id.id),
            ("state", "in", ["pending", "confirmed", "checkin", "checkout"])
        ])
        partners = shifts.mapped("partner_id").filtered(lambda p: p.email)
        if partners:
            mail_vals = {
                "subject": f"[Event Update] {self.event_id.name}",
                "body_html": self.message_body,
                "email_to": ",".join(partners.mapped("email")),
            }
            self.env["mail.mail"].create(mail_vals).send()
        return {"type": "ir.actions.act_window_close"}
