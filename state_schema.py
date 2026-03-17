"""

Author: Venkateshwara Doijode

"""   
def create_initial_state(url):
    """
    Creates and returns the initial shared state dictionary for the pipeline.
    This state is passed between all agents — each agent reads from it and
    writes its results back into it, allowing data to flow through the pipeline.

    Args:
        url (str): The target webpage URL to be processed.

    Returns:
        dict: A dictionary with all expected state keys initialized to None or empty.
    """

    return {
        "url": url,                  # The target URL — used by page_loader_agent to fetch the page
        "dom": None,                 # Will hold the raw HTML/DOM content after page loading
        "screenshot_path": None,     # Will hold the file path to the captured screenshot
        "interactive_elements": [],  # Will be populated with filtered UI elements (buttons, inputs, etc.)
        "analysis": [],              # Will store vision model analysis results for each element
        "final_output": []           # Will hold the final aggregated list of validated locators
    }