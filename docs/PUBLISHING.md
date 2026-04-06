# GitHub Publishing Guide

## 1. Create a clean repository

Put the contents of `pdf-toolbox-github` into a new repository folder, then:

```bash
git init
git add .
git commit -m "Initial PDF Toolbox release"
```

## 2. Push the source repository

Create a new GitHub repository, then connect and push:

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## 3. Do not commit the large app zips

The release zip files are intentionally ignored by `.gitignore`.

Why:

- GitHub repository files over `100 MB` are blocked in normal git pushes
- app bundles are better distributed through GitHub Releases

## 4. Create a GitHub Release

On GitHub:

1. Open the repository
2. Go to `Releases`
3. Click `Draft a new release`
4. Tag the release, for example `v1.0.0`
5. Paste the release notes from [`RELEASE_TEMPLATE.md`](./RELEASE_TEMPLATE.md)
6. Upload the staged zip files from:
   - `release-assets/apple-silicon/`
   - `release-assets/intel/`
7. Publish the release

## 5. Recommended release assets

- `PDF-Toolbox-macOS-Apple-Silicon-1.0.0.zip`
- `PDF-Toolbox-macOS-Intel-1.0.0.zip`
- `checksums.sha256`

## 6. Before making the repo public

Check these items:

- remove any personal PDFs or private documents
- confirm the copyright text is correct
- choose a license if you want to allow public source reuse
- test both Apple Silicon and Intel downloads
