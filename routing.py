import google.generativeai as genai

genai.configure(api_key="AIzaSyCDabmhS8naYquZ7rx0z-unYrCksE15Weg")

flash = genai.GenerativeModel("gemini-2.5-flash")
pro = genai.GenerativeModel("gemini-2.5-pro")

router_model = genai.GenerativeModel("gemini-2.5-flash")

def route_llm(prompt):
    decision = router_model.generate_content(f"""
Classify this request into one label:
- simple
- complex

Request: {prompt}
Answer only the label.
""").text.strip().lower()

    if "complex" in decision:
        return pro
    return flash

def ask(prompt):
    model = route_llm(prompt)
    response = model.generate_content(prompt)
    return response.text

while True:
    q = input("You: ")
    print("AI:", ask(q))