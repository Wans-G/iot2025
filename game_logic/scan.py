from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import base64
import json
import os
import sys
from openai import OpenAI

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

# --- Analysis Functions ---

def analyze_tile_background(image_path):
    """Analyzes a single Catan tile image for its number, type, and resource.
       Returns a JSON object string without list wrappers."""
    print(f"Analyzing tile details for: {image_path}", file=sys.stderr)

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    prompt = (
        "Analyze the provided image, which shows a single Catan game tile.\n"
        "Focus ONLY on the central hexagonal tile itself.\n"
        "1. Identify the number token printed on the tile. If obscured by the robber or it is desert with no number at all, return 0.\n"
        "2. Identify the visual terrain type (Forest, Pasture, Field, Hill, Mountain, Desert).\n"
        "3. Map terrain to resource (Wood, Sheep, Wheat, Brick, Ore, None).\n"
        "Return ONLY a JSON array with one object: {\"number\": int, \"type\": string, \"resource\": string}."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=200,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        # Parse JSON and unwrap list
        data = json.loads(result)
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
            return json.dumps(data[0])
        elif isinstance(data, dict):
            return json.dumps(data)
        else:
            print(f"Unexpected tile details format: {result}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Error during tile details analysis: {e}", file=sys.stderr)
        return None


def analyze_single_tile(image_path):
    """Analyzes a single Catan tile image for surrounding settlements/cities and robber.
       Returns a JSON object string."""
    print(f"Analyzing tile image: {image_path}", file=sys.stderr)

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    prompt = (
        "Analyze the provided image, which shows a single Catan game tile and potentially pieces on the vertices around it.\n"
        "1. Identify settlements (type=1) and cities (type=2) on surrounding vertices with their colors.\n"
        "2. Check whether the number token on the hexagonal tile is visible. If a silver circular token (robber) is placed in the center of the tile and the number is not visible, return true. Otherwise, if no silver circular token (robber) is placed in the center of the tile, return false.\n"
        "Return ONLY a JSON object with keys 'vertices' and 'robber'."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=300,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        # Validate JSON object
        if result.strip().startswith("{") and result.strip().endswith("}"):
            json.loads(result)
            return result
        else:
            print(f"Unexpected single tile format: {result}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Error during single tile analysis: {e}", file=sys.stderr)
        return None

# --- Execution ---
if __name__ == "__main__":
    image_to_analyze = IMAGE_PATH
    print(f"Using image: {os.path.abspath(image_to_analyze)}", file=sys.stderr)

    # First, get tile details
    details = analyze_tile_background(image_to_analyze)
    if details:
        print(details)
    else:
        print("{\"error\": \"Failed to analyze tile details.\"}")
        sys.exit(1)

    # Next, get surrounding piece analysis
    surroundings = analyze_single_tile(image_to_analyze)
    if surroundings:
        print(surroundings)
    else:
        print("{\"error\": \"Failed to analyze surrounding pieces.\"}")
        sys.exit(1)
