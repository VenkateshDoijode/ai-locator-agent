"""

Author: Venkateshwara Doijode

"""
# Import the factory function that initializes the shared state dictionary for the pipeline
from state_schema import create_initial_state

# Import each agent in the pipeline — each agent performs one step of the locator extraction process
from agents.page_loader_agent import page_loader_agent       # Loads the webpage DOM/HTML
from agents.scroll_agent import scroll_agent                 # Scrolls the page to trigger lazy-loaded content
from agents.screenshot_agent import screenshot_agent         # Captures a screenshot of the rendered page
from agents.filter_agent import filter_agent                 # Filters the DOM to isolate interactive elements
from agents.vision_locator_agent import vision_locator_agent # Uses vision/AI to identify UI element locators
from agents.validation_agent import validation_agent         # Validates and scores each locator for reliability
from agents.aggregator_agent import aggregator_agent         # Aggregates and saves the final results


def run_pipeline(url):
    """
    Orchestrates the full multi-agent pipeline.
    Each agent receives the current state, processes it, and returns an updated state.
    If any agent raises an exception, the pipeline halts and reports the failure.
    """

    # Initialize the shared state dict with the target URL and empty placeholders
    state = create_initial_state(url)

    # Define the ordered sequence of agents — each step builds on the previous one's output
    pipeline = [
        page_loader_agent,       # Step 1: Load page content
        scroll_agent,            # Step 2: Scroll to reveal dynamic/lazy content
        screenshot_agent,        # Step 3: Capture visual snapshot
        filter_agent,            # Step 4: Extract interactive elements from the DOM
        vision_locator_agent,    # Step 5: Use vision model to identify CSS locators
        validation_agent,        # Step 6: Score and validate each locator candidate
        aggregator_agent         # Step 7: Compile and persist final output
    ]

    # Run each agent in sequence, passing state through like a baton
    for agent in pipeline:
        try:
            state = agent(state)  # Agent consumes and returns updated state

        except Exception as e:
            # If an agent fails, log which step broke and stop the pipeline
            print(f"\n❌ Pipeline failed at {agent.__name__}")
            print(f"Error: {e}")
            break  # Exit the loop — remaining agents are skipped

    return state  # Return the final state (complete or partial, depending on where it stopped)


def main():
    """
    Entry point: prompts the user for a URL, runs the pipeline,
    and prints a summary of the top locator candidates found.
    """

    # Prompt the user for a target webpage URL and strip any accidental whitespace
    url = input("Enter webpage URL: ").strip()

    # Normalize the URL — prepend https:// if the user omitted the scheme
    if not url.startswith("http"):
        url = "https://" + url

    # Execute the full agent pipeline on the given URL
    final_state = run_pipeline(url)

    print("\n✅ Pipeline completed")

    # Only display results if the validation agent successfully populated validated_output
    if "validated_output" in final_state:
        print("\nTop Locator Candidates:\n")

        # Show only the top 5 results to keep output concise
        for item in final_state["validated_output"][:5]:

            # Extract the human-readable element name, its CSS selector, and reliability score
            name = item.get("element_name")
            locator = item.get("css_locator")
            score = item.get("reliability_score")

            # Print a summary line for each top locator
            print(f"{name} → {locator} (score={score})")

    print("\n📁 Results saved to validated_locators.json\n")


# Standard Python guard — only run main() when this script is executed directly,
# not when it's imported as a module by another file
if __name__ == "__main__":
    main()