from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        order = super().create(vals)
        # Website order?
        if order.website_id and order.partner_id:
            # first purchase? (exclude this order)
            prev = self.search_count([
                ('partner_id', '=', order.partner_id.id),
                ('id', '!=', order.id),
            ])
            if prev == 0:
                self.env['crm.lead'].sudo().create({
                    'name': f"New web supporter: {order.partner_id.display_name}",
                    'type': 'opportunity',
                    'partner_id': order.partner_id.id,
                    'email_from': order.partner_id.email or False,
                    'mobile': order.partner_id.mobile or order.partner_id.phone or False,
                    'description': f"Auto-created from website order {order.name}",
                    'priority': '1',  # low/normal
                })
        return order

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            # Only for website orders, real customers (not companies)
            if not order.website_id or not order.partner_id or order.partner_id.is_company:
                continue
            # mark donor if any donation product is on this order
            has_donation = any(
                line.product_id.product_tmpl_id.is_donation
                for line in order.order_line
            )
            if has_donation and order.partner_id and not order.partner_id.is_donor:
                order.partner_id.is_donor = True
            # First confirmed order for this partner?
            previous = self.search_count([
                ("partner_id", "=", order.partner_id.id),
                ("state", "in", ["sale", "done"]),
                ("id", "!=", order.id),
            ])
            if previous == 0:
                self.env["crm.lead"].sudo().create({
                    "name": f"New web supporter: {order.partner_id.display_name}",
                    "type": "opportunity",
                    "partner_id": order.partner_id.id,
                    "email_from": order.partner_id.email or False,
                    "mobile": order.partner_id.mobile or order.partner_id.phone or False,
                    "description": f"Auto-created from website order {order.name}",
                    "team_id": False,  # set a Sales Team if you want
                    "priority": "1",
                    "referred": "Website",  # optional field in some editions
                })
        return res