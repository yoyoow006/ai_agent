"""Command-line entry points for the local login demonstration."""

from __future__ import annotations

import argparse
from typing import List, Optional

from login_service import (
    AuthenticationError,
    LoginService,
    VerificationDelivery,
    VerificationError,
)


_DEMO_USERNAME = "example"
_DEMO_PASSWORD = "CorrectHorse42"


def run_demo(*, auto: bool = False, reject: bool = False) -> int:
    """Run one in-process registration and two-step login demonstration."""

    delivered: List[VerificationDelivery] = []

    if auto:
        delivery = delivered.append
    else:

        def delivery(message: VerificationDelivery) -> None:
            print(f"Verification code for {message.username}: {message.code}")

    service = LoginService(delivery=delivery)
    service.register(_DEMO_USERNAME, _DEMO_PASSWORD)
    challenge_id = service.begin_login(_DEMO_USERNAME, _DEMO_PASSWORD)

    if auto:
        if not delivered:
            print("Verification failed")
            return 1
        code = delivered[-1].code
        if reject:
            code = "000000" if code != "000000" else "111111"
    else:
        code = input("Verification code: ")

    try:
        token = service.complete_login(challenge_id, code)
    except (AuthenticationError, VerificationError):
        print("Verification failed")
        return 1

    print("Login successful")
    print(f"Session token: {token}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Local login verification demo")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run one local login demonstration")
    demo.add_argument("--auto", action="store_true", help="use the in-memory delivery channel")
    demo.add_argument(
        "--reject",
        action="store_true",
        help="intentionally submit an incorrect verification code",
    )
    arguments = parser.parse_args(argv)

    if arguments.command == "demo":
        return run_demo(auto=arguments.auto, reject=arguments.reject)
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
