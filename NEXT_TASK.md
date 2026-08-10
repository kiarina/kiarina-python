# NEXT TASK

## Upgrade Pillow to 12.3

### Objective

Allow kiari to resolve Pillow 12.3.0 or later and clear its remaining Pillow
Dependabot alerts.

### Background

- kiari already declares `pillow>=11.3.0,<13`, but its lockfile remains on
  Pillow 11.3.0.
- Resolution of Pillow 12.3.0 fails because `kiarina-agi-data-builder==2.19.0`
  and `kiarina-agi-image==2.17.0` declare `pillow>=11.3.0,<12`.
- Pillow 12 removes some deprecated APIs, but the current direct usages in these
  packages use ordinary `Image.open`, `Image.fromarray`, `Image.resize`, and
  `Image.save` operations. Do not assume compatibility solely from this review;
  verify it with the package tests.
- kiarina-python supports Python 3.12 and later, so Pillow 12 dropping Python
  3.9 support is not a blocker.

### Required Changes

1. Change every Pillow requirement in the following files to
   `pillow>=12.3.0,<13`:
   - `packages/kiarina-agi-data-builder/pyproject.toml`
   - `packages/kiarina-agi-image/pyproject.toml`
2. Update the Pillow version shown in both image package READMEs:
   - `packages/kiarina-agi-image/README.md`
   - `packages/kiarina-agi-image/README.ja.md`
3. Refresh `uv.lock` and confirm that the resolved Pillow version is at least
   12.3.0 on every supported platform.
4. Review the Pillow 12 incompatible changes. Update implementation code only
   if tests or direct API inspection show an actual incompatibility.
5. Add regression tests only where an existing image, PDF, video-frame, or
   segmentation path is not already covered.

### Validation

Run at minimum:

```sh
mise run test kiarina-agi-data-builder
mise run test kiarina-agi-image
make
mise run ci
```

Also confirm the locked version:

```sh
uv tree --locked --package pillow --invert
```

### Changelog and Release

This dependency change requires a PyPI release. Before committing, add concise
`Unreleased` entries to:

- `CHANGELOG.md`
- `packages/kiarina/CHANGELOG.md`
- `packages/kiarina-agi-data-builder/CHANGELOG.md`
- `packages/kiarina-agi-image/CHANGELOG.md`

Follow `docs/runbooks/release/README.md` to release the changed packages and the
`kiarina` meta-package. Do not choose or publish a release version without the
release owner's instruction.

### kiari Follow-up

After the new kiarina packages are published:

1. Upgrade kiarina dependencies in `kiari`.
2. Run the kiarina-python documentation sync playbook required by kiari.
3. Run `uv lock --upgrade-package pillow` and confirm Pillow resolves to 12.3.0
   or later.
4. Run `make ci` in kiari.
5. Confirm that the remaining Pillow Dependabot alerts close after the updated
   lockfile reaches the default branch.

### Completion Criteria

- Both changed kiarina packages support and require `pillow>=12.3.0,<13`.
- Package tests and the full kiarina-python CI pass with Pillow 12.3.0 or later.
- The required packages and meta-package are released.
- kiari resolves the released packages with Pillow 12.3.0 or later and passes
  its full CI.
- kiari has no remaining Pillow Dependabot alerts.
