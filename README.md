# Custom Caddy image

Caddy with AuthCrunch authorization, response replacement, and Cloudflare DNS support.
The Dockerfile pins Caddy and all three modules. The builder and runtime use the same Caddy release.

Pull requests build an AMD64 image and verify the Caddy version and required modules.
Authorization tests check role permissions and rejection of missing, tampered, expired, and unsigned tokens.
Pushes to `main` and version tags publish that tested image to `ghcr.io/elibosley/caddy-v2-jwt`.
Images include a full commit SHA tag. Deploy by digest when a fixed artifact is required.

Use **Actions → Docker → Run workflow** to rebuild the current release, including updated base-image packages.
The build workflow has no repository cron, so GitHub's scheduled-workflow inactivity rule does not disable it.
Dependabot checks Docker images and GitHub Actions weekly and opens update pull requests.
Module upgrades remain explicit Dockerfile changes; builds do not select an unreviewed module release automatically.

When upgrading an existing authorization policy to caddy-security 1.5, set its cookie name explicitly with
`set access_token cookie name YOUR_COOKIE_NAME`. A crypto key's `token_name` alone does not select that cookie for request authentication.

To build and verify locally:

```sh
docker buildx build --platform linux/amd64 --load -t caddy-custom:verify .
scripts/smoke-test.sh caddy-custom:verify
python3 tests/auth_check.py caddy-custom:verify
```

