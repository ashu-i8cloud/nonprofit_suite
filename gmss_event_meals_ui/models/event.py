# -*- coding: utf-8 -*-
from odoo import models, fields

class EventEvent(models.Model):
    _inherit = "event.event"

    meal_service = fields.Boolean(string="Meal Service")
    expected_meals = fields.Integer(string="Expected Meals", help="Planned meal count for this event")
    actual_meals = fields.Integer(string="Actual Meals Served")