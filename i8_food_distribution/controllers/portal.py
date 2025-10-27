
from odoo import http
from odoo.http import request

class FoodDistributionPortal(http.Controller):

    @http.route(['/v/activity/<int:act_id>/signup_meal'], type='json', auth='user', csrf=False)
    def activity_signup_meal(self, act_id, meal_quantity=1, **kw):
        partner = request.env.user.partner_id
        Activity = request.env['volunteer.activity'].sudo()
        Shift = request.env['volunteer.shift'].sudo()
        act = Activity.browse(act_id)
        if not act.exists():
            return {"ok": False, "message": "Activity not found"}

        shift = Shift.search([('partner_id','=',partner.id), ('activity_id','=',act_id)], limit=1)
        vals = {
            "partner_id": partner.id,
            "activity_id": act_id,
            "event_id": act.event_id.id,
            "company_id": act.company_id.id,
            "meal_quantity": int(meal_quantity or 1),
            "state": "pending",
        }
        if shift:
            shift.write({"meal_quantity": vals["meal_quantity"]})
        else:
            shift = Shift.create(vals)

        return {"ok": True, "message": f"Signed up for {act.name} with {vals['meal_quantity']} meal(s)."}
