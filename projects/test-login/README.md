# Test Login Project

This is a deliberately small, offline Python 3.8 project for exercising:

- in-memory user registration;
- salted PBKDF2-HMAC-SHA256 password verification;
- a cryptographically random six-digit verification code;
- a 300-second, five-attempt, one-time verification challenge;
- a random session token after both factors succeed.

## Run the tests

```bash
cd projects/test-login
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
```

## Run the demo

Interactive local demonstration:

```bash
python3 cli.py demo
```

Automatic successful demonstration:

```bash
python3 cli.py demo --auto
```

Failure path with an intentionally wrong verification code:

```bash
python3 cli.py demo --auto --reject
```

The failure command intentionally exits with a non-zero status.

## Boundaries

This project uses only the Python standard library and keeps all state in memory. It does not use a database, network, SMS gateway, email provider, persistent session store, or external identity provider.

The implementation is for local testing and is not production-ready. A production service would also need secure code delivery, rate limiting and lockout policies, persistent credential storage, session revocation, auditing, monitoring, recovery flows, and deployment security review.
