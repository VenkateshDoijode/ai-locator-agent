def build_prompt(elements):

    return f"""
You are the best senior QA automation engineer.

Your task is to analyze a webpage screenshot and HTML elements and identify UI components with reliable automation locators.

IMPORTANT RULES:
- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include comments
- Output must be a JSON array

Locator priority:
1. id
2. data-testid
3. name
4. aria-label
5. placeholder
6. visible text
7. css fallback

Output format EXACTLY like this:

[
  {{
    "element_name": "login_button",
    "element_type": "button",
    "description": "Login button used to submit login form",
    "css_locator": "#login-btn",
    "xpath_locator": "//button[@id='login-btn']",
    "playwright_locator": "page.locator('#login-btn')"
  }}
]

HTML elements to analyze:

{elements}
"""