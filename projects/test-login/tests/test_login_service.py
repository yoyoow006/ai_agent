import re
import hashlib
import unittest
from unittest import mock

import login_service
from login_service import (
    AuthenticationError,
    LoginService,
    RegistrationError,
    VerificationDelivery,
    VerificationError,
    generate_verification_code,
)


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class CapturingDelivery:
    def __init__(self):
        self.deliveries = []

    def __call__(self, delivery):
        if not isinstance(delivery, VerificationDelivery):
            raise TypeError("delivery channel received an invalid object")
        self.deliveries.append(delivery)


class LoginServiceTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.delivery = CapturingDelivery()
        self.service = LoginService(
            clock=self.clock,
            delivery=self.delivery,
            pbkdf2_iterations=1_000,
        )

    def register_user(self, username="example", password="ValidPassword123"):
        self.service.register(username, password)
        return username, password

    def test_register_rejects_invalid_usernames_weak_and_duplicate_users(self):
        with self.assertRaises(RegistrationError):
            self.service.register("a", "ValidPassword123")
        with self.assertRaises(RegistrationError):
            self.service.register("invalid user", "ValidPassword123")
        with self.assertRaises(RegistrationError):
            self.service.register("example", "short")
        with self.assertRaises(RegistrationError):
            self.service.register("example", "1234567890")

        self.register_user()
        with self.assertRaises(RegistrationError):
            self.service.register("example", "DifferentPassword123")

    def test_password_is_stored_with_unique_random_salt_and_pbkdf2_parameters(self):
        self.register_user("first", "ValidPassword123")
        self.register_user("second", "OtherValidPassword123")

        records = [self.service._users[name] for name in ("first", "second")]
        self.assertNotEqual(records[0].salt, records[1].salt)
        self.assertNotEqual(records[0].password_hash, records[1].password_hash)
        for record in records:
            self.assertEqual(len(record.salt), 16)
            self.assertGreaterEqual(record.iterations, 1_000)
            self.assertNotEqual(record.password_hash, b"ValidPassword123")
            self.assertNotEqual(record.password_hash, b"OtherValidPassword123")

    def test_password_hash_uses_pbkdf2_hmac_sha256_with_configured_iterations(self):
        original_digest = login_service.hashlib.pbkdf2_hmac

        with mock.patch.object(
            login_service.hashlib,
            "pbkdf2_hmac",
            wraps=original_digest,
        ) as pbkdf2:
            self.service.register("example", "ValidPassword123")

        self.assertEqual(pbkdf2.call_count, 1)
        self.assertEqual(
            pbkdf2.call_args[0],
            ("sha256", b"ValidPassword123", mock.ANY, 1_000),
        )

        record = self.service._users["example"]
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256", b"ValidPassword123", record.salt, 1_000
        )
        self.assertEqual(record.password_hash, expected_hash)

    def test_salts_come_from_secure_random_bytes_of_sixteen_bytes(self):
        dummy_salt = b"a" * 16
        user_salt = b"b" * 16

        with mock.patch(
            "login_service.secrets.token_bytes",
            side_effect=[dummy_salt, user_salt],
        ) as token_bytes:
            service = LoginService(
                clock=self.clock,
                delivery=self.delivery,
                pbkdf2_iterations=1_000,
            )
            service.register("example", "ValidPassword123")

        self.assertEqual(token_bytes.call_args_list, [mock.call(16), mock.call(16)])
        self.assertEqual(service._dummy_salt, dummy_salt)
        self.assertEqual(service._users["example"].salt, user_salt)

    def test_default_pbkdf2_iterations_are_at_least_one_hundred_thousand(self):
        original_digest = login_service.hashlib.pbkdf2_hmac

        with mock.patch.object(
            login_service.hashlib,
            "pbkdf2_hmac",
            wraps=original_digest,
        ) as pbkdf2:
            service = LoginService(clock=self.clock, delivery=self.delivery)
            service.register("example", "ValidPassword123")

        self.assertEqual(pbkdf2.call_args[0][3], 100_000)

    def test_unknown_user_performs_one_equal_parameter_dummy_pbkdf2_calculation(self):
        original_digest = login_service.hashlib.pbkdf2_hmac

        with mock.patch.object(
            login_service.hashlib,
            "pbkdf2_hmac",
            wraps=original_digest,
        ) as pbkdf2:
            with self.assertRaises(AuthenticationError):
                self.service.begin_login("missing", "ValidPassword123")

        self.assertEqual(pbkdf2.call_count, 1)
        self.assertEqual(
            pbkdf2.call_args[0],
            ("sha256", b"ValidPassword123", self.service._dummy_salt, 1_000),
        )

    def test_password_comparison_is_delegated_to_constant_time_compare(self):
        self.register_user()

        with mock.patch(
            "login_service.hmac.compare_digest", return_value=False
        ) as compare_digest:
            with self.assertRaises(AuthenticationError):
                self.service.begin_login("example", "ValidPassword123")

        compare_digest.assert_called_once()

    def test_unknown_user_and_wrong_password_have_the_same_safe_failure(self):
        username, password = self.register_user()

        with self.assertRaises(AuthenticationError) as unknown:
            self.service.begin_login("missing", password)
        with self.assertRaises(AuthenticationError) as wrong_password:
            self.service.begin_login(username, "WrongPassword123")

        self.assertIs(type(unknown.exception), type(wrong_password.exception))
        self.assertEqual(str(unknown.exception), str(wrong_password.exception))
        self.assertEqual(self.delivery.deliveries, [])
        self.assertEqual(self.service._challenges, {})

    def test_non_string_and_unhashable_usernames_use_the_same_safe_failure(self):
        self.register_user()

        for username in (None, [], {}):
            with self.assertRaises(AuthenticationError) as caught:
                self.service.begin_login(username, "ValidPassword123")
            self.assertEqual(
                str(caught.exception), "username or password is incorrect"
            )

        self.assertEqual(self.delivery.deliveries, [])
        self.assertEqual(self.service._challenges, {})

    def test_verification_code_is_six_digits_and_uses_secure_random_source(self):
        with mock.patch("login_service.secrets.randbelow", return_value=42) as random_source:
            self.assertEqual(generate_verification_code(), "000042")

        random_source.assert_called_once_with(1_000_000)
        codes = {generate_verification_code() for _ in range(100)}
        self.assertGreater(len(codes), 1)
        self.assertTrue(all(re.fullmatch(r"[0-9]{6}", code) for code in codes))

    def begin_challenge(self):
        username, password = self.register_user()
        challenge_id = self.service.begin_login(username, password)
        self.assertEqual(len(self.delivery.deliveries), 1)
        return challenge_id, self.delivery.deliveries[0].code

    def test_correct_code_returns_a_valid_one_time_session_token(self):
        challenge_id, code = self.begin_challenge()

        token = self.service.complete_login(challenge_id, code)

        self.assertTrue(token)
        self.assertTrue(self.service.validate_token(token))
        self.assertFalse(self.service.validate_token("not-a-real-token"))
        with self.assertRaises(VerificationError):
            self.service.complete_login(challenge_id, code)

    def test_default_challenge_ids_and_session_tokens_use_secure_urlsafe_tokens(self):
        with mock.patch(
            "login_service.secrets.token_urlsafe",
            side_effect=["challenge-id", "session-token"],
        ) as token_urlsafe:
            service = LoginService(
                clock=self.clock,
                delivery=self.delivery,
                pbkdf2_iterations=1_000,
            )
            service.register("example", "ValidPassword123")
            challenge_id = service.begin_login("example", "ValidPassword123")
            token = service.complete_login(
                challenge_id, self.delivery.deliveries[-1].code
            )

        self.assertEqual(challenge_id, "challenge-id")
        self.assertEqual(token, "session-token")
        self.assertEqual(
            token_urlsafe.call_args_list,
            [mock.call(24), mock.call(32)],
        )

    def test_wrong_codes_are_limited_and_then_challenge_is_invalidated(self):
        challenge_id, code = self.begin_challenge()
        wrong_code = "000000" if code != "000000" else "111111"

        for _ in range(4):
            with self.assertRaises(VerificationError):
                self.service.complete_login(challenge_id, wrong_code)

        self.assertIn(challenge_id, self.service._challenges)
        with self.assertRaises(VerificationError):
            self.service.complete_login(challenge_id, wrong_code)
        self.assertNotIn(challenge_id, self.service._challenges)

        with self.assertRaises(VerificationError):
            self.service.complete_login(challenge_id, code)

    def test_challenge_expires_after_300_seconds(self):
        challenge_id, code = self.begin_challenge()
        self.clock.advance(300)

        with self.assertRaises(VerificationError):
            self.service.complete_login(challenge_id, code)
        self.assertNotIn(challenge_id, self.service._challenges)

    def test_expired_unused_challenges_are_cleaned_by_later_login_activity(self):
        username, password = self.register_user()
        expired_challenge_id = self.service.begin_login(username, password)
        self.clock.advance(300)

        active_challenge_id = self.service.begin_login(username, password)

        self.assertNotIn(expired_challenge_id, self.service._challenges)
        self.assertIn(active_challenge_id, self.service._challenges)
        self.assertEqual(set(self.service._challenges), {active_challenge_id})

    def test_active_challenge_repr_does_not_expose_the_verification_code(self):
        challenge_id, code = self.begin_challenge()

        rendered = repr(self.service._challenges[challenge_id])

        self.assertNotIn(code, rendered)
        self.assertIn("code=<redacted>", rendered)


if __name__ == "__main__":
    unittest.main()
