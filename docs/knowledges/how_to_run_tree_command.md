---
title: How to run the tree command
description: Use the eza command instead of the tree command
---

When you want to run the `tree` command in the shell, use the `eza` command instead.

```bash
eza --tree --git-ignore -L 2 .
```

The `--tree` flag displays the directory structure in tree format.
The `--git-ignore` flag does not display files or directories that are ignored based on the `.gitignore` file.
The `-L 2` flag limits the tree depth to 2 levels.
`.` targets the current directory.

- Unless there is a clear intention otherwise, always use the `--git-ignore` flag
