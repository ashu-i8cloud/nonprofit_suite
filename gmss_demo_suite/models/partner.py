from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_devotee = fields.Boolean("Is Devotee")
    is_volunteer = fields.Boolean("Is Volunteer")
    is_donor = fields.Boolean("Is Donor", help="Checked automatically when this contact makes a donation.")
    birthday = fields.Date("Date of Birth")
    preferred_temple = fields.Char("Preferred Temple")
    gotra = fields.Char("Gotra / Family Lineage")
    skills = fields.Char("Skills (comma separated)")
    availability = fields.Char("Availability")
    notes_internal = fields.Text("Internal Notes")

    # Orders that include donation products (computed, no SQL)
    donation_order_ids = fields.Many2many(
        "sale.order",
        compute="_compute_donation_orders",
        string="Donation Orders",
        store=False,
    )
    total_donations = fields.Monetary(
        string="Total Donations",
        compute="_compute_total_donations",
        currency_field="company_currency_id",
        store=False,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency",
        store=False,
    )

    @api.depends("company_id")
    def _compute_currency(self):
        for rec in self:
            rec.company_currency_id = rec.company_id.currency_id or self.env.company.currency_id

    @api.depends("sale_order_count")
    def _compute_donation_orders(self):
        for partner in self:
            partner.donation_order_ids = self.env["sale.order"].search([
                ("partner_id", "=", partner.id),
                ("state", "in", ["sale", "done"]),
                ("order_line.product_id.product_tmpl_id.is_donation", "=", True),
            ])

    @api.depends("sale_order_count")
    def _compute_total_donations(self):
        for partner in self:
            total = 0.0
            orders = self.env["sale.order"].search([
                ("partner_id", "=", partner.id),
                ("state", "in", ["sale", "done"]),
            ])
            for line in orders.mapped("order_line"):
                if line.product_id.product_tmpl_id.is_donation:
                    total += line.price_total
            partner.total_donations = total
