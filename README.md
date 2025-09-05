# The Pitch Visualizer

The Pitch Visualizer is a web application designed to bridge the gap between narrative storytelling and visual presentation. It takes a block of text, such as a customer success story or a sales pitch, and automatically generates a multi-panel visual storyboard. This tool leverages a multi-AI system to intelligently deconstruct the narrative into key moments and translate them into compelling, descriptive prompts for image generation.

### Key Capabilities
* **Intelligent Scene Segmentation**: Uses Google's Gemini model to analyze a narrative and break it down into logical, context-aware visual scenes.
* **Advanced Prompt Engineering**: For each scene, Gemini acts as an expert prompt engineer, enhancing the simple text into a rich, detailed, and cinematic prompt tailored for an AI image generator.
* **Dynamic Storyboard Generation**: The application can dynamically create storyboards of variable length based on the complexity of the input text.
* **User-Selectable Styles**: Allows the user to choose from a variety of artistic styles to ensure the final visuals match the desired tone of the pitch.

---

## How It Works: The AI Pipeline

The application functions as a sophisticated pipeline that processes text through multiple AI stages to produce a visual output.

1.  **User Input**: The user provides a narrative and selects a visual style via a simple web interface.
2.  **Gemini (The "Screenwriter")**: The Flask backend sends the entire narrative to the Gemini 1.5 Flash model in a single API call. A carefully crafted "meta-prompt" instructs Gemini to:
    * Act as an expert screenwriter.
    * Deconstruct the narrative into a logical number of key scenes.
    * For each scene, provide both a concise description and a new, dramatically enhanced prompt.
    * Return this entire structure as a clean, predictable JSON object.
3.  **Hugging Face (The "Artist")**: The backend parses the JSON from Gemini. For each enhanced prompt, it makes an API call to the Hugging Face Inference API, which uses the **Stable Diffusion xl base 1.0** model to generate an image.
4.  **Flask & Frontend**: The backend collects the generated images and their corresponding text captions, then renders them in a clean, user-friendly storyboard format on a results page.

---

## Setup and Execution

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/Kush-fanta/The-Pitch-Visualizer-From-Words-to-Storyboard.git](https://github.com/Kush-fanta/The-Pitch-Visualizer-From-Words-to-Storyboard.git)
cd The-Pitch-Visualizer-From-Words-to-Storyboard
```

### 2. Create and Activate Virtual Environment
* **macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
* **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

### 3. Install Dependencies
All required packages are listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys
The application requires API keys from Google and Hugging Face. A `.env.example` file is included with placeholders.

1.  Create your own `.env` file and add your API keys there.
2.  Open the `.env` file and replace the placeholder values with your actual API keys:
    ```
    GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    HUGGINGFACE_API_KEY="YOUR_HUGGINGFACE_API_KEY"
    ```

### 5. Run the Application
```bash
flask run
```
Open your web browser and navigate to `http://127.0.0.1:5000` to use the application.

---

## Design Choices & Prompt Engineering

Our methodology was centered on creating an intelligent, adaptable system rather than a simple chain of API calls.

* **Moving Beyond NLTK**: I initially used NLTK for sentence segmentation but quickly pivoted. NLTK is rule-based and lacks contextual understanding. By delegating this task to **Gemini**, the application can identify true "visual moments" that may span multiple sentences or exist within a single long one.

* **Single, Structured API Call**: My final architecture makes a single call to Gemini to handle both segmentation and prompt enhancement. We instruct the LLM to return a structured **JSON object**. This is a highly robust and efficient design pattern that reduces latency and simplifies the backend logic, as we receive all the necessary text data in one predictable format.

* **Prompt Engineering as Instruction**: My "meta-prompt" is the core of our AI logic. Instead of just asking the LLM a question, we give it a **persona** ("expert screenwriter") and a **strict set of instructions** (deconstruct text, create new prompts, return only JSON, do not invent new story elements). This level of control is key to getting reliable, high-quality output from modern LLMs and represents the core of our "intelligent prompt engineering" methodology.

