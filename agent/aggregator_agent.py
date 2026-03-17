"""
Author: Venkateshwara Doijode
"""
import json  # For serializing the validated locators list to a JSON file
from utils.agent_decorator import agent


@agent("Aggregator Agent")
def aggregator_agent(state):
    """
    Step 7 — final step of the pipeline.
    Takes the validated and ranked locators from state and
    persists them to a JSON file on disk.
    This file is the final deliverable of the entire pipeline.
    """

    # Retrieve the sorted, validated locator list from the previous agent
    validated = state["validated_output"]

    # Write the results to a human-readable JSON file
    # indent=2 makes the output pretty-printed for easy inspection
    with open("validated_locators.json", "w") as f:
        json.dump(validated, f, indent=2)

    return state  # Return state unchanged — this agent's job is purely output/persistence