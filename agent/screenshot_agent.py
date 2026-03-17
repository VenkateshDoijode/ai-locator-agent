"""
Author: Venkateshwara Doijode
"""
from playwright.sync_api import sync_playwright
from utils.agent_decorator import agent


@agent("Screenshot Agent")
def screenshot_agent(state):
    """
    Step 3 of the pipeline.
    Captures a full-page screenshot of the rendered webpage.
    The screenshot is later used by the vision_locator_agent to
    visually identify UI elements alongside their HTML snippets.
    """

    url = state["url"]

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Scroll to the very bottom before screenshotting to ensure
        # all lazy-loaded content is visible in the final image
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        path = "debug/page.png"  # Output path for the screenshot file

        # Capture the entire page (not just the visible viewport) as a PNG
        page.screenshot(path=path, full_page=True)

        # Store the screenshot file path in state so vision_locator_agent can read it
        state["screenshot_path"] = path

        browser.close()

    return state