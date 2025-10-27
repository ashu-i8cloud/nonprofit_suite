from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

class VolunteerShift(models.Model):
    _name = "volunteer.shift"
    _description = "Volunteer Shift (Signup & Time)"
    _inherit = ["mail.thread"]

    partner_id = fields.Many2one("res.partner", required=True, index=True)
    activity_id = fields.Many2one("volunteer.activity", required=True, ondelete="cascade", index=True)
    event_id = fields.Many2one(related="activity_id.event_id", store=True, readonly=True)
    company_id = fields.Many2one(related="activity_id.company_id", store=True, readonly=True)

    state = fields.Selection([
        ("pending", "Pending Approval"),
        ("confirmed", "Confirmed"),
        ("checkin", "Checked-In"),
        ("checkout", "Checked-Out"),
        ("rejected", "Rejected"),
    ], default="pending", tracking=True)

    check_in = fields.Datetime()
    check_out = fields.Datetime()
    duration_hours = fields.Float(compute="_compute_duration", store=True)
    certificate_attachment_id = fields.Many2one("ir.attachment")

    _sql_constraints = [
        ("unique_active_signup", "unique(partner_id, activity_id, state)",
         "Duplicate state row (technical). If this triggers, consider data cleanup.")
    ]

    @api.depends("check_in", "check_out")
    def _compute_duration(self):
        for rec in self:
            rec.duration_hours = 0.0
            if rec.check_in and rec.check_out:
                delta = fields.Datetime.to_datetime(rec.check_out) - fields.Datetime.to_datetime(rec.check_in)
                rec.duration_hours = round(delta.total_seconds() / 3600.0, 2)

    def action_confirm(self):
        for rec in self:
            if rec.state in ("pending", "rejected"):
                rec.state = "confirmed"

    def action_reject(self):
        for rec in self:
            if rec.state != "checkout":
                rec.state = "rejected"

    def action_check_in(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError("Your signup must be confirmed by the organizer before check-in.")
            rec.write({"check_in": fields.Datetime.now(), "state": "checkin"})

    def action_check_out(self):
        for rec in self:
            if rec.state != "checkin":
                raise UserError("You must check in first.")
            rec.write({"check_out": fields.Datetime.now(), "state": "checkout"})

    def action_generate_certificate(self):
        for rec in self:
            if rec.state != "checkout":
                raise UserError("Complete checkout before generating a certificate.")
            report = self.env.ref('i8_volunteer_demo.report_volunteer_certificate', raise_if_not_found=False)
            if not report:
                raise UserError("Volunteer certificate report is not installed.")
            pdf = report._render_qweb_pdf(
                'i8_volunteer_demo.report_volunteer_certificate',  # report_ref (xmlid)
                res_ids=[rec.id]
            )[0]
            att = self.env["ir.attachment"].create({
                "name": f"Certificate_{rec.partner_id.name}_{rec.id}.pdf",
                "datas": base64.b64encode(pdf),
                "res_model": self._name,
                "res_id": rec.id,
                "mimetype": "application/pdf",
            })
            # after: att = self.env["ir.attachment"].create({...})
            if not att.access_token:
                att.generate_access_token()  # v18 method

            rec.certificate_attachment_id = att.id
            att.copy({"res_model": "res.partner", "res_id": rec.partner_id.id})

            template = self.env.ref('i8_volunteer_demo.mail_template_volunteer_certificate', raise_if_not_found=False)
            if template and rec.partner_id.email:
                # attach the generated PDF to the outgoing email
                template.send_mail(rec.id, force_send=True, email_values={
                    'attachment_ids': [(4, att.id)],
                })

    def action_preview_certificate(self):
        self.ensure_one()
        report = self.env.ref('i8_volunteer_demo.report_volunteer_certificate')
        # opens the report viewer/download for this record
        return report.report_action(self)
