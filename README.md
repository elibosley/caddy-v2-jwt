# Custom Caddy image

Caddy with AuthCrunch authorization, response replacement, and Cloudflare DNS support.
The Dockerfile pins Caddy and all three modules. The builder and runtime use the same Caddy release.

Pull requests build an AMD64 image and verify the Caddy version and required modules.
Pushes to `main` and version tags publish that tested image to `ghcr.io/elibosley/caddy-v2-jwt`.
Images include a full commit SHA tag. Deploy by digest when a fixed artifact is required.

Use **Actions → Docker → Run workflow** to rebuild the current release, including updated base-image packages.
The build workflow has no repository cron, so GitHub's scheduled-workflow inactivity rule does not disable it.
Dependabot checks Docker images and GitHub Actions weekly and opens update pull requests.
Module upgrades remain explicit Dockerfile changes; builds do not select an unreviewed module release automatically.

To build and verify locally:

```sh
docker buildx build --platform linux/amd64 --load -t caddy-custom:verify .
scripts/smoke-test.sh caddy-custom:verify
```

