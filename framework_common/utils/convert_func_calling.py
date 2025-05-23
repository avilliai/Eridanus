import copy


def convert_gemini_to_openai(gemini_tools):
    openai_functions = []

    for tool in gemini_tools["function_declarations"]:
        #print(tool)
        openai_function = {
            "type": "function",
            "function": {
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "parameters": copy.deepcopy(tool.get("parameters", {}))
            }
        }

        # Ensure 'parameters' has all required fields for OpenAI format
        if "parameters" in openai_function["function"]:
            parameters = openai_function["function"]["parameters"]
            parameters.setdefault("type", "object")
            parameters.setdefault("properties", {})
            parameters.setdefault("required", [])
            parameters["additionalProperties"] = False

        openai_functions.append(openai_function)

    return openai_functions
