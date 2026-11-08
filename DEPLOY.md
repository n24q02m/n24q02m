# Site deployment

The static site for `n24q02m.com` lives in `site/` and is published to Cloudflare Pages.

- Pages project: `n24q02m-lab` (production branch `main`)
- Custom domains: `n24q02m.com` and `www.n24q02m.com`
- Deploy: run the `CD` workflow manually (`workflow_dispatch`). It uploads `site/` with
  `wrangler pages deploy site --project-name=n24q02m-lab --branch=main`.
- Repository secrets: `CLOUDFLARE_API_TOKEN` (Pages edit scope) and `CLOUDFLARE_ACCOUNT_ID`.
  Both are projected from the secret store with `skret sync --to=github` (see `.skret.yaml`);
  do not set them by hand.
- Rollback: redeploy an earlier commit, or promote a previous deployment in the Pages dashboard.

There is no build step: `site/` is plain HTML served as-is.
