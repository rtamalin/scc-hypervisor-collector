# pandoc generated man pages

The man pages are generated from Markdown based input files using
pandoc.

## Updating the man pages

If changes are needed in the man pages, the required changes should
be made to the Markdown input files.

Then (re)generate the man pages using:

```
% make all
```

## Why use pre-generated man pages?

The pandoc command is not available for SLE build targets in OBS
so the man pages should be pre-generated and committed into the
repo so that the build process can pull them into the built RPM(s).
