import frappe

GOOGLE_FONT_WEIGHTS = "400;500;600;700"


def update_website_context(context):
	"""Inject the generated branding CSS (and optional Google Font) into the
	<head> of every rendered website/portal page.

	Everything is wrapped defensively: a failure here must never take down
	website rendering (this hook runs on every page, including /login).
	"""
	try:
		settings = frappe.get_cached_doc("Portal Branding Settings")
	except Exception:
		return

	try:
		if not settings.enabled:
			return

		fragments = []

		google_font = (settings.google_font or "").strip()
		if google_font:
			family = google_font.replace(" ", "+")
			fragments.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
			fragments.append(
				'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
			)
			fragments.append(
				'<link rel="stylesheet" '
				f'href="https://fonts.googleapis.com/css2?family={family}:wght@{GOOGLE_FONT_WEIGHTS}&display=swap">'
			)

		css = settings.generated_css or ""
		if css:
			fragments.append(f"<style data-portal-branding>\n{css}\n</style>")

		if fragments:
			# base.html renders {{ head_include or "" }} inside <head> on both
			# v15 and v16 (frappe/templates/base.html, block head_include).
			context.head_include = (context.get("head_include") or "") + "\n" + "\n".join(fragments)
	except Exception:
		frappe.log_error(title="Portal Branding: failed to inject branding CSS")
