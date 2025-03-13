import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = "AIzaSyD9SqGrU4fP54MPwc5KIL7bdUWNLgnzp24"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add these headers to your responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def analyze_text(text):
    """Analyze text using Gemini"""
    prompt = f"""Analyze this meeting transcript and provide a detailed analysis in markdown format:
                # NLP Analysis
                ## Text Overview
                - Word frequencies and key terms
                - Important entities and roles
                - Key metrics mentioned
                
                ## Content Analysis
                - Main discussion topics
                - Timeline and deadlines
                - Critical metrics and numbers

                Meeting Transcript:
                {text}
                """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def summarize_text(text):
    """Generate summary using Gemini"""
    prompt = f"""Create a clear, concise summary of this meeting in markdown format with these sections:
                # Meeting Summary
                ## Key Points
                ## Decisions
                ## Action Items
                ## Next Steps

                Keep it brief and focused on the most important information.

                Meeting Transcript:
                {text}
                """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename.endswith('.txt'):
            transcript = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Please upload a .txt file"}), 400
    else:
        return jsonify({"error": "No file provided"}), 400

    # Get both analysis and summary from Gemini
    analysis = analyze_text(transcript)
    summary = summarize_text(transcript)
    
    # Convert only the summary to speech
    engine = pyttsx3.init()
    engine.say(summary)
    engine.runAndWait()
    
    return jsonify({
        "analysis": analysis,
        "summary": summary
    })

@app.route("/transcribe", methods=["POST"])
def transcribe():
    transcript = request.json.get('transcript', '')
    if not transcript:
        return jsonify({"error": "No transcript provided"}), 400
        
    # Get both analysis and summary from Gemini
    analysis = analyze_text(transcript)
    summary = summarize_text(transcript)
    
    # Convert only the summary to speech
    engine = pyttsx3.init()
    engine.say(summary)
    engine.runAndWait()
    
    return jsonify({
        "analysis": analysis,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 