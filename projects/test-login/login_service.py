"""In-memory login and random verification demonstration service."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import re
import secrets
import time
from typing import Callable, Dict, Optional


_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
_VERIFICATION_CODE_PATTERN = re.compile(r"^[0-9]{6}$")
_CHALLENGE_LIFETIME_SECONDS = 300
_MAX_VERIFICATION_ATTEMPTS = 5


class LoginError(RuntimeError):
    """Base class for safe login failures."""


class RegistrationError(LoginError, ValueError):
    """The requested account cannot be registered."""


class AuthenticationError(LoginError):
    """A username or password is invalid."""


class VerificationError(LoginError):
    """A verification challenge is invalid, expired, or exhausted."""


@dataclass(frozen=True)
class VerificationDelivery:
    username: str
    code: str

    def __repr__(self) -> str:
        return f"VerificationDelivery(username={self.username!r}, code=<redacted>)"


@dataclass(frozen=True)
class _UserRecord:
    username: str
    salt: bytes
    iterations: int
    password_hash: bytes

    def __repr__(self) -> str:
        return (
            f"_UserRecord(username={self.username!r}, salt=<redacted>, "
            f"iterations={self.iterations}, password_hash=<redacted>)"
        )


@dataclass
class _Challenge:
    username: str
    code: str
    expires_at: float
    attempts: int = 0

    def __repr__(self) -> str:
        return (
            f"_Challenge(username={self.username!r}, code=<redacted>, "
            f"expires_at={self.expires_at!r}, attempts={self.attempts})"
        )


def generate_verification_code() -> str:
    """Return a cryptographically random six-digit verification code."""

    return f"{secrets.randbelow(1_000_000):06d}"


def _generate_challenge_id() -> str:
    return secrets.token_urlsafe(24)


def _generate_session_token() -> str:
    return secrets.token_urlsafe(32)


class LoginService:
    """A small in-memory service for local two-step login demonstrations."""

    def __init__(
        self,
        *,
        clock: Optional[Callable[[], float]] = None,
        delivery: Optional[Callable[[VerificationDelivery], None]] = None,
        code_generator: Optional[Callable[[], str]] = None,
        challenge_generator: Optional[Callable[[], str]] = None,
        token_generator: Optional[Callable[[], str]] = None,
        pbkdf2_iterations: int = 100_000,
    ) -> None:
        if pbkdf2_iterations < 1:
            raise ValueError("pbkdf2_iterations must be positive")

        self._clock = clock if clock is not None else time.monotonic
        self._delivery = delivery if delivery is not None else self._ignore_delivery
        self._code_generator = (
            code_generator if code_generator is not None else generate_verification_code
        )
        self._challenge_generator = (
            challenge_generator
            if challenge_generator is not None
            else _generate_challenge_id
        )
        self._token_generator = (
            token_generator
            if token_generator is not None
            else _generate_session_token
        )
        self._pbkdf2_iterations = pbkdf2_iterations
        self._users: Dict[str, _UserRecord] = {}
        self._challenges: Dict[str, _Challenge] = {}
        self._active_tokens: set[str] = set()
        self._dummy_salt = secrets.token_bytes(16)

    @staticmethod
    def _ignore_delivery(delivery: VerificationDelivery) -> None:
        return None

    def _remove_expired_challenges(self) -> None:
        now = self._clock()
        expired_challenge_ids = [
            challenge_id
            for challenge_id, challenge in self._challenges.items()
            if now >= challenge.expires_at
        ]
        for challenge_id in expired_challenge_ids:
            del self._challenges[challenge_id]

    @staticmethod
    def _password_bytes(password: str) -> bytes:
        return password.encode("utf-8")

    def _password_hash(
        self, password: str, salt: bytes, iterations: int
    ) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            self._password_bytes(password),
            salt,
            iterations,
        )

    @staticmethod
    def _valid_username(username: str) -> bool:
        return (
            isinstance(username, str)
            and _USERNAME_PATTERN.fullmatch(username) is not None
        )

    @staticmethod
    def _valid_password(password: str) -> bool:
        return (
            isinstance(password, str)
            and 10 <= len(password) <= 128
            and any(character.isalpha() for character in password)
            and any(character.isdigit() for character in password)
        )

    def register(self, username: str, password: str) -> None:
        """Register an in-memory user with a salted password hash."""

        if not self._valid_username(username):
            raise RegistrationError("username is invalid")
        if not self._valid_password(password):
            raise RegistrationError("password is too weak")
        if username in self._users:
            raise RegistrationError("username is already registered")

        salt = secrets.token_bytes(16)
        password_hash = self._password_hash(
            password, salt, self._pbkdf2_iterations
        )
        self._users[username] = _UserRecord(
            username=username,
            salt=salt,
            iterations=self._pbkdf2_iterations,
            password_hash=password_hash,
        )

    def begin_login(self, username: str, password: str) -> str:
        """Check credentials and deliver a one-time random verification code."""

        record = (
            self._users.get(username)
            if isinstance(username, str)
            else None
        )
        if record is None:
            candidate = self._password_hash(
                password if isinstance(password, str) else "",
                self._dummy_salt,
                self._pbkdf2_iterations,
            )
            valid_password = False
        else:
            candidate = self._password_hash(
                password if isinstance(password, str) else "",
                record.salt,
                record.iterations,
            )
            valid_password = hmac.compare_digest(
                candidate, record.password_hash
            )

        if not valid_password:
            raise AuthenticationError("username or password is incorrect")

        self._remove_expired_challenges()

        while True:
            challenge_id = self._challenge_generator()
            if challenge_id and challenge_id not in self._challenges:
                break

        code = self._code_generator()
        if (
            not isinstance(code, str)
            or _VERIFICATION_CODE_PATTERN.fullmatch(code) is None
        ):
            raise VerificationError("verification code is invalid")

        delivery = VerificationDelivery(username=username, code=code)
        self._delivery(delivery)
        self._challenges[challenge_id] = _Challenge(
            username=username,
            code=code,
            expires_at=self._clock() + _CHALLENGE_LIFETIME_SECONDS,
        )
        return challenge_id

    def complete_login(self, challenge_id: str, code: str) -> str:
        """Complete login with an unexpired, unconsumed verification code."""

        challenge = self._challenges.get(challenge_id)
        if challenge is None:
            raise VerificationError("verification code is invalid or expired")

        if self._clock() >= challenge.expires_at:
            del self._challenges[challenge_id]
            raise VerificationError("verification code is invalid or expired")

        correct = (
            isinstance(code, str)
            and _VERIFICATION_CODE_PATTERN.fullmatch(code) is not None
            and hmac.compare_digest(code, challenge.code)
        )
        if not correct:
            challenge.attempts += 1
            if challenge.attempts >= _MAX_VERIFICATION_ATTEMPTS:
                del self._challenges[challenge_id]
            raise VerificationError("verification code is invalid or expired")

        del self._challenges[challenge_id]
        while True:
            token = self._token_generator()
            if isinstance(token, str) and token and token not in self._active_tokens:
                break

        self._active_tokens.add(token)
        return token

    def validate_token(self, token: str) -> bool:
        """Return whether a token was issued by this service instance."""

        return isinstance(token, str) and token in self._active_tokens
