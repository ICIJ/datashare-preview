# Datashare Preview

[![CI](https://github.com/ICIJ/datashare-preview/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/ICIJ/datashare-preview/actions/workflows/main.yml)

This is an application that will take documents hashes/routing information as input and serve previews/thumbnails for these documents.

It will cache the previews to avoid reprocessing images for each request.

## Develop

Install system dependencies once and for all:

```
make install_dependencies
```

To develop, [install Poetry](https://python-poetry.org/docs/#installation) then just run:

```
make install
make test
```

To run the server:

```
make run
```

## Release

Releases are automated, nothing has to be run by hand.

Every push runs the [CI workflow](.github/workflows/main.yml). When that run is on `main` and it passes, it triggers the [Release workflow](.github/workflows/release.yml), which:

1. Works out the next version from the commit messages with [Python Semantic Release](https://python-semantic-release.readthedocs.io/), bumps `pyproject.toml`, updates `CHANGELOG.md`, commits, tags and creates the GitHub release.
2. Builds the `linux/amd64` and `linux/arm64` images from the new tag and pushes them to [Docker Hub](https://hub.docker.com/r/icij/datashare-preview), as `:<version>` and `:latest`.

Step 2 only runs when step 1 actually produced a version. The whole workflow is skipped outside the `ICIJ/datashare-preview` repository, so forks never publish.

What decides the version is the commit subject, which follows [Conventional Commits](https://www.conventionalcommits.org/):

| Commit subject | Release |
| --- | --- |
| `fix: ...` or `perf: ...` | patch |
| `feat: ...` | minor |
| `feat!: ...`, or any commit with a `BREAKING CHANGE:` footer | major |
| `build:`, `chore:`, `ci:`, `docs:`, `refactor:`, `style:`, `test:` | none |

Follow the run on the [Actions tab](https://github.com/ICIJ/datashare-preview/actions/workflows/release.yml). When no commit calls for a release, the workflow succeeds and publishes nothing. You can also start it by hand from that page ("Run workflow"), which always releases from `main`.

### Manual fallback

If the workflow is unavailable, you can publish from your machine. This requires being a member of the ICIJ organization on Docker Hub.

Bump the version and tag it (pick one, following [semver](https://semver.org/)):

```
make patch
make minor
make major
```

To set a specific version use this command:

```
make set_version CURRENT_VERSION=X.Y.Z
```

Build the Docker image and publish it on Docker Hub:

```
make docker-publish
```

Datashare Preview is a multi-platform build. You might need to set up your environment for multi-platform builds with `make docker-setup-multiarch`. Read more [in the Docker documentation](https://docs.docker.com/build/building/multi-platform/).
