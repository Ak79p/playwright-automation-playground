# Dynamic ID Test Plan

**Target:** http://www.uitestingplayground.com/dynamicid
**Test framework:** Python + pytest + Playwright (`tests/`)

## Locator guidance

- **Stable locator to use:** `page.get_by_role("button", name="Button with Dynamic ID")`. The button's accessible
  role (`button`) and accessible name (`Button with Dynamic ID`) never change between page loads. The button's CSS
  class attribute (`btn btn-primary`) is also stable and may be used as a secondary/confirming locator (e.g.
  `page.locator("button.btn.btn-primary")`), but the role+name locator is preferred since the class is generic and
  shared by other Bootstrap buttons across the site.
- **Forbidden pattern:** Never locate the button using its `id` attribute, in any form — not `page.locator("#<id>")`,
  not `page.locator("button[id='<id>']")`, and not an XPath that embeds the id such as
  `//button[@id='<id>']`. Any test code that hardcodes an id value observed during exploration or during a prior
  test run is invalid, because that id will not exist on the next page load.
  - Allowed XPath alternative if XPath is ever required: `//button[text()="Button with Dynamic ID"]` (no id
    referenced).
- **Why:** The page under test intentionally generates a new random UUID-style `id` for the button on every page
  load (two consecutive loads during exploration produced two completely different UUID-style values; they are
  deliberately not reproduced here so nobody copies one into a test). The button's role and accessible name
  ("Button with Dynamic ID") and its class (`btn btn-primary`) remain constant across loads. Tests must therefore
  never reference a specific id value in code or assertions, except when explicitly proving a negative case (see
  Scenario 1.5), where the id must be treated as an opaque, previously observed value captured at runtime — never a
  literal string written into the test.

### 1. Dynamic ID
**Start URL:** http://www.uitestingplayground.com/dynamicid

#### 1.1 Button is visible and enabled with a stable accessible name
**Steps:**
1. Navigate to http://www.uitestingplayground.com/dynamicid.
2. Locate the button using `get_by_role("button", name="Button with Dynamic ID")`.
**Expected:**
- The button is visible.
- The button is enabled (not disabled).
- The button's accessible name is exactly "Button with Dynamic ID".
- The button's `class` attribute contains `btn` and `btn-primary`.

#### 1.2 Clicking the button succeeds without side effects
**Steps:**
1. Navigate to http://www.uitestingplayground.com/dynamicid.
2. Locate the button by role "button" and name "Button with Dynamic ID".
3. Click the button.
**Expected:**
- The click completes without throwing an error or timing out.
- The page URL remains http://www.uitestingplayground.com/dynamicid (no navigation occurs).
- No JavaScript error is logged to the browser console as a result of the click.
- No dialog (alert/confirm/prompt) appears.
- The button identified by role "button" and name "Button with Dynamic ID" is still visible and enabled
  immediately after the click (the page content is otherwise unchanged — clicking does not add, remove, or
  alter any visible text on the page).

#### 1.3 Button id differs between two page loads
**Steps:**
1. Navigate to http://www.uitestingplayground.com/dynamicid.
2. Read the `id` attribute of the button located by role "button" and name "Button with Dynamic ID"; store it as
   `firstId`.
3. Navigate to http://www.uitestingplayground.com/dynamicid again (fresh page load, not a soft reload via
   history).
4. Read the `id` attribute of the button located by role "button" and name "Button with Dynamic ID" on the
   reloaded page; store it as `secondId`.
**Expected:**
- `firstId` and `secondId` are both non-empty strings.
- `firstId` is not equal to `secondId`, proving the id is regenerated on every page load and must not be used as
  a locator.
- On both loads, the button's accessible role remains "button" and its accessible name remains exactly
  "Button with Dynamic ID".

#### 1.4 Stable role/name locator still resolves after a reload
**Steps:**
1. Navigate to http://www.uitestingplayground.com/dynamicid.
2. Confirm the button located by role "button" and name "Button with Dynamic ID" is visible.
3. Reload the page (navigate to the same URL again).
4. Using the same role+name locator (`get_by_role("button", name="Button with Dynamic ID")`), locate the button
   again — do not capture or reuse any id.
**Expected:**
- The role+name locator resolves to exactly one element both before and after the reload.
- The button is visible and enabled after the reload.
- Clicking the button after the reload succeeds without error, confirming the locator remains valid across
  reloads even though the underlying id has changed.

#### 1.5 Negative check: a locator built from a previously observed id does not resolve after reload
**Steps:**
1. Navigate to http://www.uitestingplayground.com/dynamicid.
2. Read the current `id` attribute of the button located by role "button" and name "Button with Dynamic ID" and
   store it in a variable at runtime (this is "the id observed on the previous load" — never hardcode this value
   as a literal string in the test).
3. Build a CSS locator at runtime using that stored id value, e.g. `page.locator(f'[id="{observed_id}"]')`
   (attribute selector, because `#<id>` is invalid CSS when the generated id starts with a digit).
4. Confirm this id-based locator resolves to the button on the current page (sanity check that the captured id
   was correct for this load).
5. Reload the page (navigate to the same URL again).
6. Without changing the locator string, attempt to locate an element using the same id-based locator built from
   the id observed on the previous load (step 2's stored value).
**Expected:**
- In step 4, the id-based locator resolves to exactly one element (the button), confirming the id was valid for
  that specific page load.
- In step 6, after the reload, the id-based locator built from the id observed on the previous load resolves to
  zero elements (the element is not found / locator times out with zero matches), because the page regenerated a
  new id on reload.
- This demonstrates why the id must never be hardcoded or reused across page loads/test runs, and confirms that
  only the role/name (or class) locator from the Locator Guidance section should be used in real test code.
