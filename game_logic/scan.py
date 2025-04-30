from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import base64
import json
import os
from openai import OpenAI
import sys

# --- Configuration ---
# API Key is expected to be in an environment variable named OPENAI_API_KEY
API_KEY = os.environ.get("OPENAI_API_KEY")
# Specify the path to the single tile image you want to analyze
IMAGE_PATH = "game_logic/0_tile.jpg"

# --- Initialize OpenAI Client ---
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
    print("Please set the environment variable before running the script.", file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

# --- Helper Function ---
def encode_image(image_path):
    """Encodes the image at the given path to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}", file=sys.stderr)
        return None

# --- Core Analysis Function ---
def analyze_single_tile(image_path):
    """Analyzes a single Catan tile image for surrounding settlements/cities and robber.
       Returns the analysis result as a JSON string, or None on failure.
    """
    print(f"Analyzing tile image: {image_path}", file=sys.stderr) # Print status to stderr

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    prompt = """
    Analyze the provided image, which shows a single Catan game tile and potentially pieces on the vertices around it.
    Focus ONLY on the following tasks:
    1.  Identify pieces located on the vertices *surrounding* the central tile.
        - If a piece is a house-shaped pentagon (a Settlement), record its type as 1 and its color (e.g., "red", "blue", "orange", "white").
        - If a piece is an L-shaped bent piece (a City), record its type as 2 and its color.
        - Ignore any long, thin road pieces.
        - Compile these findings into a list named 'vertices'. Each item in the list should be a two-element list: [type, color_string]. Example: [1, "blue"].
    2.  Look at the number token on the *central tile* itself.
        - Determine if this number is obscured by a silver or grey circular Robber piece.
        - Create a list named 'robber' containing a single string: "True" if the robber is present on the number, "False" otherwise.

    Return ONLY a valid JSON object containing exactly two keys: "vertices" and "robber".
    The value for "vertices" should be the list of identified settlements/cities (e.g., [[1, "blue"], [2, "red"]]). If no settlements or cities are found on the surrounding vertices, the list should be empty ([]).
    The value for "robber" should be the list containing the single boolean string (e.g., ["True"] or ["False"]).
    Do not include any explanations, markdown formatting, or any text outside the JSON structure.
    Example of the exact output format expected:
    {"vertices": [[1, "red"]], "robber": ["False"]}
    Another example:
    {"vertices": [], "robber": ["True"]}
    Another example:
    {"vertices": [[1, "white"], [2, "orange"]], "robber": ["False"]}
    """

    print(f"Sending analysis request to OpenAI...", file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            max_tokens=300, # Reduced max_tokens as output is expected to be small
            temperature=0.1, # Lower temperature for more deterministic output
            response_format={ "type": "json_object" },
        )
        json_result = response.choices[0].message.content
        print(f"Received response from OpenAI.", file=sys.stderr)
        # Basic validation: Check if it looks like a JSON object
        if json_result and json_result.strip().startswith("{") and json_result.strip().endswith("}"):
             # Attempt to parse to ensure it's valid JSON before returning
             try:
                 json.loads(json_result)
                 return json_result
             except json.JSONDecodeError as json_err:
                 print(f"Error: OpenAI response was not valid JSON: {json_err}", file=sys.stderr)
                 print(f"Received content: {json_result}", file=sys.stderr)
                 return None
        else:
            print(f"Error: OpenAI response did not appear to be a JSON object.", file=sys.stderr)
            print(f"Received content: {json_result}", file=sys.stderr)
            return None

    except Exception as e:
        print(f"An error occurred during the OpenAI API call: {e}", file=sys.stderr)
        return None

# --- Execution ---
if __name__ == "__main__":
    # Use IMAGE_PATH directly, as it's relative to the execution directory (project root)
    image_to_analyze = IMAGE_PATH

    print(f"Using image: {os.path.abspath(image_to_analyze)}", file=sys.stderr) # Print absolute path for logging

    # Analyze the image using the relative path
    result_json = analyze_single_tile(image_to_analyze) # <-- Pass the correct relative path

    # Print the resulting JSON string directly to standard output
    if result_json:
        print(result_json) # Print JSON to stdout
    else:
        print("{\"error\": \"Failed to get analysis result.\"}") # Print error JSON to stdout
        sys.exit(1) # Exit with error code if analysis failed
