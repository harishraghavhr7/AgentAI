import google.generativeai as genai
import requests
import json

# ----------------------------
# 🔐 SET YOUR API KEYS HERE
# ----------------------------
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------
# 🌦 Weather Tool Function
# ----------------------------
def get_weather(location: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return {"error": "Location not found"}

    return {
        "location": location,
        "temperature_celsius": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }

# ----------------------------
# 🛠 Tool Definition
# ----------------------------
weather_tool = {
    "name": "get_weather",
    "description": "Get current weather information for a given city",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name to get weather for"
            }
        },
        "required": ["location"]
    }
}

# ----------------------------
# 🤖 Create Gemini Model
# ----------------------------
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[weather_tool]
)

chat = model.start_chat()

# ----------------------------
# 💬 User Input
# ----------------------------
user_query = input("Ask something about weather: ")

response = chat.send_message(user_query)

# ----------------------------
# 🔄 Handle Tool Call
# ----------------------------
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    
    if function_call.name == "get_weather":
        args = dict(function_call.args)
        result = get_weather(**args)

        # Send tool result back to Gemini
        final_response = chat.send_message(
            genai.types.Part.from_function_response(
                name="get_weather",
                response=result
            )
        )

        print("\nGemini Response:")
        print(final_response.text)

else:
    print("\nGemini Response:")
    print(response.text)