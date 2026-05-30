import os
from dotenv import load_dotenv

load_dotenv()


def use_gemini():
    flag = os.getenv("USE_GEMINI", "false").lower().strip()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return flag == "true" and len(api_key) > 0


def generate_with_gemini(prompt, fallback_text=None):
    if fallback_text is None:
        fallback_text = "Gemini API is not configured. Using local fallback output."

    if not use_gemini():
        return fallback_text

    try:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return fallback_text

    except Exception as exc:
        return f"{fallback_text}\n\n[Gemini fallback triggered: {exc}]"