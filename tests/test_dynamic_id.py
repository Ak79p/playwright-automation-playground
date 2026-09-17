# spec: specs/dynamic-id.md
# section: Dynamic ID
"""Tests for http://www.uitestingplayground.com/dynamicid

The button on this page gets a fresh, random id on every page load. All tests locate it with the
stable role + accessible-name locator; the id is never hardcoded (scenario 1.5 reads it at runtime only
to prove that an id-based locator breaks after a reload).
"""

from playwright.sync_api import Page, expect

BUTTON_NAME = "Button with Dynamic ID"


def test_button_visible_and_enabled_with_stable_name(page: Page, base_url: str) -> None:
    """1.1 Button is visible and enabled with a stable accessible name"""
    # 1. Navigate to http://www.uitestingplayground.com/dynamicid.
    page.goto(f"{base_url}/dynamicid")

    # 2. Locate the button using get_by_role("button", name="Button with Dynamic ID").
    button = page.get_by_role("button", name=BUTTON_NAME)

    # Expected: the button is visible.
    expect(button).to_be_visible()

    # Expected: the button is enabled (not disabled).
    expect(button).to_be_enabled()

    # Expected: the button's accessible name is exactly "Button with Dynamic ID".
    expect(button).to_have_accessible_name(BUTTON_NAME)

    # Expected: the button's class attribute contains btn and btn-primary.
    expect(button).to_have_class("btn btn-primary")


def test_click_button_succeeds_without_side_effects(page: Page, base_url: str) -> None:
    """1.2 Clicking the button succeeds without side effects"""
    # 1. Navigate to http://www.uitestingplayground.com/dynamicid.
    page.goto(f"{base_url}/dynamicid")

    # Listeners are attached after the initial load so only click-caused errors/dialogs are counted
    # (the page itself logs an unrelated console error on load).
    console_errors = []
    dialogs = []
    page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
    page.on("dialog", lambda dialog: (dialogs.append(dialog), dialog.dismiss()))

    # 2. Locate the button by role "button" and name "Button with Dynamic ID".
    button = page.get_by_role("button", name=BUTTON_NAME)

    # 3. Click the button.
    button.click()

    # Expected: the click completes without throwing an error or timing out, and the URL is unchanged.
    expect(page).to_have_url(f"{base_url}/dynamicid")

    # Expected: no JavaScript error is logged to the console as a result of the click.
    assert console_errors == []

    # Expected: no dialog (alert/confirm/prompt) appears.
    assert dialogs == []

    # Expected: the button is still visible and enabled immediately after the click.
    expect(button).to_be_visible()
    expect(button).to_be_enabled()


def test_button_id_differs_between_page_loads(page: Page, base_url: str) -> None:
    """1.3 Button id differs between two page loads"""
    # 1. Navigate to http://www.uitestingplayground.com/dynamicid.
    page.goto(f"{base_url}/dynamicid")

    # 2. Read the id attribute of the button located by role/name; store it as first_id.
    button = page.get_by_role("button", name=BUTTON_NAME)
    expect(button).to_be_visible()
    first_id = button.get_attribute("id")

    # 3. Navigate to the same URL again (fresh page load, not a soft reload via history).
    page.goto(f"{base_url}/dynamicid")

    # 4. Read the id attribute of the button on the reloaded page; store it as second_id.
    button = page.get_by_role("button", name=BUTTON_NAME)
    expect(button).to_be_visible()
    second_id = button.get_attribute("id")

    # Expected: first_id and second_id are both non-empty strings.
    assert first_id
    assert second_id

    # Expected: first_id is not equal to second_id.
    assert first_id != second_id

    # Expected: on both loads the accessible role stays "button" and the name stays "Button with Dynamic ID".
    expect(button).to_have_accessible_name(BUTTON_NAME)


def test_stable_locator_resolves_after_reload(page: Page, base_url: str) -> None:
    """1.4 Stable role/name locator still resolves after a reload"""
    # 1. Navigate to http://www.uitestingplayground.com/dynamicid.
    page.goto(f"{base_url}/dynamicid")

    # 2. Confirm the button located by role "button" and name "Button with Dynamic ID" is visible.
    button = page.get_by_role("button", name=BUTTON_NAME)
    expect(button).to_have_count(1)
    expect(button).to_be_visible()

    # 3. Reload the page (navigate to the same URL again).
    page.goto(f"{base_url}/dynamicid")

    # 4. Using the same role+name locator, locate the button again - do not capture or reuse any id.
    button = page.get_by_role("button", name=BUTTON_NAME)

    # Expected: the locator resolves to exactly one element after the reload.
    expect(button).to_have_count(1)

    # Expected: the button is visible and enabled after the reload.
    expect(button).to_be_visible()
    expect(button).to_be_enabled()

    # Expected: clicking the button after the reload succeeds without error.
    button.click()
    expect(button).to_be_visible()


def test_previous_id_locator_does_not_resolve_after_reload(page: Page, base_url: str) -> None:
    """1.5 Negative check: a locator built from a previously observed id does not resolve after reload"""
    # 1. Navigate to http://www.uitestingplayground.com/dynamicid.
    page.goto(f"{base_url}/dynamicid")

    # 2. Read the current id attribute of the button located by role/name and store it at runtime.
    button = page.get_by_role("button", name=BUTTON_NAME)
    observed_id = button.get_attribute("id")

    # 3. Build a CSS locator at runtime using that stored id value (never a literal). An attribute selector
    #    is used instead of "#id" because "#..." is invalid CSS when the generated id starts with a digit.
    id_locator = page.locator(f'[id="{observed_id}"]')

    # 4. Confirm this id-based locator resolves to the button on the current page.
    expect(id_locator).to_have_count(1)

    # 5. Reload the page (navigate to the same URL again).
    page.goto(f"{base_url}/dynamicid")

    # 6. Without changing the locator string, try the same id-based locator built from the previous load's id.
    expect(id_locator).to_have_count(0)
