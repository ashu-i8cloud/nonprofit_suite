from odoo import http, fields
from odoo.http import request
from odoo.tools import html2plaintext

import logging
_logger = logging.getLogger(__name__)

class VolunteerPortal(http.Controller):

    @http.route(['/v/chapters'], type='http', auth='user', website=True)
    def chapters(self, **kw):
        companies = request.env['res.company'].sudo().search([])
        return request.render('i8_volunteer_demo.page_chapters', {"companies": companies})

    @http.route(['/v/events'], type='http', auth='user', website=True)
    def portal_events(self, **kw):
        print("Method called")
        # 1) read chapter id safely
        chapter_raw = kw.get('chapter') or '0'
        try:
            chapter_id = int(chapter_raw)
        except Exception:
            chapter_id = 0
        if not chapter_id:
            _logger.info("[i8_volunteer_demo] /v/events missing chapter param: %r", chapter_raw)
            return request.redirect('/v/chapters')

        # 2) fetch events for that company (sudo to ignore portal ACLs)
        domain = [('company_id', '=', chapter_id)]
        events = request.env['event.event'].sudo().search(domain, order='date_begin asc')
        _logger.info("[i8_volunteer_demo] /v/events chapter=%s found=%s ids=%s",
                     chapter_id, len(events), events.ids)

        # 3) if nothing returned, log a hint and (temporarily) fall back to show all (debug aid)
        if not events:
            any_events = request.env['event.event'].sudo().search([], limit=3)
            _logger.info("[i8_volunteer_demo] No events for company %s. Sample other events (ids): %s",
                            chapter_id, any_events.ids)

        # 4) build SAFE card dicts (plain text desc + resolvable image url)
        cards = []
        for e in events:
            desc_plain = html2plaintext(e.note or '').strip()
            short_desc = (desc_plain[:160] + ('…' if len(desc_plain) > 160 else '')) if desc_plain else ''
            img_url = e.badge_image and f"/web/image?model=event.event&id={e.id}&field=badge_image" or "/web/static/img/placeholder.png"
            cards.append({
                "id": e.id,
                "name": e.name,
                "date_begin": e.date_begin,
                "date_end": e.date_end,
                "short_desc": short_desc,
                "img_url": img_url,
            })
        _logger.info("[i8_volunteer_demo] /v/events cards=%s",
                     cards)
        # 5) render with 'cards' (what the template uses)
        return request.render('i8_volunteer_demo.page_events', {
            "chapter": chapter_id,
            "cards": cards,
        })

    @http.route(['/v/event/<int:event_id>'], type='http', auth='user', website=True)
    def event_detail(self, event_id, **kw):
        event = request.env['event.event'].sudo().browse(event_id)
        activities = request.env['volunteer.activity'].sudo().search([('event_id', '=', event_id)])
        my_partner = request.env.user.partner_id
        my_shifts = request.env['volunteer.shift'].sudo().search([
            ('partner_id', '=', my_partner.id),
            ('event_id', '=', event_id)
        ])
        # NEW: map activity_id -> shift (first one)
        my_shift_by_activity = {s.activity_id.id: s for s in my_shifts}

        return request.render('i8_volunteer_demo.page_event_detail', {
            "event": event,
            "activities": activities,
            "my_shifts": my_shifts,
            "my_shift_by_activity": my_shift_by_activity,  # <-- pass mapping
        })

    @http.route(['/v/activity/<int:act_id>/signup'], type='json', auth='user', csrf=False)
    def activity_signup(self, act_id, **kw):
        act = request.env['volunteer.activity'].sudo().browse(act_id)
        partner = request.env.user.partner_id
        _logger.info("[i8_volunteer_demo] signup partner=%s activity=%s", partner.id, act.id)
        if not act.allow_self_signup:
            return {"ok": False, "message": "Self-signup not allowed for this activity."}
        # capacity check (ignore rejected)
        if act.capacity and len(act.signup_ids.filtered(lambda s: s.state != 'rejected')) >= act.capacity:
            return {"ok": False, "message": "Capacity reached."}
        # prevent duplicates (except rejected)
        exists = request.env['volunteer.shift'].sudo().search_count([
            ('partner_id', '=', partner.id),
            ('activity_id', '=', act.id),
            ('state', '!=', 'rejected'),
        ])
        if exists:
            return {"ok": False, "message": "You are already signed up for this activity."}
        shift = request.env['volunteer.shift'].sudo().create({
            "partner_id": partner.id,
            "activity_id": act.id,
            "state": "pending",
        })
        return {"ok": True, "shift_id": shift.id, "message": "Signup received. Await confirmation."}

    @http.route(['/v/shift/<int:shift_id>/checkin'], type='json', auth='user', csrf=False)
    def shift_checkin(self, shift_id, **kw):
        shift = request.env['volunteer.shift'].sudo().browse(shift_id)
        _logger.info("[i8_volunteer_demo] checkin partner=%s shift=%s", request.env.user.partner_id.id, shift.id)
        if shift.partner_id.id != request.env.user.partner_id.id:
            return {"ok": False, "message": "Unauthorized"}
        try:
            shift.action_check_in()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    @http.route(['/v/shift/<int:shift_id>/checkout'], type='json', auth='user', csrf=False)
    def shift_checkout(self, shift_id, **kw):
        shift = request.env['volunteer.shift'].sudo().browse(shift_id)
        _logger.info("[i8_volunteer_demo] checkout partner=%s shift=%s", request.env.user.partner_id.id, shift.id)
        if shift.partner_id.id != request.env.user.partner_id.id:
            return {"ok": False, "message": "Unauthorized"}
        try:
            shift.action_check_out()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "message": str(e)}
