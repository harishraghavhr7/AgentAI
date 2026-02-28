import google.generativeai as genai
import requests
import json
from datetime import datetime
import pytz
import math
from typing import Dict, Any, Callable
import logging

# ----------------------------
# 🔐 SET YOUR API KEYS HERE
# ----------------------------
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

genai.configure(api_key=GEMINI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------
# 🛠 Tool Registry System
# ----------------------------
class ToolRegistry:
    """Manages all available tools and their definitions"""
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: list = []
    
    def register(self, name: str, func: Callable, definition: Dict[str, Any]):
        """Register a new tool"""
        self.tools[name] = func
        self.tool_definitions.append(definition)
        logging.info(f"Registered tool: {name}")
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given arguments"""
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found"}
        
        try:
            logging.info(f"Executing tool: {name} with args: {kwargs}")
            result = self.tools[name](**kwargs)
            return result
        except Exception as e:
            logging.error(f"Error executing {name}: {str(e)}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def list_tools(self) -> str:
        """List all available tools"""
        tools_info = []
        for tool_def in self.tool_definitions:
            tools_info.append(f"- {tool_def['name']}: {tool_def['description']}")
        return "\n".join(tools_info)

# Initialize tool registry
registry = ToolRegistry()

# ----------------------------
# 🌦 Weather Tool Function
# ----------------------------
def get_weather(location: str):
    """Get current weather information for a given city"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code != 200:
            return {"error": "Location not found"}

        return {
            "location": location,
            "temperature_celsius": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}

# ----------------------------
# 🧮 Calculator Tool Function
# ----------------------------
def calculate(operation: str, a: float, b: float = None):
    """Perform mathematical calculations"""
    try:
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
            "power": lambda x, y: x ** y,
            "sqrt": lambda x, y: math.sqrt(x),
            "modulo": lambda x, y: x % y
        }
        
        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}
        
        if operation == "sqrt":
            result = operations[operation](a, None)
        else:
            if b is None:
                return {"error": "Second operand required for this operation"}
            result = operations[operation](a, b)
        
        return {
            "operation": operation,
            "operand_a": a,
            "operand_b": b,
            "result": result
        }
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}

# ----------------------------
# 🕒 Time/Date Tool Function
# ----------------------------
def get_time_info(timezone: str = "UTC", format_type: str = "full"):
    """Get current time and date information for a timezone"""
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        formats = {
            "full": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "timezone": timezone,
            "timestamp": formats.get(format_type, formats["full"]),
            "day_of_week": current_time.strftime("%A"),
            "unix_timestamp": int(current_time.timestamp())
        }
    except Exception as e:
        return {"error": f"Failed to get time info: {str(e)}"}

# ----------------------------
# 📏 Unit Converter Tool Function
# ----------------------------
def convert_units(value: float, from_unit: str, to_unit: str, category: str = "length"):
    """Convert between different units of measurement"""
    try:
        conversions = {
            "length": {
                "meters": 1,
                "kilometers": 0.001,
                "miles": 0.000621371,
                "feet": 3.28084,
                "inches": 39.3701
            },
            "temperature": {
                "celsius": lambda x: x,
                "fahrenheit": lambda x: (x * 9/5) + 32,
                "kelvin": lambda x: x + 273.15
            },
            "weight": {
                "kilograms": 1,
                "pounds": 2.20462,
                "ounces": 35.274,
                "grams": 1000
            }
        }
        
        if category not in conversions:
            return {"error": f"Unknown category: {category}"}
        
        if category == "temperature":
            # Special handling for temperature
            if from_unit == "celsius":
                celsius = value
            elif from_unit == "fahrenheit":
                celsius = (value - 32) * 5/9
            elif from_unit == "kelvin":
                celsius = value - 273.15
            else:
                return {"error": f"Unknown temperature unit: {from_unit}"}
            
            result = conversions[category][to_unit](celsius)
        else:
            # Standard unit conversion
            base_value = value / conversions[category].get(from_unit, 1)
            result = base_value * conversions[category].get(to_unit, 1)
        
        return {
            "original_value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "converted_value": round(result, 2),
            "category": category
        }
    except Exception as e:
        return {"error": f"Conversion failed: {str(e)}"}

# ----------------------------
# 🛠 Tool Definitions
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

