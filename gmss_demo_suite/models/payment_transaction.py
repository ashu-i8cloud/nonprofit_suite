# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    donation_sale_order_id = fields.Many2one("sale.order", string="Donation SO", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("GMSS: payment.transaction.create %s", [v.get('reference') for v in vals_list])
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            _logger.info("GMSS: payment.transaction.write state->%s ids=%s", vals['state'], self.ids)
        return res

    # Called when state becomes 'done' in many flows
    def _set_done(self):
        _logger.info("GMSS: _set_done ids=%s", self.ids)
        res = super()._set_done()
        self._gmss_make_so_from_donation()
        return res

    # Called after done (some providers)
    def _post_process_after_done(self, **kwargs):
        _logger.info("GMSS: _post_process_after_done ids=%s kwargs=%s", self.ids, kwargs)
        res = super()._post_process_after_done(**kwargs)
        self._gmss_make_so_from_donation()
        return res

    # Called at the very end for others
    def _finalize_post_processing(self, **kwargs):
        _logger.info("GMSS: _finalize_post_processing ids=%s kwargs=%s", self.ids, kwargs)
        res = super()._finalize_post_processing(**kwargs)
        self._gmss_make_so_from_donation()
        return res

    def _gmss_make_so_from_donation(self):
        for tx in self.sudo():
            try:
                _logger.info(
                    "GMSS: evaluating tx[%s] state=%s amount=%s ref=%s",
                    tx.id, tx.state, tx.amount, tx.reference,
                )

                if tx.state != "done" or tx.donation_sale_order_id:
                    _logger.info("GMSS: skip tx[%s] (state!=done or already linked)", tx.id)
                    continue

                # Determine website safely
                website = False
                if tx.sale_order_ids:
                    website = tx.sale_order_ids[0].website_id
                elif hasattr(tx.provider_id, "website_id"):
                    website = tx.provider_id.website_id

                # Treat as website donation only if no linked SO/invoice and payment from Demo/Website
                is_website_donation = not tx.sale_order_ids and not tx.invoice_ids and tx.provider_id.code in (
                "demo", "stripe", "paypal")
                if not is_website_donation:
                    _logger.info("GMSS: tx[%s] not a website donation", tx.id)
                    continue

                partner = tx.partner_id or self.env.ref("base.public_partner")
                product = self.env.ref("gmss_demo_suite.product_donation_general", raise_if_not_found=False)
                if not product:
                    _logger.warning("GMSS: donation product missing; abort tx[%s]", tx.id)
                    continue

                so_vals = {
                    "partner_id": partner.id,
                    "website_id": website.id if website else False,
                    "origin": f"Website Donation {tx.reference or ''}".strip(),
                    "order_line": [(0, 0, {
                        "product_id": product.id,
                        "name": product.display_name,
                        "product_uom_qty": 1.0,
                        "price_unit": tx.amount or 0.0,
                    })],
                }
                so = self.env["sale.order"].create(so_vals)
                _logger.info("GMSS: created SO %s for tx[%s]", so.name, tx.id)
                so.action_confirm()
                _logger.info("GMSS: confirmed SO %s", so.name)

                if hasattr(partner, "is_donor") and not partner.is_donor:
                    partner.is_donor = True
                    _logger.info("GMSS: partner %s marked donor", partner.id)

                tx.donation_sale_order_id = so.id
                _logger.info("GMSS: linked tx[%s] → SO %s", tx.id, so.name)

            except Exception as e:
                _logger.exception("GMSS: error creating SO for tx[%s]: %s", tx.id, e)
