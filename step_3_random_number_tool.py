import random
import re




#method to generate random number within a specified range
def random_number_generator(min, max):
    random_number = random.randint(min, max)
    return random_number


#sets and gets our tool definition
def get_tool_definition():
    random_number = {
        "toolSpec": {
            "name": "random_number_generator",
            "description": "Generate a random number within a specified range",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "The specified minimum value for the random number"
                        },
                        "max": {
                            "type": "number",
                            "description": "The specified maximum value for the random number"
                        }
                    },
                    "required": ["min", "max"]
                }
            }
        }
    }

    tool_definition = []
    tool_definition.append(random_number)

    return tool_definition
