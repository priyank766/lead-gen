from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: Replace with your Groq API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_with_llm(html_content: str) -> dict:
    """
    Extracts structured data from HTML content using an LLM.

    Args:
        html_content: The HTML content to extract data from.

    Returns:
        A dictionary containing the extracted data.
    """
    system_prompt = """
    You are a strict JSON extractor. Given raw webpage text or HTML, output ONLY a JSON object (no commentary, no backticks) that matches the schema:
    {
      "company_name": string|null,
      "domain": string|null,
      "emails": [string],
      "phones": [string],
      "linkedin": string|null,
      "has_contact_page": boolean,
      "has_pricing": boolean,
      "intent_phrases": [string],
      "title": string|null,
      "raw_snippet": string|null,
      "industry": string|null,
      "tech_stack": [string]
    }
    Rules:
    - If unsure about a field, use null or empty array.
    - Never fabricate contact info.
    - Keep values minimal (no paragraphs).
    - For 'industry', provide a concise industry classification (e.g., 'Software as a Service (SaaS)', 'E-commerce', 'Healthcare').
    - For 'tech_stack', list key technologies found on the page (e.g., 'React', 'Stripe', 'Google Analytics').
    """


    try:
        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": html_content[:4000]},
            ],
            temperature=0,
            max_tokens=500,
            top_p=1,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        return {}

def main():
    """
    Main function to test the extractor.
    """
    test_html = "<html><head><title>Acme Inc</title></head><body><a href=\"/contact\">Contact Us</a><p>Email us at: test@acme.com</p><script src=\"https://cdn.jsdelivr.net/npm/react/umd/react.development.js\"></script></body></html>"
    extracted_data = extract_with_llm(test_html)
    print(extracted_data)

if __name__ == "__main__":
    main()
