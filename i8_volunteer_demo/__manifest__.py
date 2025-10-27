{
    "name": "i8 Volunteer Demo",
    "version": "18.0.1.0.0",
    "summary": "Volunteer activities: signup (pending), admin confirm, check-in/out, broadcast, certificates",
    "depends": ["base", "web", "portal", "mail", "event", "contacts"],
    "data": [
        "security/volunteer_security.xml",
        "security/ir.model.access.csv",
        "views/volunteer_shift_views.xml",
        "views/volunteer_activity_views.xml",
        "views/broadcast_wizard_views.xml",
        "views/event_views_inherit.xml",
        "views/portal_pages.xml",
        "views/portal_my_link.xml",
        #"views/portal_templates.xml",
        "views/menu.xml",
        "report/volunteer_certificate_template.xml",
        "report/volunteer_certificate_report.xml",
        "data/mail_template_volunteer_certificate.xml",
        "data/demo_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "i8_volunteer_demo/static/src/js/volunteer_portal.js",
        ],
        "web.assets_frontend_minimal": [
            "i8_volunteer_demo/static/src/js/volunteer_portal.js",
        ],
    },
    "application": True,
    "license": "OEEL-1"
}
