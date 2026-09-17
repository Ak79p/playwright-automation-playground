"""End-to-end tests for every scenario listed on http://www.uitestingplayground.com/

Each test starts on the home page (see ``goto_home``), follows the scenario link and
exercises the page the way the playground describes it.
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def goto_home(page: Page, base_url: str) -> None:
    page.goto(base_url)


def test_run(page: Page) -> None:
    title = page.title()
    assert title == "UI Test Automation Playground"
    page.get_by_role("link", name="Dynamic ID").click()
    expect(page.get_by_role("button", name="Button with Dynamic ID")).to_be_visible()


def test_class_attribute(page: Page) -> None:
    page.get_by_role("link", name="Class Attribute").click()
    page.on("dialog", lambda dialog: dialog.accept())
    page.locator("//button[contains(@class,'btn-primary')]").click()
    expect(page.locator("//button[contains(@class,'btn-primary')]")).to_be_visible()


def test_hidden_layers(page: Page) -> None:
    page.get_by_role("link", name="Hidden Layers").click()
    green = page.locator("#greenButton")
    green.click()
    # After the first click a blue button is layered on top, so the green one is not clickable.
    expect(page.locator("#blueButton")).to_be_visible()
    with pytest.raises(Exception):
        green.click(timeout=2000)


def test_load_delay(page: Page) -> None:
    """Additionaly you could also do this:
    page.goto("https://example.com",wait_until="load")"""
    page.get_by_role("link", name="Load Delay").click()
    page.get_by_role("button", name="Button Appearing After Delay").wait_for(state="visible")
    expect(page.get_by_role("button", name="Button Appearing After Delay")).to_be_visible()


def test_ajax_data(page: Page) -> None:
    page.get_by_role("link", name="AJAX Data").click()
    page.get_by_role("button", name="Button Triggering AJAX Request").click()
    page.locator(".bg-success").wait_for(state="visible", timeout=20000)
    expect(page.locator(".bg-success")).to_contain_text("Data loaded with AJAX get request.")


def test_client_side_delay(page: Page) -> None:
    page.get_by_role("link", name="Client Side Delay").click()
    page.get_by_role("button", name="Button Triggering Client Side Logic").click()
    page.locator(".bg-success").wait_for(state="visible", timeout=20000)
    expect(page.locator(".bg-success")).to_contain_text("Data calculated on the client side.")


def test_click(page: Page) -> None:
    page.get_by_role("link", name="Click", exact=True).click()
    button = page.locator("#badButton")
    button.click()  # Playwright emulates a real mouse click, which this button accepts
    expect(button).to_have_class(re.compile(r"btn-success"))


def test_text_input(page: Page) -> None:
    page.get_by_role("link", name="Text Input").click()
    button = page.locator("#updatingButton")
    expect(button).to_be_visible()
    page.get_by_placeholder("MyButton").fill("Test User")
    button.click()
    expect(page.locator("#updatingButton")).to_contain_text("Test User")


def test_scrollbars(page: Page) -> None:
    page.get_by_role("link", name="Scrollbars").click()
    expect(page.get_by_role("button", name="Hiding Button")).not_to_be_in_viewport()
    page.get_by_role("button", name="Hiding Button").scroll_into_view_if_needed()
    expect(page.get_by_role("button", name="Hiding Button")).to_be_in_viewport()


def test_dynamic_table(page: Page) -> None:
    """Column order changes on every load, so the CPU column index is resolved at runtime."""
    page.get_by_role("link", name="Dynamic Table").click()
    table = page.get_by_role("table")
    expect(table.get_by_role("columnheader", name="CPU")).to_be_visible()  # table is rendered by JS
    headers = [h.strip() for h in table.get_by_role("columnheader").all_inner_texts()]
    cpu_index = headers.index("CPU")

    chrome_row = table.get_by_role("row").filter(has=page.get_by_role("cell", name="Chrome", exact=True))
    chrome_cpu = chrome_row.get_by_role("cell").nth(cpu_index).inner_text().strip()

    assert re.fullmatch(r"\d+(\.\d+)?%", chrome_cpu), f"unexpected CPU value: {chrome_cpu!r}"
    expect(page.locator(".bg-warning")).to_have_text(f"Chrome CPU: {chrome_cpu}")


def test_verify_text(page: Page) -> None:
    page.get_by_role("link", name="Verify Text").click()
    # Text is split across elements and contains non-breaking spaces; normalized matching handles it.
    # A decoy "Welcome..." badge exists too, so match the full normalized text exactly.
    expect(page.get_by_text("Welcome UserName!", exact=True)).to_be_visible()
    expect(page.locator(".bg-primary")).to_contain_text("Welcome UserName!")


def test_progress_bar(page: Page) -> None:
    page.get_by_role("link", name="Progress Bar").click()
    page.locator("#startButton").click()
    page.wait_for_function(
        "() => Number(document.getElementById('progressBar').getAttribute('aria-valuenow')) >= 75",
        timeout=60000,
    )
    page.locator("#stopButton").click()
    value = int(page.locator("#progressBar").get_attribute("aria-valuenow"))
    assert 75 <= value <= 85, f"stopped at {value}%"
    expect(page.locator("#result")).to_contain_text(f"Result: {value - 75}")


def test_visibility(page: Page) -> None:
    page.get_by_role("link", name="Visibility").click()
    page.locator("#hideButton").click()

    expect(page.locator("#removedButton")).to_have_count(0)
    expect(page.locator("#zeroWidthButton")).not_to_be_visible()
    expect(page.locator("#invisibleButton")).to_be_hidden()
    expect(page.locator("#notdisplayedButton")).to_be_hidden()
    expect(page.locator("#offscreenButton")).not_to_be_in_viewport()
    expect(page.locator("#transparentButton")).to_have_css("opacity", "0")
    # Overlapped button is still in the DOM but another layer intercepts pointer events.
    with pytest.raises(Exception):
        page.locator("#overlappedButton").click(timeout=2000)


def test_sample_app_login_and_logout(page: Page) -> None:
    page.get_by_role("link", name="Sample App").click()
    page.get_by_placeholder("User Name").fill("tester")
    page.get_by_placeholder("********").fill("pwd")
    page.locator("#login").click()
    expect(page.locator("#loginstatus")).to_have_text("Welcome, tester!")
    expect(page.locator("#login")).to_have_text("Log Out")

    page.locator("#login").click()
    expect(page.locator("#loginstatus")).to_have_text("User logged out.")


def test_sample_app_invalid_password(page: Page) -> None:
    page.get_by_role("link", name="Sample App").click()
    page.get_by_placeholder("User Name").fill("tester")
    page.get_by_placeholder("********").fill("wrong")
    page.locator("#login").click()
    expect(page.locator("#loginstatus")).to_have_text("Invalid username/password")


def test_mouse_over(page: Page) -> None:
    page.get_by_role("link", name="Mouse Over").click()
    # Hovering replaces the element, so the locator is re-resolved on every action.
    link = page.get_by_text("Click me", exact=True)
    link.click()
    link.click()
    expect(page.locator("#clickCount")).to_have_text("2")

    link_button = page.get_by_text("Link Button", exact=True)
    link_button.click()
    link_button.click()
    expect(page.locator("#clickButtonCount")).to_have_text("2")


def test_non_breaking_space(page: Page) -> None:
    page.get_by_role("link", name="Non-Breaking Space").click()
    # A plain-space XPath does not match the &nbsp; in the button text.
    expect(page.locator("//button[text()='My Button']")).to_have_count(0)
    expect(page.get_by_role("button", name="My Button")).to_be_visible()
    expect(page.locator("//button[text()='My Button']")).to_be_visible()


def test_overlapped_element(page: Page) -> None:
    page.get_by_role("link", name="Overlapped Element").click()
    name = page.locator("#name")
    # The field sits under an absolutely positioned overlay; scroll the inner container so it is exposed.
    name.evaluate("el => el.parentElement.scrollTop = el.offsetTop")
    name.click()
    name.fill("Playwright")
    expect(name).to_have_value("Playwright")


def test_shadow_dom(page: Page) -> None:
    page.get_by_role("link", name="Shadow DOM").click()
    # Playwright locators pierce open shadow roots automatically.
    page.locator("#buttonGenerate").click()
    guid = page.locator("#editField").input_value()
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", guid)

    # navigator.clipboard is unavailable on a plain-http origin, so only check the copy button is usable.
    page.locator("#buttonCopy").click()
    expect(page.locator("#editField")).to_have_value(guid)


def test_alerts(page: Page) -> None:
    page.get_by_role("link", name="Alerts").click()
    messages = []

    def handle(dialog):
        messages.append((dialog.type, dialog.message))
        if dialog.type == "prompt":
            dialog.accept("Playwright")
        else:
            dialog.accept()

    page.on("dialog", handle)
    page.locator("#alertButton").click()
    page.locator("#confirmButton").click()
    page.locator("#promptButton").click()

    assert [t for t, _ in messages] == ["alert", "confirm", "prompt"]


def test_file_upload(page: Page, tmp_path) -> None:
    page.get_by_role("link", name="File Upload").click()
    sample = tmp_path / "sample.txt"
    sample.write_text("hello playwright")

    frame = page.frame_locator("iframe")
    frame.locator("#browse").set_input_files(str(sample))
    expect(frame.get_by_text("sample.txt")).to_be_visible()


def test_animated_button(page: Page) -> None:
    page.get_by_role("link", name="Animated Button").click()
    page.locator("#animationButton").click()
    target = page.locator("#movingTarget")
    # Wait for the animation to finish (the "spin" class is removed on animationend).
    expect(target).not_to_have_class(re.compile(r"spin"), timeout=15000)
    target.click()
    expect(page.locator("#opstatus")).to_have_text("Moving Target clicked. It's class name is 'btn btn-primary'")


def test_disabled_input(page: Page) -> None:
    page.get_by_role("link", name="Disabled Input").click()
    page.locator("#enableButton").click()
    field = page.locator("#inputField")
    expect(field).to_be_disabled()
    expect(field).to_be_enabled(timeout=10000)
    field.fill("Playwright")
    field.press("Tab")
    expect(page.locator("#opstatus")).to_have_text("Value changed to: Playwright")


def test_auto_wait(page: Page) -> None:
    page.get_by_role("link", name="Auto Wait").click()
    page.locator("#element-type").select_option("button")
    page.locator("#visible").uncheck()
    page.locator("#enabled").uncheck()
    page.locator("#applyButton3").click()
    # The target is hidden/disabled for 3s; Playwright auto-waits before clicking.
    page.locator("#target").click(timeout=10000)
    expect(page.locator("#opstatus")).to_have_text("Target clicked.")


def test_frames(page: Page) -> None:
    page.get_by_role("link", name="Frames").click()
    outer = page.frame_locator("#frame-outer")
    outer.get_by_role("button", name="Submit").click()
    expect(outer.locator("#result")).to_have_text("Button pressed: Submit")

    inner = outer.frame_locator("#frame-inner")
    inner.get_by_role("button", name="Click me").click()
    expect(inner.locator("#result")).to_have_text("Button pressed: Click me")


def test_geo_location(page: Page) -> None:
    # The Geolocation API is blocked on insecure (http) origins, so stub it before the page loads.
    page.add_init_script(
        """navigator.geolocation.getCurrentPosition = (ok) =>
               ok({ coords: { latitude: 51.5074, longitude: -0.1278, accuracy: 10 } });"""
    )
    page.get_by_role("link", name="Geo Location").click()
    page.locator("#requestLocation").click()
    location = page.locator("#location")
    expect(location).not_to_have_text("Not requested")
    expect(location).to_contain_text("51.5")


def test_clear_input(page: Page) -> None:
    page.get_by_role("link", name="Clear Input").click()
    for field in page.locator(".clear-target").all():
        field.clear()
        expect(field).to_have_value("")


def test_scroll_to_click(page: Page) -> None:
    page.get_by_role("link", name="Scroll to Click").click()
    for i in range(1, 4):
        button = page.locator(f"#scrollTarget{i}")
        button.scroll_into_view_if_needed()
        button.click()
        expect(button).to_have_class(re.compile(r"btn-success"))

    # Case 4: the Flag button only appears while its row is hovered.
    page.locator("#targetRow4").scroll_into_view_if_needed()
    page.locator("#targetRow4").hover()
    page.locator("#scrollTarget4").click()
    expect(page.locator("#scrollTarget4")).to_have_class(re.compile(r"btn-success"))
    expect(page.locator("#progressText")).to_have_text("All buttons clicked!")


def test_css_selectors(page: Page) -> None:
    page.get_by_role("link", name="CSS Selectors").click()
    expect(page.locator("#primary-btn")).to_have_text("Primary Button")
    expect(page.locator(".css-btn")).to_have_count(3)
    expect(page.locator(".css-btn.highlight")).to_have_text("Third")
    expect(page.locator("[data-testid='username-input']")).to_have_attribute("placeholder", "Username")
    expect(page.locator("a[target='_blank']")).to_have_attribute("href", "https://example.com")
    expect(page.locator("span[data-status='active']")).to_have_text("Active")


def test_select(page: Page) -> None:
    page.get_by_role("link", name="Select", exact=True).click()
    page.locator("#selectLanguage").select_option(label="Python")
    expect(page.locator("#statusLanguage")).to_contain_text("Python")

    page.locator("#selectCity").select_option("sf")
    expect(page.locator("#statusCity")).to_contain_text("San Francisco")
