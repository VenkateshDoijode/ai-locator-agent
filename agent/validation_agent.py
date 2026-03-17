"""
Author: Venkateshwara Doijode
"""
from playwright.sync_api import sync_playwright
from utils.agent_decorator import agent


def stability_score(locator):
    """
    Estimates how stable (resilient to UI changes) a CSS locator is,
    based on the type of attribute it uses.
    Inspired by Playwright's own locator preference guidelines.

    Scoring rationale:
      - ID (#)           → Most stable, IDs are meant to be unique and rarely change
      - data-testid      → Explicitly added for testing, very reliable
      - name=            → Form field names are usually stable
      - aria-*           → Accessibility attributes, stable and semantically meaningful
      - placeholder      → Moderately stable, but UI copy can change
      - text             → Fragile — display text changes with copy/i18n updates
      - anything else    → Least reliable (class names, indexes, etc.)
    """

    if not locator:
        return 0  # No locator provided — score zero

    locator = locator.lower()  # Normalize to lowercase for consistent matching

    if "#" in locator:
        return 1.0       # ID selector — best possible stability

    if "data-testid" in locator:
        return 0.95      # Test-specific attribute — purpose-built for automation

    if "name=" in locator:
        return 0.9       # Input name attributes — stable in forms

    if "aria" in locator:
        return 0.85      # ARIA attributes — accessibility-driven, rarely removed

    if "placeholder" in locator:
        return 0.85      # Placeholder text — fairly stable but can change with copy updates

    if "text" in locator:
        return 0.8       # Text-based locators — readable but brittle to copy changes

    return 0.6           # Generic fallback (class names, tag-only selectors, etc.)


def uniqueness_score(matches):
    """
    Scores a locator based on how many elements it matches on the page.
    A good locator should match exactly one element — ambiguous locators are unreliable.

    Args:
        matches (int): Number of DOM elements the CSS locator matched.
    """

    if matches == 1:
        return 1.0   # Perfect — uniquely identifies one element

    if matches in [2, 3]:
        return 0.6   # Ambiguous — matches a few elements, may need refinement

    if matches > 3:
        return 0.3   # Too generic — matches many elements, unreliable for targeting

    return 0         # Zero matches — locator doesn't exist on this page


@agent("Locator Validation Agent")
def validation_agent(state):
    """
    Step 6 of the pipeline.
    For each locator candidate from vision_locator_agent:
      1. Launches a real browser and checks if the CSS locator actually exists on the page
      2. Counts how many elements it matches (uniqueness)
      3. Computes a reliability score = stability × uniqueness
      4. Sorts results by reliability score (best first)
    """

    locators = state.get("final_output", [])  # Locator candidates from vision_locator_agent
    url = state["url"]

    validated = []

    # Guard: if the LLM accidentally returned a plain string instead of a list of dicts,
    # skip validation gracefully rather than crashing
    if isinstance(locators, str):
        print("⚠️ LLM output was string, skipping validation")
        state["validated_output"] = []
        return state

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the live page to test locators against the actual DOM
        page.goto(url, wait_until="domcontentloaded")

        for item in locators:

            # Skip any items that aren't proper dictionaries (malformed LLM output)
            if not isinstance(item, dict):
                continue

            css = item.get("css_locator")  # The CSS selector string to test

            matches = 0
            exists = False

            if css:
                try:
                    # Count how many elements this CSS selector matches on the live page
                    matches = page.locator(css).count()
                    exists = matches > 0  # True if at least one element was found
                except:
                    # Playwright throws if the selector is syntactically invalid
                    matches = 0
                    exists = False

            # Calculate individual score components
            stability = stability_score(css)
            uniqueness = uniqueness_score(matches)

            # Combined reliability = stability × uniqueness, rounded for readability
            # Both factors must be high for the overall score to be high
            reliability = round(stability * uniqueness, 2)

            # Annotate the item dict with validation results
            item["valid"] = exists               # Whether the element was found on the page
            item["matches"] = matches            # How many elements the selector matched
            item["stability_score"] = stability  # How robust the selector type is
            item["reliability_score"] = reliability  # Final combined score

            validated.append(item)

        browser.close()

    # Sort all validated locators by reliability score, highest first
    # This surfaces the best locators at the top for the output summary
    validated.sort(
        key=lambda x: x.get("reliability_score", 0),
        reverse=True
    )

    # Store ranked results in state for the aggregator_agent
    state["validated_output"] = validated

    return state