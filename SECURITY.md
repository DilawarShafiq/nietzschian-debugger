# Security policy

## Reporting a vulnerability

Please **don't open a public issue** for security problems. Report them privately
through GitHub: **Security → Report a vulnerability**, or
[open an advisory directly](https://github.com/DilawarShafiq/nietzschian-debugger/security/advisories/new).

You'll get a reply within a few days. Once a fix ships, you'll be credited in the
release notes unless you'd rather not be.

## Supported versions

Only the latest release on [PyPI](https://pypi.org/project/nietzschian-debugger/)
receives fixes.

## What to know about `predict`

`predict` imports and runs functions from the file you point it at. It runs them
in a separate process with a timeout, but **it is not a sandbox**: the code can
read your files and use the network. Secret-looking environment variables (API
keys, tokens, passwords) are stripped first. Only run `predict` on code you trust.
