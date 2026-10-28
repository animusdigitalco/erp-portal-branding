app_name = "portal_branding"
app_title = "Portal Branding"
app_publisher = "Animus Digital"
app_description = (
    "Rebrand the Frappe/ERPNext web portal with your own colors, logo, and fonts. "
    "No CSS required."
)
app_email = "jon@animusdigital.co"
app_license = "MIT"

# Inject generated branding CSS (and optional Google Font) into the <head>
# of every website/portal page, including the login page.
update_website_context = [
    "portal_branding.overrides.update_website_context",
]
