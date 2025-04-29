import base64
import json
import os
from openai import OpenAI

# --- Configuration ---
# source .venv/bin/activate
IMAGE_PATH = "game_logic/test_pic_0.jpg"
USE_MOCK_API = False # Set to True to use mock data instead of making real API calls

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", MOCK_API_KEY))


# --- Helper Functions ---
def encode_image(image_path):
    """Encodes the image at the given path to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None

def clean_json_response(response_str):
    """Cleans potential markdown fences from API JSON response."""
    if not response_str:
        return None
    cleaned_str = response_str.strip()
    if cleaned_str.startswith("```json"):
        cleaned_str = cleaned_str[len("```json"):].strip()
    if cleaned_str.endswith("```"):
        cleaned_str = cleaned_str[:-len("```")].strip()
    return cleaned_str

def call_openai_api(base64_image, prompt, analysis_type):
    """Calls the OpenAI API with a specific prompt."""
    print(f"\n--- Sending {analysis_type} Prompt to OpenAI --- ")
    # print(prompt) # Optionally print the full prompt for debugging
    print(f"-------------------------------------------")

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
            max_tokens=1000, # Adjust as needed
            response_format={ "type": "json_object" }, # Request JSON output directly if using compatible models
        )
        raw_response = response.choices[0].message.content
        print(f"\n--- Received Raw {analysis_type} Response from OpenAI ---")
        # print(raw_response) # Optionally print raw response for debugging
        print(f"---------------------------------------------------")
        return raw_response
    except Exception as e:
        print(f"An error occurred during the OpenAI API call for {analysis_type}: {e}")
        return None


# --- MOCK Responses ---
def mock_hex_response():
    print("--- MOCKING Hex Analysis Response ---")
    return """
    {
      "hexes": [
        {"number": 8, "resource": "Hill", "has_robber": false},
        {"number": 10, "resource": "Forest", "has_robber": false},
        {"number": 2, "resource": "Pasture", "has_robber": false},
        {"number": 11, "resource": "Forest", "has_robber": false},
        {"number": 9, "resource": "Field", "has_robber": false},
        {"number": 8, "resource": "Mountain", "has_robber": false},
        {"number": 3, "resource": "Field", "has_robber": false},
        {"number": 9, "resource": "Pasture", "has_robber": false},
        {"number": 5, "resource": "Mountain", "has_robber": false},
        {"number": 0, "resource": "Desert", "has_robber": true},
        {"number": 12, "resource": "Pasture", "has_robber": false},
        {"number": 6, "resource": "Forest", "has_robber": false},
        {"number": 3, "resource": "Hill", "has_robber": false},
        {"number": 6, "resource": "Field", "has_robber": false},
        {"number": 11, "resource": "Hill", "has_robber": false},
        {"number": 4, "resource": "Mountain", "has_robber": false},
        {"number": 5, "resource": "Forest", "has_robber": false},
        {"number": 4, "resource": "Field", "has_robber": false}
      ]
    }
    """

def mock_vertex_response():
    print("--- MOCKING Vertex Analysis Response ---")
    # Mock response for an empty board as per test_pic_0.jpg
    return """
    {
      "vertices": [
          # Empty because test_pic_0.jpg has no pieces.
          # Example if pieces existed:
          # {"type": 1, "color": "blue", "adjacent_hex_numbers": [9, 5, 8]},
          # {"type": 2, "color": "red", "adjacent_hex_numbers": [8, 3, 12]}
      ]
    }
    """

# --- Analysis-Specific Functions ---

prompt_hexes = """
Analyze the Catan board image provided.
Identify ONLY the hexagonal tiles. For each tile, provide:
1. Its resource type based on the visual appearance (e.g., Forest, Pasture, Field, Hill, Mountain, Desert). Use these exact names.
2. The number token on it (integer). Use 0 for the Desert tile.
3. Whether the robber piece is present on this tile (has_robber: boolean).

Return the response ONLY as a JSON object containing a single key: 'hexes'.
'hexes' should be a list of objects, each representing a tile: {"number": <int>, "resource": <str>, "has_robber": <bool>}.
Example: {"hexes": [{"number": 8, "resource": "Hill", "has_robber": false}, ...]}
Do not include any other keys or information in the JSON.
"""

prompt_vertices = """
Analyze the Catan board image provided.
Identify ONLY the vertices (intersections) that currently contain a settlement (type 1) or a city (type 2). Ignore empty vertices.
For each identified occupied vertex, provide:
1. Its type (1 for settlement, 2 for city).
2. Its color (string, e.g., "red", "blue", "orange", "white", or "unknown").
3. The number tokens of the 1, 2, or 3 adjacent hexagonal tiles. Use -1 for edges/water, and 0 for the Desert tile number if adjacent.

