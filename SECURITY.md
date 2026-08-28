# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

Please report security issues privately to the repository owner. Do not open a public issue containing secrets, exploit details, or customer document content.

Expected response time is 5 business days.

## Secret Handling

- Never commit `.env`.
- Never place API keys in source code, tests, logs, reports, or GitHub Actions logs.
- The SDK accepts DeepSeek credentials only through explicit constructor arguments or process environment variables.
- CLI `.env` support is optional and intended for local use only.

## Distribution Safety

The SDK is designed to keep the following out of wheel and sdist artifacts:

- `.env`
- API keys
- generated output directories
- private Markdown fixtures
- virtual environments and caches
