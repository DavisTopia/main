# Nashville Tax Solutions Website

This repository contains the static website for Nashville Tax Solutions.

## GitHub Pages deployment

Every push to `main` deploys the site to GitHub Pages using the workflow in
`.github/workflows/pages.yml`. The workflow publishes the homepage, the
`about-us`, `blog`, `community`, `contact-us`, `faq`, `our-team`, and `services`
pages, the site assets, and the browser files needed from the WordPress capture
in `assets/vendor/wordpress/`. Blog articles and referenced media are static
files generated from the local WordPress backup; the full WordPress export under
`web/` remains local and is excluded from version control and the Pages artifact.

The project site URL is <https://davistopia.github.io/main/>.

The Pages build rewrites WordPress styles, scripts, and media to local paths on
captured pages. `.github/workflows/pages.yml` is the only Pages deployment
workflow; a raw repository upload would bypass these compatibility fixes.

## Static WordPress blog

The published archive is at `/blog/`. It contains the published posts and
referenced media from the local database dump and uploads folder. It does not
run WordPress or provide a WordPress editor, database, comments, or other
server-side features. The SQL dump is never copied into the site.

To refresh the static archive after updating the local WordPress backup, run:

```sh
python3 scripts/build_wordpress_blog.py \
  web/10_204_133_16.sql web/wp-content/uploads blog
```

Commit the generated changes in `blog/` along with any code changes, then push
to `main` to deploy them. GitHub Pages serves the archive as part of the
existing site, so no separate DNS record or WordPress hosting credits are
needed for `/blog/`. DNS only points a domain name at a host; it cannot run
WordPress or make the local backup available online.

If you later need an editable WordPress blog, it must be restored to a host that
supports PHP and a database. You can give that host a subdomain such as
`blog.nashvilletaxsolutions.com` by configuring the DNS record specified by
that host, but this requires WordPress hosting. Do not change the existing DNS
records without confirming where the main site is hosted. The repository's
`CNAME` currently configures `www.nashvilletaxsolutions.com` for GitHub Pages.

The Contact Us form uses the existing WordPress FormCraft and reCAPTCHA
services hosted at `nashvilletaxsolutions.com`; form submissions require that
backend to remain available.
