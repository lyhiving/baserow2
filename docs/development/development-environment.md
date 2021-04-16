# Baserow's dev environment

- See [running the dev environment](../guides/running-the-dev-environment.md) for a
  step-by-step guide on how to set-up the dev env.
- See [baserow docker api](../reference/baserow-docker-api.md) for more detail on how
  Baserow's docker setup can be used and configured.
- See [dev.sh](../development/dev_sh.md) for further detail on the CLI tool for managing
  the dev environment.
- See [contributing](../development/CONTRIBUTING.md) for info on how to get started contributing
  to baserow.

## Fixing git blame

A large formatting only commit was made to the repo when we converted to use the black
auto-formatter on April, 12 2021. If you don't want to see this commit in git blame, you
can run the command below to get your local git to ignore that commit in blame for this
repo:

```bash
$ git config blame.ignoreRevsFile .git-blame-ignore-revs
```
