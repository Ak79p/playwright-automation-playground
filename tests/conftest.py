"""Shared pytest fixtures for the uitestingplayground.com test suite.

pytest-playwright already provides the core fixtures used by every test:
  - ``page``          : a fresh Playwright ``Page`` per test (new browser context)
  - ``base_url``      : taken from ``--base-url`` in pytest.ini
  - ``browser_name``  : from ``--browser`` (chromium by default)

Add project-wide fixtures here (e.g. page objects, test data) rather than in
individual test modules.
"""

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Default context settings applied to every test.

    Overrides pytest-playwright's ``browser_context_args`` so all tests share a
    consistent viewport. Extend this dict to add locale, timezone, permissions, etc.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }
