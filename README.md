# PDF Toolbox

PDF Toolbox is a standalone macOS utility for everyday PDF cleanup and packaging tasks.

It includes:

- Merge PDFs in any order
- Merge PDFs by a `YYYYMMDD` filename prefix
- Convert images to PDF
- Split PDFs into single-page PDFs
- Remove scanner watermarks
- Compress scanned PDFs
- In-app Guide / Help and About sections

## macOS builds

This project is prepared for two macOS release tracks:

- Apple Silicon (`arm64`) for M-series Macs
- Intel (`x86_64`) for older Macs

Important:

- The app zip files are intentionally staged for GitHub Releases, not normal git commits.
- GitHub normally blocks files over `100 MB` in the repository itself.
- Upload the `.zip` files through the GitHub Releases page instead.

## Project layout

- [`pdf_toolkit`](./pdf_toolkit): shared app logic
- [`pdf_toolkit_app.py`](./pdf_toolkit_app.py): desktop launcher entry point
- [`pdf_toolkit_cli.py`](./pdf_toolkit_cli.py): CLI entry point
- [`scripts`](./scripts): build and release helpers
- [`docs`](./docs): install, build, and publishing guides
- [`release-assets`](./release-assets): local staging area for release zips

## Quick start

Run locally:

```bash
python pdf_toolkit_app.py
```

See CLI options:

```bash
python pdf_toolkit_cli.py --help
```

Build Apple Silicon release:

```bash
./scripts/build_arm64_release.sh
```

Build Intel release:

```bash
./scripts/build_intel_release.sh
```

## Publishing to GitHub

1. Put this `pdf-toolbox-github` folder into its own repository.
2. Commit the source and docs.
3. Do not commit the large `.zip` app bundles.
4. Create a GitHub Release and upload the staged zip files from [`release-assets`](./release-assets).

Detailed instructions:

- [`docs/BUILD.md`](./docs/BUILD.md)
- [`docs/INSTALL.md`](./docs/INSTALL.md)
- [`docs/PUBLISHING.md`](./docs/PUBLISHING.md)
- [`docs/RELEASE_TEMPLATE.md`](./docs/RELEASE_TEMPLATE.md)

## Copyright

See [`COPYRIGHT.txt`](./COPYRIGHT.txt).

If you want to allow source reuse by the public, add an explicit software license before publishing the repository.
