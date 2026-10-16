# Nashville Tax Solutions Website

This repository contains the static website for Nashville Tax Solutions.

## GitHub Pages deployment

Every push to `main` deploys the site to GitHub Pages using the workflow in
`.github/workflows/pages.yml`. The workflow publishes the homepage, the
`about-us`, `community`, `contact-us`, `faq`, `our-team`, and `services` pages,
the `assets` directory, and browser assets captured in `web/`. The build rewrites
available homepage theme assets to local paths and excludes database exports
and unrelated source/media files from the Pages artifact.

The project site URL is <https://davistopia.github.io/main/>.

The Contact Us form uses the existing WordPress FormCraft and reCAPTCHA
services hosted at `nashvilletaxsolutions.com`; form submissions require that
backend to remain available.
