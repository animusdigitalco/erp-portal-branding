# Portal Branding

Rebrand the Frappe/ERPNext web portal with your own colors, logo, and fonts. No CSS required.

Out of the box, the ERPNext customer portal looks like ERPNext. Changing that means writing SCSS in a Website Theme and chasing down the Bootstrap classes the portal templates hardcode. This app replaces all of that with a settings page: pick your colors, upload your logo, save. The branding applies to every website and portal page, including the login page.

## What it does

- **Colors**: primary (buttons, active sidebar items, focus rings), links, navbar background and text, page background, footer background and text. Set only the ones you want; everything else stays stock.
- **Logo**: applied to the portal navbar and the login page by writing into Website Settings through Frappe's own plumbing, so it behaves exactly like a logo you set by hand.
- **Favicon**: same approach.
- **Fonts**: name any Google Font and it loads automatically, or supply your own CSS font stack.
- **Custom CSS**: an escape hatch field for anything the options above do not cover.
- **One switch**: uncheck Enabled and the portal goes back to stock styling instantly.

CSS is generated once when you save and injected into the page head. There is no build step, no template overrides, and no schema change to any core doctype.

## What it does not do

- It does not restyle the desk (the `/app` back office). Portal and website pages only.
- It does not restyle outgoing emails. Email templates do not inherit website CSS.
- It does not replace a full Website Theme. If you need heavy structural changes, you still want a theme or custom templates.

## Requirements

- Frappe Framework v15 or v16 (works with or without ERPNext)
- A site where you can install apps (bench or Frappe Cloud)

## Installation

### Bench (self-hosted)

From your bench directory:

```bash
bench get-app https://github.com/animusdigitalco/erp-portal-branding
bench --site yoursite.example.com install-app portal_branding
bench --site yoursite.example.com migrate
bench restart
```

Note that the app name is `portal_branding` (underscore) even though the repository is `erp-portal-branding`.

To install a specific branch or update later:

```bash
bench get-app https://github.com/animusdigitalco/erp-portal-branding --branch main
bench update --apps portal_branding
```

### Frappe Cloud

1. Open your bench group, go to **Apps**, and choose **Add App**.
2. Pick **From GitHub** and paste `https://github.com/animusdigitalco/erp-portal-branding`.
3. Deploy the bench, then install **Portal Branding** on your site from the site's Apps tab.

### Development install

If you keep apps locally and want to hack on this one:

```bash
cd ~/frappe-bench/apps
git clone https://github.com/animusdigitalco/erp-portal-branding portal_branding
cd ..
bench --site yoursite.localhost install-app portal_branding
bench --site yoursite.localhost migrate
bench start
```

### Verify the install

```bash
bench --site yoursite.example.com list-apps
```

You should see `portal_branding` in the list. Then open **Portal Branding Settings** from the desk search bar.

## Usage

1. In the desk, search for **Portal Branding Settings**.
2. Upload a logo and favicon, pick your colors, optionally set a Google Font.
3. Save.
4. Open the portal in a private window (so you see it logged out too) and check the login page, `/me`, and any portal list like `/orders`.

If a change does not show up, clear the website cache:

```bash
bench --site yoursite.example.com clear-website-cache
```

Saving the settings doc already does this for you, but a stubborn browser cache or proxy can hold the old page.

## How it works

- A single doctype, **Portal Branding Settings**, holds your choices and generates a small CSS block on save.
- The `update_website_context` hook appends that CSS (and the Google Font `<link>` tags, if set) to the head of every rendered website page. The hook is wrapped defensively so a bad value can never take down page rendering.
- Logo and favicon are written into **Website Settings** (`app_logo`, `brand_html`, `favicon`) so the navbar and login page pick them up natively. The app checks that those fields exist before writing, which keeps it tolerant of version differences between v15 and v16.

## Uninstall

```bash
bench --site yoursite.example.com uninstall-app portal_branding
```

The logo, brand HTML, and favicon written into Website Settings stay as you set them. Clear those fields by hand if you want them gone.

## License

MIT
