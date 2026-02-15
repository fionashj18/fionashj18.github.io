"""
Chat backend for "Chat with Fiona" - uses Google Gemini API.
Deploy to Render.com as a Web Service.
Set GEMINI_API_KEY in Render Environment Variables.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# Fiona's personality - customize this to match you!
SYSTEM_PROMPT = """You are Fiona Shi, an ECE undergrad at Carnegie Mellon University. 
You're passionate about hardware development, software engineering, circuit design, and computer architecture.
You like working with Python, C, Arduino, and Verilog.
Be friendly, helpful, and conversational. Keep responses concise (a few sentences).
If asked about yourself, draw from this: you're into tech, building things, and learning. 
Don't pretend to browse the web or access real-time info—just chat naturally."""


def get_gemini_response(messages: list[dict]) -> str:
    """Send conversation to Gemini and return the model's reply."""
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Build chat history for Gemini (user/model alternation)
    # Last message must be from user - we send that via send_message
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)
    last_msg = messages[-1] if messages else {"content": "Hi!"}
    response = chat.send_message(last_msg["content"])
    return response.text


@app.route("/health", methods=["GET"])
def health():
    """Health check for Render."""
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    """
    Accepts JSON: { "messages": [ {"role": "user", "content": "..."}, ... ] }
    Returns JSON: { "reply": "..." } or { "error": "..." }
    """
    try:
        data = request.get_json()
        if not data or "messages" not in data:
            return jsonify({"error": "Missing 'messages' array"}), 400

        messages = data["messages"]
        if not isinstance(messages, list):
            return jsonify({"error": "messages must be an array"}), 400

        # Validate each message
        for m in messages:
            if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
                return jsonify({"error": "Each message must have role 'user' or 'assistant' and content"}), 400
            if "content" not in m or not isinstance(m["content"], str):
                return jsonify({"error": "Each message must have a string 'content'"}), 400
            if not m["content"].strip():
                return jsonify({"error": "Message content cannot be empty"}), 400

        if not messages or messages[-1]["role"] != "user":
            return jsonify({"error": "Last message must be from the user"}), 400

        normalized = [{"role": m["role"], "content": m["content"].strip()} for m in messages]
        reply = get_gemini_response(normalized)

        return jsonify({"reply": reply})

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
