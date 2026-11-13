"""Read-only gh client: empty pages, auth failure, and HTTP 429."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import github_read  # noqa: E402


def _proc(returncode, stdout, stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class GithubReadTests(unittest.TestCase):
    def test_empty_page_is_success_not_an_error(self):
        def runner(args):
            self.assertEqual(args[4], "GET")
            self.assertIn("--method", args)
            self.assertNotIn("POST", args)
            return _proc(0, "HTTP/2.0 200 OK\nX-RateLimit-Remaining: 10\n\n[]\n")

        result = github_read.fetch_json(
            "repos/example/example/issues?per_page=100",
            runner=runner,
            sleeper=lambda _delay: None,
            paginate=True,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data, [])
        self.assertEqual(result.rate_limit_remaining, 10)

    def test_auth_failure_is_not_retried(self):
        calls = []

        def runner(args):
            calls.append(args)
            return _proc(4, "", "please run gh auth login")

        result = github_read.gh_get(
            "rate_limit",
            runner=runner,
            sleeper=lambda _delay: calls.append("sleep"),
            max_attempts=4,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.detail, "gh auth failed")
        self.assertEqual(len(calls), 1)
        self.assertNotIn("sleep", calls)

    def test_http_429_backs_off_four_times_then_fails(self):
        calls = []
        sleeps = []

        def runner(args):
            calls.append(args)
            return _proc(1, "HTTP/2.0 429 Too Many Requests\n\n{\"message\":\"rate limit\"}\n")

        result = github_read.gh_get(
            "rate_limit",
            runner=runner,
            sleeper=sleeps.append,
            max_attempts=4,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.status, 429)
        self.assertEqual(result.detail, "HTTP 429")
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [1, 2, 4])

    def test_http_403_uses_the_same_backoff_budget(self):
        sleeps = []

        def runner(_args):
            return _proc(1, "HTTP/2.0 403 Forbidden\n\n{\"message\":\"secondary\"}\n")

        result = github_read.gh_get(
            "rate_limit",
            runner=runner,
            sleeper=sleeps.append,
            max_attempts=4,
        )
        self.assertEqual(result.detail, "HTTP 403")
        self.assertEqual(len(sleeps), 3)


if __name__ == "__main__":
    unittest.main()
