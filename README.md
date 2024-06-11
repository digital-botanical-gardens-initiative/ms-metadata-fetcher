# ms-metadata-fetcher

[![Release](https://img.shields.io/github/v/release/edouardbruelhart/ms-metadata-fetcher)](https://img.shields.io/github/v/release/edouardbruelhart/ms-metadata-fetcher)
[![Build status](https://img.shields.io/github/actions/workflow/status/edouardbruelhart/ms-metadata-fetcher/main.yml?branch=main)](https://github.com/edouardbruelhart/ms-metadata-fetcher/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/edouardbruelhart/ms-metadata-fetcher/branch/main/graph/badge.svg)](https://codecov.io/gh/edouardbruelhart/ms-metadata-fetcher)
[![Commit activity](https://img.shields.io/github/commit-activity/m/edouardbruelhart/ms-metadata-fetcher)](https://img.shields.io/github/commit-activity/m/edouardbruelhart/ms-metadata-fetcher)
[![License](https://img.shields.io/github/license/edouardbruelhart/ms-metadata-fetcher)](https://img.shields.io/github/license/edouardbruelhart/ms-metadata-fetcher)

A script to retrieve MS data and the associated metadata

- **Github repository**: <https://github.com/edouardbruelhart/ms-metadata-fetcher/>
- **Documentation** <https://edouardbruelhart.github.io/ms-metadata-fetcher/>

## Running the fetcher

Move to `ms_metadata_fetcher` directory

```bash
cd ms_metadata_fetcher
```

Make sure that the .env is present (you have an example with `.env.example`)

And run the following command:

```bash
./launcher.sh
```

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:edouardbruelhart/ms-metadata-fetcher.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPi or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
