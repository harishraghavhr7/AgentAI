import google.generativeai as genai
from pydantic import BaseModel, create_model
from typing import Literal
import os
import json

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.5 Flash
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "response_mime_type": "application/json"
    }
)


def build_dynamic_schema(intents: list[str]):
    """
    Dynamically create a Pydantic model
    with allowed intents as Literal values.
    """
    IntentLiteral = Literal[tuple(intents)]
    
    DynamicIntentModel = create_model(
        "DynamicIntentModel",
        intent=(IntentLiteral, ...)
    )
    
    return DynamicIntentModel


def classify_intent(user_input: str, intents: list[str]):

    # Build schema dynamically
    IntentModel = build_dynamic_schema(intents)

    # Create dynamic prompt
    intent_list = "\n- ".join(intents)

    prompt = f"""
    Classify the user intent into one of:
    - {intent_list}

    Return ONLY valid JSON:
    {{"intent": "<one_of_the_above>"}}

    User: {user_input}
    """

    response = model.generate_content(prompt)

    parsed_json = json.loads(response.text.strip())

    # Validate with dynamic schema
    return IntentModel(**parsed_json)


# Example usage
if __name__ == "__main__":

    intents = [
        "book_flight",
        "cancel_flight",
        "check_weather",
        "order_food",
        "unknown"
    ]

    result = classify_intent(
        "I want to order pizza tonight",
        intents
    )

    print(result)