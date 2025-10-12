---
title: How to Define Tasks
description: Tasks are defined as mise File Tasks.
---

Tasks are defined as mise File Tasks under `mise-tasks/`.

You can check the current list of tasks with `mise tasks`.

```sh
> mise tasks
Name                Description
build               Build *
ci                  Run CI checks (setup, format, lint, typecheck, test, build) for all packages
clean               Clean *
default             Run format, lint-fix, typecheck *
download-test-data  Download test data to tests/data/large/
extract-changelog   Extract changelog section for a specific version
format              Format *
get-packages        Get list of packages to process (excludes meta-packages)
lint                Lint *
lint-fix            Lint auto-fix *
package             Run format, lint-fix, typecheck
package:build       Build <package>
package:clean       Clean <package>
package:format      Format code for a specific package
package:lint        Lint <package>
package:lint-fix    Lint auto-fix <package>
package:publish     Publish <package> to PyPI
package:test        Test <package>
package:typecheck   Type check <package>
setup               Setup development environment (install tools and sync dependencies)
test                Test *
typecheck           Type check *
update-changelog    Update CHANGELOG.md files for all packages with version entry
upgrade             Upgrade dependencies
version             Update version in root and all packages
```
