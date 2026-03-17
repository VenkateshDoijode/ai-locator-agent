"""

Author: Venkateshwara Doijode

"""
import base64   # Used to encode the screenshot image as a base64 string for the API
import json     # For parsing JSON responses from the LLM
import os       # For reading environment variables (API key)
import re       # For regex-based JSON extraction from LLM response text

from dotenv import load_dotenv  # Loads environment variables from a .env file
from openai import OpenAI       # OpenAI Python SDK client

from utils.agent_decorator import agent
# Helper that builds the text prompt for each element sent to the vision model
from prompts.vision_locator_prompt import build_prompt

# Load OPENAI_API_KEY and any other vars from the .env file into the environment
load_dotenv()

# Initialize the OpenAI client using the API key from the environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def encode_image(path):
    """
    Reads an image file from disk and encodes it as a base64 string.
    OpenAI's vision API requires images to be base64-encoded when sent inline.
    """
    with open(path, "rb") as f:  # Open in binary read mode
        return base64.b64encode(f.read()).decode("utf-8")  # Encode bytes → base64 → UTF-8 string


def parse_json(text):
    """
    Extracts a JSON object from a free-form LLM response string.
    LLMs sometimes wrap JSON in markdown or extra text, so we use
    regex to find the first {...} block and parse only that.
    """
    try:
        # re.DOTALL makes '.' match newlines too — needed for multi-line JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())  # Parse the matched JSON string
    except Exception:
        return None  # Return None if parsing fails — caller handles gracefully


@agent("Vision Locator Agent")
def vision_locator_agent(state):
    """
    Step 5 of the pipeline.
    For each interactive HTML element, sends both the element's HTML snippet
    and the full-page screenshot to GPT-4.1-mini (vision model).
    The model acts as a senior QA engineer and generates stable CSS locators.
    Results are collected and stored in state["final_output"].
    """

    elements = state.get("interactive_elements", [])   # HTML snippets from filter_agent
    screenshot_path = state.get("screenshot_path")     # Screenshot path from screenshot_agent

    # Encode the screenshot once — reused for every element to avoid re-reading the file
    screenshot = encode_image(screenshot_path)

    results = []

    # Cap at 50 elements to control API cost and avoid hitting token limits
    for element in elements[:50]:

        # Build the text prompt for this specific HTML element
        prompt = build_prompt(element)

        try:
            # Call the GPT-4.1-mini vision model with both text and image inputs
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                temperature=0,  # Deterministic output — important for consistent locator generation
                messages=[
                    {
                        "role": "system",
                        # Sets the model's persona to produce QA-focused, stable locators
                        "content": "You are a senior QA automation engineer generating stable UI locators."
                    },
                    {
                        "role": "user",
                        "content": [
                            # The text prompt describing what locator to generate
                            {"type": "text", "text": prompt},
                            {
                                # The full-page screenshot sent inline as a base64 data URI
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot}"
                                }
                            }
                        ]
                    }
                ]
            )

            # Extract the model's text response from the API response object
            response_text = response.choices[0].message.content

            # Attempt to parse a JSON object out of the response text
            parsed = parse_json(response_text)

            if parsed:
                results.append(parsed)  # Only keep successfully parsed results

        except Exception as e:
            # Log element-level failures without stopping the whole agent
            print(f"⚠️ Failed to process element: {e}")

    # Store all parsed locator results for the validation_agent
    state["final_output"] = results

    return state