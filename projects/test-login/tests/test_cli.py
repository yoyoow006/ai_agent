import contextlib
import io
import unittest

from cli import run_demo


class CliTests(unittest.TestCase):
    def test_auto_demo_completes_login_without_printing_the_password(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = run_demo(auto=True)

        rendered = output.getvalue()
        self.assertEqual(status, 0)
        self.assertIn("Login successful", rendered)
        self.assertIn("Session token:", rendered)
        self.assertNotIn("CorrectHorse42", rendered)

    def test_reject_demo_fails_safely_without_printing_password_or_code(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = run_demo(auto=True, reject=True)

        rendered = output.getvalue()
        self.assertNotEqual(status, 0)
        self.assertIn("Verification failed", rendered)
        self.assertNotIn("CorrectHorse42", rendered)
        self.assertNotIn("code:", rendered.lower())


if __name__ == "__main__":
    unittest.main()
