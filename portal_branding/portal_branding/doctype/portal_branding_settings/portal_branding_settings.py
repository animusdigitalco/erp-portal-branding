import frappe
from frappe.model.document import Document
from frappe.utils import cint


COLOR_FIELDS = (
	"primary_color",
	"link_color",
	"navbar_background",
	"navbar_text_color",
	"page_background",
	"footer_background",
	"footer_text_color",
)


class PortalBrandingSettings(Document):
	def validate(self):
		self.validate_colors()
		self.generated_css = self.build_css()

	def validate_colors(self):
		"""Only valid hex colors make it into the generated stylesheet."""
		for fieldname in COLOR_FIELDS:
			value = (self.get(fieldname) or "").strip()
			if value and not parse_hex(value):
				frappe.throw(
					frappe._("{0} must be a hex color like #1a73e8").format(
						frappe.bold(self.meta.get_label(fieldname))
					)
				)

	def on_update(self):
		self.sync_website_settings()
		clear_website_cache()

	def build_css(self) -> str:
		rules = []

		primary = (self.primary_color or "").strip()
		link = (self.link_color or "").strip() or primary
		navbar_bg = (self.navbar_background or "").strip()
		navbar_text = (self.navbar_text_color or "").strip()
		page_bg = (self.page_background or "").strip()
		footer_bg = (self.footer_background or "").strip()
		footer_text = (self.footer_text_color or "").strip()

		if primary:
			primary_dark = shade(primary, 0.85) or primary
			rules.append(f":root {{ --primary: {primary}; --primary-color: {primary}; }}")
			rules.append(
				f".btn-primary {{ background-color: {primary} !important; "
				f"border-color: {primary} !important; }}"
			)
			rules.append(
				".btn-primary:hover, .btn-primary:focus, .btn-primary:active, "
				".btn-primary:not(:disabled):not(.disabled):active "
				f"{{ background-color: {primary_dark} !important; "
				f"border-color: {primary_dark} !important; }}"
			)
			rules.append(f".text-primary {{ color: {primary} !important; }}")
			rules.append(f".bg-primary, .badge-primary {{ background-color: {primary} !important; }}")
			rules.append(
				".sidebar-item.selected a, .sidebar-item.active a, "
				".portal-sidebar .selected a "
				f"{{ color: {primary} !important; }}"
			)
			rules.append(
				".form-control:focus "
				f"{{ border-color: {primary}; "
				f"box-shadow: 0 0 0 0.2rem {rgba(primary, 0.25) or 'transparent'}; }}"
			)

		if link:
			link_dark = shade(link, 0.8) or link
			rules.append(
				"a:not(.btn):not(.nav-link):not(.navbar-brand):not(.dropdown-item) "
				f"{{ color: {link}; }}"
			)
			rules.append(
				"a:not(.btn):not(.nav-link):not(.navbar-brand):not(.dropdown-item):hover "
				f"{{ color: {link_dark}; }}"
			)

		if navbar_bg:
			rules.append(
				f".navbar, header .navbar {{ background-color: {navbar_bg} !important; }}"
			)
		if navbar_text:
			rules.append(
				".navbar .nav-link, .navbar .navbar-brand, .navbar .dropdown-toggle, "
				".navbar .navbar-toggler, .navbar a "
				f"{{ color: {navbar_text} !important; }}"
			)

		if page_bg:
			rules.append(f"body {{ background-color: {page_bg}; }}")

		if footer_bg:
			rules.append(
				f".web-footer, footer.web-footer {{ background-color: {footer_bg} !important; }}"
			)
		if footer_text:
			rules.append(
				".web-footer, .web-footer a, .web-footer .footer-col-left, "
				".web-footer .footer-col-right "
				f"{{ color: {footer_text} !important; }}"
			)

		font_stack = self.get_font_stack()
		if font_stack:
			rules.append(f"body, .navbar, .btn, .form-control {{ font-family: {font_stack}; }}")

		if self.custom_css:
			rules.append(self.custom_css)

		return "\n".join(rules)

	def get_font_stack(self) -> str:
		fallback = (
			self.font_family
			or "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif"
		).strip()
		google_font = (self.google_font or "").strip()
		if google_font:
			return f"'{google_font}', {fallback}"
		if self.font_family:
			return fallback
		return ""

	def sync_website_settings(self):
		"""Push logo and favicon into Website Settings so the navbar,
		login page, and browser tab pick them up through Frappe's own plumbing."""
		if not self.enabled:
			return

		meta = frappe.get_meta("Website Settings")
		updates = {}

		if self.favicon and meta.has_field("favicon"):
			updates["favicon"] = self.favicon

		if self.logo:
			if meta.has_field("app_logo"):
				updates["app_logo"] = self.logo
			if cint(self.apply_logo_to_navbar) and meta.has_field("brand_html"):
				height = cint(self.logo_height) or 24
				app_name = frappe.db.get_single_value("Website Settings", "app_name") or "Home"
				alt = frappe.utils.escape_html(app_name)
				updates["brand_html"] = (
					f'<img src="{self.logo}" alt="{alt}" style="height: {height}px;">'
				)

		for fieldname, value in updates.items():
			frappe.db.set_value("Website Settings", "Website Settings", fieldname, value)


def shade(hex_color: str, factor: float) -> str | None:
	"""Darken (<1) or lighten (>1) a hex color. Returns None if unparseable."""
	parsed = parse_hex(hex_color)
	if not parsed:
		return None
	r, g, b = (min(255, max(0, round(c * factor))) for c in parsed)
	return f"#{r:02x}{g:02x}{b:02x}"


def rgba(hex_color: str, alpha: float) -> str | None:
	parsed = parse_hex(hex_color)
	if not parsed:
		return None
	r, g, b = parsed
	return f"rgba({r}, {g}, {b}, {alpha})"


def parse_hex(hex_color: str) -> tuple[int, int, int] | None:
	value = (hex_color or "").strip().lstrip("#")
	if len(value) == 3:
		value = "".join(c * 2 for c in value)
	if len(value) != 6:
		return None
	try:
		return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
	except ValueError:
		return None


def clear_website_cache():
	try:
		from frappe.website.utils import clear_cache

		clear_cache()
	except Exception:
		frappe.clear_cache()
