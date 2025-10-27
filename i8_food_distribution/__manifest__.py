{
    "name": "i8 Food Distribution",
    "version": "18.0.1.0.0",
    "summary": "Meal quantity sign-ups for daily food distribution events",
    "depends": ["base", "web", "portal", "website", "event", "i8_volunteer_demo"],
    "data": ["views/event_views_inherit.xml", "views/portal_inherit.xml", "security/ir.model.access.csv",
             "views/menu.xml", "views/volunteer_shift_inherit.xml",],
    "assets": {"web.assets_frontend": ["i8_food_distribution/static/src/js/meal_signup.js"],
               "web.assets_frontend_minimal": ["i8_food_distribution/static/src/js/meal_signup.js"]},
    "application": False,
    "license": "OEEL-1",
}
