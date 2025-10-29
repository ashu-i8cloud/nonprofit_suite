# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta

class GmssBirthdayCampaign(models.Model):
    _name = "gmss.birthday.campaign"
    _description = "GMSS Birthday Campaign Helper"

    @api.model
    def _find_upcoming_birthdays(self, days_ahead=14, limit=200):
        today = date.today()
        end = today + timedelta(days=days_ahead)
        partners = self.env['res.partner'].search([
            ('birthday', '!=', False),
            ('email', '!=', False),
            ('active', '=', True),
        ], limit=limit)

        result = []
        for p in partners:
            bday = p.birthday
            if not bday:
                continue
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            if today <= bday_this_year <= end:
                result.append(p)
        return result

    @api.model
    def run_birthday_campaign(self, days_ahead=14):
        template = self.env.ref('gmss_demo_suite.mail_template_birthday_seva', raise_if_not_found=False)
        if not template:
            return
        for partner in self._find_upcoming_birthdays(days_ahead=days_ahead):
            if partner.email and not getattr(partner, 'opt_out', False):
                template.send_mail(partner.id, force_send=False)
