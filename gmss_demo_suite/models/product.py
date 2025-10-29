from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_donation = fields.Boolean(
        string="Is Donation",
        help="When enabled, sales of this product are counted as donations."
    )
