"""Environment smoke test.

This is NOT part of the functional test suite. It exists only to confirm that
Playwright, pytest-playwright, the Chromium browser and the target application
are all wired up correctly. The real tests are generated later by the
Playwright Test Agents (planner -> generator -> healer).
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_home_page_loads(page: Page, base_url: str) -> None:
    """The playground home page loads and shows its list of scenarios."""
    page.goto(base_url)

    expect(page).to_have_title("UI Test Automation Playground")
    # Every scenario on the home page is a link; at least a few must exist.
    expect(page.get_by_role("link", name="Dynamic ID")).to_be_visible()
    expect(page.get_by_role("link", name="Click", exact=True)).to_be_visible()
    expect(page.get_by_text("This work is licensed under the Apache License 2.0.")).to_be_visible()
    
