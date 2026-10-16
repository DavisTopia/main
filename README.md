# Nashville Tax Solutions Website

This repository contains the static website for Nashville Tax Solutions.

## GitHub Pages deployment

Every push to `main` deploys the site to GitHub Pages using the workflow in
`.github/workflows/pages.yml`. The workflow publishes the homepage, the
`about-us`, `community`, `contact-us`, `faq`, `our-team`, and `services` pages,
the site assets, and the browser files needed from the WordPress capture in
`assets/vendor/wordpress/`. The build rewrites homepage theme and media
references to local paths. The full WordPress export under `web/` remains local
and is excluded from version control and the Pages artifact.

The project site URL is <https://davistopia.github.io/main/>.

The Contact Us form uses the existing WordPress FormCraft and reCAPTCHA
services hosted at `nashvilletaxsolutions.com`; form submissions require that
backend to remain available.