calculator_tool = {
    "name": "calculate",
    "description": "Perform mathematical calculations (add, subtract, multiply, divide, power, sqrt, modulo)",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "Mathematical operation to perform",
                "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt", "modulo"]
            },
            "a": {
                "type": "number",
                "description": "First operand"
            },
            "b": {
                "type": "number",
                "description": "Second operand (not required for sqrt)"
            }
        },
        "required": ["operation", "a"]
    }
}

time_tool = {
    "name": "get_time_info",
    "description": "Get current time and date information for a specific timezone",
    "parameters": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone name (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo')"
            },
            "format_type": {
                "type": "string",
                "description": "Format type: 'full', 'date', 'time', or 'datetime'",
                "enum": ["full", "date", "time", "datetime"]
            }
        },
        "required": ["timezone"]
    }
}

unit_converter_tool = {
    "name": "convert_units",
    "description": "Convert between different units of measurement",
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "Value to convert"
            },
            "from_unit": {
                "type": "string",
                "description": "Unit to convert from"
            },
            "to_unit": {
                "type": "string",
                "description": "Unit to convert to"
            },
            "category": {
                "type": "string",
                "description": "Category of measurement: 'length', 'temperature', or 'weight'",
                "enum": ["length", "temperature", "weight"]
            }
        },
        "required": ["value", "from_unit", "to_unit", "category"]
    }
}

# Register all tools
registry.register("get_weather", get_weather, weather_tool)
registry.register("calculate", calculate, calculator_tool)
registry.register("get_time_info", get_time_info, time_tool)
registry.register("convert_units", convert_units, unit_converter_tool)

# ----------------------------
# 🤖 Create Gemini Model with All Tools
# ----------------------------
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=registry.tool_definitions
)

chat = model.start_chat()

# ----------------------------
# 💡 Helper Functions
# ----------------------------
def print_separator():
    """Print a visual separator"""
    print("\n" + "="*60 + "\n")

def display_help():
    """Display available commands and tools"""
    print("\n📚 Available Commands:")
    print("- 'help': Show this help message")
    print("- 'tools': List all available tools")
    print("- 'quit' or 'exit': Exit the program")
    print("\n🛠 Available Tools:")
    print(registry.list_tools())
    print_separator()

def process_tool_call(chat, function_call):
    """Process a single tool call and return response"""
    tool_name = function_call.name
    args = dict(function_call.args)
    
    print(f"🔧 Calling tool: {tool_name}")
    print(f"📝 Arguments: {json.dumps(args, indent=2)}")
    
    # Execute the tool
    result = registry.execute(tool_name, **args)
    
    print(f"✅ Result: {json.dumps(result, indent=2)}")
    print_separator()
    
    # Send tool result back to Gemini
    response = chat.send_message(
        genai.types.Part.from_function_response(
            name=tool_name,
            response=result
        )
    )
    
    return response

# ----------------------------
# 💬 Main Conversation Loop
# ----------------------------
def main():
    """Main conversation loop with multi-turn support"""
    print("\n🤖 Gemini Tool Assistant Started!")
    print("Type 'help' for available commands and tools")
    print_separator()
    
    while True:
        try:
            user_query = input("You: ").strip()
            
            # Handle special commands
            if user_query.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_query.lower() == 'help':
                display_help()
                continue
            elif user_query.lower() == 'tools':
                print("\n🛠 Available Tools:")
                print(registry.list_tools())
                print_separator()
                continue
            elif not user_query:
                continue
            
            # Send message to Gemini
            response = chat.send_message(user_query)
            
            # Handle potential multiple tool calls in sequence
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Check if response contains a function call
                if (response.candidates and 
                    response.candidates[0].content.parts and 
                    response.candidates[0].content.parts[0].function_call):
                    
                    function_call = response.candidates[0].content.parts[0].function_call
                    response = process_tool_call(chat, function_call)
                    
                else:
                    # No more function calls, print final response
                    print("🤖 Gemini:")
                    print(response.text)
                    print_separator()
                    break
            
            if iteration >= max_iterations:
                logging.warning("Max tool call iterations reached")
                print("⚠️  Maximum tool call iterations reached")
                print_separator()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logging.error(f"Error in conversation loop: {str(e)}")
            print(f"❌ Error: {str(e)}")
            print("Please try again or type 'help' for assistance")
            print_separator()

if __name__ == "__main__":
    main()