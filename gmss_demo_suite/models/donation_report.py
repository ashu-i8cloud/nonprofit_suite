from odoo import api, fields, models, tools

class GmssDonationReport(models.Model):
    _name = "gmss.donation.report"
    _description = "GMSS Donation Report"
    _auto = False
    _rec_name = "partner_id"
    _order = "date_order desc"

    partner_id = fields.Many2one("res.partner", string="Donor", readonly=True)
    order_id = fields.Many2one("sale.order", string="Order", readonly=True)
    date_order = fields.Datetime("Date", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    fund_id = fields.Many2one(
        "account.analytic.account", string="Fund / Category", readonly=True, help="Reserved for future linkage."
    )
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    website_id = fields.Many2one("website", string="Website", readonly=True)
    amount_total = fields.Monetary("Donation Amount", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)
    state = fields.Selection(
        [("draft", "Quotation"), ("sale", "Sale Order"), ("done", "Done"), ("cancel", "Cancelled")],
        string="State",
        readonly=True,
    )
    donation_category_id = fields.Many2one(
        "product.category", string="Donation Category", readonly=True
    )

    def _select(self):
        return """
            SELECT
                sol.id AS id,
                so.id AS order_id,
                so.date_order AS date_order,
                so.partner_id AS partner_id,
                sol.product_id AS product_id,
                pt.categ_id AS donation_category_id,  -- <— changed
                sol.price_total AS amount_total,
                so.currency_id AS currency_id,
                so.company_id AS company_id,
                so.state AS state
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE so.state IN ('sale','done')
              AND pt.is_donation = TRUE
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"CREATE OR REPLACE VIEW {self._table} AS ({self._select()})")
