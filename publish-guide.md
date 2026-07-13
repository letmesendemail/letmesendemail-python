# Publishing — letmesendemail

## Registry

[PyPI](https://pypi.org) — `letmesendemail`

Package URL: `https://pypi.org/project/letmesendemail/`

## How Versioning Works

The package version is defined exclusively in `pyproject.toml` under
`[project] version`. The SDK reads it at runtime via
`importlib.metadata.version("letmesendemail")`.

**Versioned files:**

- `pyproject.toml` — `[project] version` field
- `CHANGELOG.md` — release section

## Maintainer Prerequisites

1. A PyPI account that is a maintainer of the `letmesendemail` project.
2. An API token from [pypi.org/manage/account/token](https://pypi.org/manage/account/token).
3. Two-factor authentication (2FA) enabled on the PyPI account.

## First-Time Setup

```bash
python3 -m pip install build twine
```

## Pre-Release Validation

Run all checks from the repository root before tagging:

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pyright
pytest
python3 -m build
twine check dist/*
```

Fix any failures before proceeding.

## Releasing a Version

```bash
# 1. Update the version in pyproject.toml (single source of truth)
# 2. Move Unreleased entries in CHANGELOG.md to a new version section
# 3. Commit all changes
git add -A
git commit -m "Release vX.Y.Z"

# 4. Tag and push both master and the tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin master vX.Y.Z
```

## Publishing to PyPI

Publishing is always manual.

```bash
# Clean previous builds
rm -rf dist/

# Build source distribution and wheel
python3 -m build

# Verify the built packages
twine check dist/*

# Upload (Twine prompts for the token without storing it in shell history)
python3 -m twine upload dist/* --username __token__
```

The `--username __token__` flag tells Twine to use token-based authentication.
Enter the token only at Twine's password prompt. For non-interactive release
automation, provide it through the CI secret `TWINE_PASSWORD`; never place the
token directly in a command, tracked file, or shell history. Tokens are scoped
to the entire account or to individual projects.

## Creating a GitHub Release

1. Go to the repository's Releases page.
2. Click "Draft a new release".
3. Select the existing tag (`vX.Y.Z`).
4. Add release notes from CHANGELOG.md.
5. Mark it as the latest release and publish.

## Verifying

```bash
pip install letmesendemail
python3 -c "from letmesendemail import LetMeSendEmail; print('OK')"
```

Then check that the installed version matches the released tag.

## Recovering a Broken Release

- **PyPI does not support overwriting published versions.** Publish a patch release
  with the fix instead.
- To yank a broken version (prevents new installs, existing installs remain),
  go to the project's Releases page on PyPI, click the version, and select "Yank".
- For severe security issues, contact PyPI support to request removal.
