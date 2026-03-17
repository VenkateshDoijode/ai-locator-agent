"""
Author: Venkateshwara Doijode
"""
from playwright.sync_api import sync_playwright
from utils.agent_decorator import agent


@agent("Auto Scroll Agent")
def scroll_agent(state):
    """
    Step 2 of the pipeline.
    Scrolls the page from top to bottom in increments to trigger
    lazy-loaded content (images, components that load on scroll).
    Does not modify the DOM in state — just ensures content is rendered.
    """

    url = state["url"]

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Inject and execute a JavaScript snippet inside the browser context
        # This simulates a real user scrolling down the page gradually
        page.evaluate("""
        async () => {
            await new Promise(resolve => {
                let totalHeight = 0;
                let distance = 300;  // Scroll 300px per step

                // setInterval fires every 200ms, scrolling incrementally
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);      // Scroll down by 'distance' pixels
                    totalHeight += distance;            // Track how far we've scrolled

                    // Stop once we've scrolled past the full page height
                    if(totalHeight >= document.body.scrollHeight){
                        clearInterval(timer);  // Cancel the repeating interval
                        resolve();             // Resolve the Promise so await completes
                    }
                }, 200);
            });
        }
        """)

        # Flag in state that scrolling has been completed
        # Downstream agents can check this if needed
        state["scrolled"] = True

        browser.close()

    return state