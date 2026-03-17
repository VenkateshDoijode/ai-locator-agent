"""
Author: Venkateshwara Doijode
"""
# BeautifulSoup — HTML parsing library for extracting elements from raw HTML strings
from bs4 import BeautifulSoup
from utils.agent_decorator import agent


@agent("DOM Filter Agent")
def filter_agent(state):
    """
    Step 4 of the pipeline.
    Parses the raw DOM HTML and extracts only interactive elements
    (buttons, inputs, links, etc.) that are relevant for UI locator generation.
    Reduces noise by ignoring non-interactive tags like divs, spans, etc.
    """

    html = state["dom"]  # Raw HTML string captured by page_loader_agent

    # Parse the HTML with Python's built-in html.parser
    soup = BeautifulSoup(html, "html.parser")

    # Find all interactive/form-related HTML elements that QA engineers typically locate
    elements = soup.find_all([
        "button",    # Clickable buttons
        "input",     # Text fields, checkboxes, radio buttons, etc.
        "textarea",  # Multi-line text input areas
        "select",    # Dropdown menus
        "a",         # Hyperlinks (often clickable targets in tests)
        "label"      # Labels tied to form inputs (useful for accessible locators)
    ])

    snippets = []

    for el in elements:
        # Convert each element back to its HTML string representation
        # Truncate to 500 chars to avoid sending huge HTML blobs to the LLM later
        snippets.append(str(el)[:500])

    # Store the list of HTML snippets in state for the vision_locator_agent
    state["interactive_elements"] = snippets

    return state