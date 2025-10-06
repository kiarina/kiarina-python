---
title: Development Flow for kiarina-python
description: Explains the process from receiving development/fix requests for kiarina-python through development, testing, and Pull Request creation.
---

### Receiving Tasks

Determine if it's a request for new feature development.
- Examples: "Please add ~", "Please improve ~", "Please fix ~", etc.

Accurately understand the request content.
- If the request is unclear, confirm the details.

---

### Design, Implementation, and Testing

Consider the design of the new feature based on the request.
- Consider consistency with existing features.
- Aim for a design with low cognitive load.

Create a development branch from the main branch.

Commit the implementation on the development branch.

Implement tests.

Execute the following to run Lint (auto fix), Format, Type Check, and Test, and confirm there are no issues.
`mise run package $package_name`

Run tests for all packages and confirm there are no issues.
`mise run ci`

---

### Updating CHANGELOG.md

For changes to features published on PyPI, record them in the CHANGELOG.md of the target sub project, meta project, and root project.

- Update the sub project's CHANGELOG.md: `packages/{package_name}/CHANGELOG.md`
  - Record detailed update content
- Update the meta package project's CHANGELOG.md: `packages/kiarina/CHANGELOG.md`
  - Record one line concisely for each item
- Update the root project's CHANGELOG.md: `CHANGELOG.md`
  - Record one line concisely for each item

Commit and push the CHANGELOG.md updates.

---

### Creating a Pull Request

Create a Pull Request against the main branch using the gh command.
- Use the body written to a tmp file as reference

When the Pull Request receives a review, respond to the feedback.
The list of discussions can be checked with `gh discussion list`.
Discussions can be viewed with `gh discussion view <number> --comments`.
