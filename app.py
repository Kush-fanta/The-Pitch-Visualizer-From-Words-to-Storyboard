import os
import json
import base64
import requests
import google.generativeai as genai
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- AI & API Configuration ---
# Configure the Gemini API client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure the Hugging Face Inference API
IMAGE_MODEL_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": f"Bearer {huggingface_api_key}"}


# --- Flask App Initialization ---
app = Flask(__name__)


# --- Core AI Functions ---
def get_storyboard_scenes_from_gemini(text, style):
    """
    Uses Gemini to perform both scene segmentation and prompt enhancement in a single call.
    Returns a list of dictionaries, where each dict contains a scene and an enhanced prompt.
    """
    print("Calling Gemini with a more constrained prompt...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # This is our new, more direct and constrained "meta-prompt"
        prompt = (
            "Your task is to analyze the following `narrative_text` and break it into logical number of distinct visual scenes. "
            "For each scene, you must extract the core action or description directly from the text to create a `scene_description`. "
            "Then, expand that `scene_description` into a detailed `enhanced_prompt` for an AI image generator, matching the visual style of '{style}'. "
            "**Do not invent new story elements that are not present in the original text.** Base all output strictly on the provided `narrative_text`. "
            "Provide your response ONLY as a valid JSON array of objects, where each object has two keys: 'scene_description' and 'enhanced_prompt'.\n\n"
            "narrative_text: '''{text}'''"
        )

        response = model.generate_content(prompt.format(text=text, style=style))
        
        # Clean up the response and parse the JSON
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        scenes = json.loads(json_response)
        
        print("Successfully got scenes from Gemini.")
        return scenes

    except Exception as e:
        print(f"Error getting scenes from Gemini: {e}")
        return [] # Return an empty list on failure

def generate_image(prompt):
    """Generates an image using the Hugging Face Inference API."""
    print(f"Generating image for prompt: {prompt}")
    try:
        response = requests.post(IMAGE_MODEL_API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
        response.raise_for_status() # Raise an exception for bad status codes
        
        image_bytes = response.content
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print("Image generated successfully.")
        return image_base64
    except requests.exceptions.RequestException as e:
        print(f"Error generating image: {e}")
        return None # Return None if image generation fails


# --- Main Application Pipeline ---
def create_storyboard(text, style):
    """The main pipeline that creates the storyboard data using the new Gemini function."""
    storyboard_panels = []
    
    # Get the scenes and prompts in one go from our new smart function
    scenes = get_storyboard_scenes_from_gemini(text, style)
    
    for scene in scenes:
        enhanced_prompt = scene.get('enhanced_prompt')
        scene_description = scene.get('scene_description')

        if not enhanced_prompt or not scene_description:
            continue # Skip if the scene data is incomplete

        image_data = generate_image(enhanced_prompt)
        
        if image_data:
            storyboard_panels.append({
                "original_text": scene_description,
                "enhanced_prompt": enhanced_prompt,
                "image_data": image_data
            })
            
    return storyboard_panels


# --- Flask Web Routes ---
@app.route('/')
def home():
    """Renders the main input page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handles the form submission and displays the storyboard."""
    if request.method == 'POST':
        narrative_text = request.form['text']
        visual_style = request.form['style']
        
        if not narrative_text or not visual_style:
            return render_template('index.html', error="Please provide a narrative and select a style.")
            
        storyboard_data = create_storyboard(narrative_text, visual_style)
        
        return render_template('storyboard.html', storyboard=storyboard_data)


# --- Main execution ---
if __name__ == '__main__':
    app.run(debug=True)