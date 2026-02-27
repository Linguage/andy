# Academic Site (Jekyll)

This repository contains a GitHub Pages-compatible Jekyll site for an academic profile.

## Development environments

### macOS

```bash
bundle install
bundle exec jekyll serve
```

### Windows (recommended: WSL2)

Use Ubuntu in WSL2 and run the same commands as Linux/macOS:

```bash
bundle install
bundle exec jekyll serve
```

This keeps local behavior close to CI and GitHub Pages build behavior.

## Build

```bash
bundle exec jekyll build
```

## Content model

All maintained content lives in `contents/`.

- `contents/data/*.csv`: structured lists (publications, projects, teaching, field testing, CV tables)
- `contents/_blocks/*.md`: page narrative blocks rendered inside page templates

Page files in `pages/` (`index.md`, `publications.md`, etc.) are renderers only.

### CSV schemas

- `contents/data/publications.csv`
  - `id,title,year,type,authors,venue,links,tags,lang`
  - `authors` and `tags` are semicolon-separated values.
- `contents/data/teaching_phd.csv`
  - `name,status,period,links`
- `contents/data/teaching_master.csv`
  - `name,status,period,links`
- `contents/data/teaching_courses.csv`
  - `code,name,role,links`
- `contents/data/projects_research.csv`
  - `year,title,description,links`
- `contents/data/projects_commission.csv`
  - `period,title,links`
- `contents/data/field_testing.csv`
  - `date,year,location,title,notes,links`
- `contents/data/external_profiles.csv`
  - `label,url`
- `contents/data/cv_general.csv`
  - `affiliation,department,profile_url`
- `contents/data/cv_employments.csv`
  - `period,title,org,links`
- `contents/data/cv_awards.csv`
  - `year,item,links`

For CSV files that include `links`, use:

- single link: `Label|https://example.com`
- multiple links: `Label A|https://a.com;Label B|https://b.com`
- publications style (recommended, matching legacy site): `web|...`, `doi|...`, `pdf|...`
- publications fallback rendering: if `links` is empty, the page auto-generates `web`, `scholar`, and `diva` links from the title query.

## Data migration helper

A one-time script is available to export existing `_data/*.yml` into CSV files:

```bash
ruby script/migrate_yaml_to_csv.rb
```

## Validation

```bash
ruby script/validate_publications.rb
ruby script/check_links.rb
# Optional for offline environments:
ALLOW_OFFLINE=1 ruby script/check_links.rb
```

## CI and deployment

- `.github/workflows/site-ci.yml` validates schema, builds the site, and checks publication links.
- `.github/workflows/deploy-pages.yml` deploys to GitHub Pages on pushes to `main`.

In repository settings, set **Pages > Source** to **GitHub Actions**.

## Deploy target: `https://linguage.github.io/andy`

The site is configured as a GitHub Pages **project site** with:

- `url: https://linguage.github.io`
- `baseurl: /andy`

To publish:

1. Push this repository to `linguage/andy`.
2. In `linguage/andy` settings, enable **Pages > Build and deployment > Source: GitHub Actions**.
3. Push to `main`; the `deploy-pages.yml` workflow publishes the site.

If this repository is private, GitHub plan constraints apply. See GitHub Pages plan/visibility notes in the GitHub Docs.

## Private -> Public sync workflow

If your source repository is private and Pages must be served from a public repo, use:

- `.github/workflows/sync-to-public.yml` in the private source repo
- target public repo: `linguage/andy` (editable in workflow env `PUBLIC_REPO`)

Required setup in the private source repository:

1. Create secret `PUBLIC_REPO_PAT`
   - Personal access token (classic) with `repo` scope, or fine-grained token with **Contents: Read and write** for the target public repo.
2. Push to `main`
   - Workflow syncs files to `linguage/andy` automatically.

Notes:

- The sync excludes `.github/workflows/sync-to-public.yml` in the target repo to avoid self-sync recursion.
- Keep `deploy-pages.yml` in the public repo so each sync commit triggers Pages deployment.
