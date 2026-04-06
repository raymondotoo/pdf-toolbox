# Release Assets

This folder is the local staging area for release files that will be uploaded to GitHub Releases.

Do not commit the large `.zip` app files into the repository.

Use these subfolders:

- `apple-silicon/`
- `intel/`
- `legacy-intel/`

Typical upload flow:

1. Build the app
2. Stage the generated `.zip` here
3. Run `./scripts/update_release_checksums.sh`
4. Upload the `.zip` files and `checksums.sha256` to GitHub Releases
