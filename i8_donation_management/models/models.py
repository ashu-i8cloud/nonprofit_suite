
from odoo import models, fields

PURPOSES = [
    ('food', 'Food Distribution'),
    ('education', 'Education'),
    ('maintenance', 'Maintenance'),
    ('medical', 'Medical Aid'),
    ('other', 'Other'),
]

class NpoDonation(models.Model):
    _name = 'npo.donation'
    _description = 'Donation'

    name = fields.Char(string='Reference', default=lambda self: self.env['ir.sequence'].next_by_code('npo.donation') or 'New')
    donor_id = fields.Many2one('res.partner', string='Donor')
    date = fields.Date(default=fields.Date.today)
    amount = fields.Float(required=True)
    purpose = fields.Selection(PURPOSES, required=True, default='food')
    notes = fields.Text()

class NpoFundUsage(models.Model):
    _name = 'npo.fund.usage'
    _description = 'Fund Usage / Allocation'

    name = fields.Char(string='Reference', default=lambda self: self.env['ir.sequence'].next_by_code('npo.fund.usage') or 'New')
    date = fields.Date(default=fields.Date.today)
    purpose = fields.Selection(PURPOSES, required=True, default='food')
    amount = fields.Float(required=True)
    event_id = fields.Many2one('event.event', string='Related Event')
    notes = fields.Text()
