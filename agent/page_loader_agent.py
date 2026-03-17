"""
Author: Venkateshwara Doijode
"""
# Playwright's synchronous API — used to control a real Chromium browser programmatically
from playwright.sync_api import sync_playwright
# Custom decorator that wraps agents with start/end logging and timing
from utils.agent_decorator import agent


@agent("Page Loader Agent")  # Registers this function with the logging/timing decorator
def page_loader_agent(state):
    """
    Step 1 of the pipeline.
    Launches a headless browser, navigates to the target URL,
    captures the fully rendered HTML (DOM), and saves it to state and disk.
    """

    url = state["url"]  # Pull the target URL from shared pipeline state

    with sync_playwright() as p:

        # Launch Chromium in headless mode (no visible browser window)
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()  # Open a new browser tab

        # Navigate to the URL and wait until the DOM is fully loaded
        # "domcontentloaded" is faster than "networkidle" — good for static structure capture
        page.goto(url, wait_until="domcontentloaded")

        # Extract the fully rendered HTML including JS-injected content
        html = page.content()

        # Store the DOM in state so downstream agents (e.g. filter_agent) can use it
        state["dom"] = html

        browser.close()  # Release browser resources

    # Also persist the DOM to disk for debugging/inspection purposes
    with open("debug/dom.html", "w", encoding="utf-8") as f:
        f.write(html)

    return state  # Pass enriched state to the next agent