Return the response ONLY as a JSON object containing a single key: 'vertices'.
'vertices' should be a list containing ONLY objects for the occupied vertices found.
Each object should follow the format: {"type": <1 or 2>, "color": <string>, "adjacent_hex_numbers": [<int>, <int>, <int>]}.
If no settlements or cities are found, return an empty list for 'vertices'.
Example: {"vertices": [{"type": 1, "color": "blue", "adjacent_hex_numbers": [9, 5, 0]}, {"type": 2, "color": "red", "adjacent_hex_numbers": [4, -1, -1]}]}
Do not include any other keys or information in the JSON.
"""

def parse_hex_response(json_response_str):
    """Parses the JSON response containing hex data."""
    board = []
    cleaned_str = clean_json_response(json_response_str)
    if not cleaned_str:
        print("Error: Empty or invalid hex response string.")
        return board # Return empty list

    try:
        analysis_data = json.loads(cleaned_str)
        if 'hexes' in analysis_data:
            for hex_data in analysis_data['hexes']:
                num = hex_data.get('number')
                # Use provided resource name directly
                resource = hex_data.get('resource', 'Unknown')
                has_robber = hex_data.get('has_robber', False)
                board.append([num, resource, has_robber])
        else:
            print("Warning: 'hexes' key not found in hex analysis response.")
            print("Received data:", analysis_data)

    except json.JSONDecodeError:
        print("Error: Could not decode JSON response for hexes.")
        print("Cleaned string attempt:", cleaned_str)
        print("Original string:", json_response_str)
    except Exception as e:
        print(f"An unexpected error occurred during hex parsing: {e}")

    return board

def parse_vertex_response(json_response_str):
    """Parses the JSON response containing vertex data."""
    vertex_states = []
    cleaned_str = clean_json_response(json_response_str)
    if not cleaned_str:
        print("Error: Empty or invalid vertex response string.")
        return vertex_states # Return empty list

    try:
        analysis_data = json.loads(cleaned_str)
        if 'vertices' in analysis_data:
            for vertex_data in analysis_data['vertices']:
                vertex_type = vertex_data.get('type', 1)
                if not isinstance(vertex_type, int) or vertex_type not in [1, 2]:
                    print(f"Warning: Invalid vertex type '{vertex_type}' found. Defaulting to 1.")
                    vertex_type = 1

                vertex_color = vertex_data.get('color', "unknown")
                if not isinstance(vertex_color, str) or not vertex_color:
                    print(f"Warning: Invalid color '{vertex_color}' found. Defaulting to 'unknown'.")
                    vertex_color = "unknown"

                adj_hex_nums = vertex_data.get('adjacent_hex_numbers', [-1, -1, -1])
                while len(adj_hex_nums) < 3:
                    adj_hex_nums.append(-1)

                processed_nums = []
                for n in adj_hex_nums[:3]:
                    if n is None:
                        processed_nums.append(-1)
                    elif isinstance(n, (int, float)):
                        num_int = int(n)
                        processed_nums.append(num_int if num_int >= -1 else -1) # Allow -1, 0, positive
                    else:
                        processed_nums.append(-1)

                vertex_states.append([vertex_type, vertex_color.lower(), processed_nums])
        else:
            print("Warning: 'vertices' key not found in vertex analysis response.")
            print("Received data:", analysis_data)

    except json.JSONDecodeError:
        print("Error: Could not decode JSON response for vertices.")
        print("Cleaned string attempt:", cleaned_str)
        print("Original string:", json_response_str)
    except Exception as e:
        print(f"An unexpected error occurred during vertex parsing: {e}")


    return vertex_states


# --- Main Orchestration Logic ---
def analyze_catan_board(image_path, use_mock=False):
    """
    Analyzes the Catan board image using separate API calls for hexes and vertices.
    Returns two lists: board_list and vertex_list.
    """
    print(f"Starting Catan board analysis for: {image_path}")
    base64_image = encode_image(image_path)
    if not base64_image:
        return None, None

    board_list = []
    vertex_list = []

    # --- Analyze Hexes ---
    hex_response_str = None
    if use_mock:
        hex_response_str = mock_hex_response()
    else:
        hex_response_str = call_openai_api(base64_image, prompt_hexes, "Hex")

    if hex_response_str:
        board_list = parse_hex_response(hex_response_str)
    else:
        print("Skipping hex parsing due to API call failure.")


    # --- Analyze Vertices ---
    vertex_response_str = None
    if use_mock:
        vertex_response_str = mock_vertex_response()
    else:
        vertex_response_str = call_openai_api(base64_image, prompt_vertices, "Vertex")

    if vertex_response_str:
        vertex_list = parse_vertex_response(vertex_response_str)
    else:
         print("Skipping vertex parsing due to API call failure.")

    return board_list, vertex_list


# --- Execution ---
if __name__ == "__main__":
    # The IMAGE_PATH is relative to the project root where the script is expected to be run.
    # Functions like open() called within the script will resolve this path correctly.
    image_to_analyze = IMAGE_PATH

    print(f"Attempting to load image from: {os.path.abspath(image_to_analyze)}")

    # Set USE_MOCK_API flag at the top of the file to True or False
    board_data, vertex_data = analyze_catan_board(image_to_analyze, use_mock=USE_MOCK_API)

    print("\n--- Final Generated Lists ---")

    print("\nBoard List ([Number, Resource, HasRobber]):")
    if board_data:
         # Use pprint for better formatting if needed: import pprint; pprint.pprint(board_data)
         for item in board_data:
             print(item)
    else:
        print("(No board data generated or parsing failed)")


    print("\nOccupied Vertex States ([Type, Color, [Adjacent Hex Nums]] - 1:Settlement, 2:City):")
    if vertex_data:
        # Use pprint for better formatting if needed: import pprint; pprint.pprint(vertex_data)
        for item in vertex_data:
            print(item)
    else:
        print("(No settlements or cities detected or parsing failed)")
