# 📦 Versioning Guidelines

We follow [Semantic Versioning](https://semver.org/) in this project: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes or incompatible API modifications
- `MINOR`: New features, backward-compatible
- `PATCH`: Bug fixes or internal improvements

## Examples
- `1.0.0`: Initial stable release
- `1.1.0`: Added LLM-powered book recommendations
- `1.1.1`: Fixed review filtering bug

## How to bump version
1. Update the `VERSION` file
2. Add a line in `CHANGELOG.md` if needed
3. Commit with message: `chore(version): bump to x.y.z`