"""
Chat backend for "Chat with Fiona" - uses Groq API (Llama).
Deploy to Render.com as a Web Service.
Set GROQ_API_KEY in Render Environment Variables.
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


def get_groq_response(messages: list[dict]) -> str:
    """Send conversation to Groq and return the model's reply."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    client = Groq(api_key=api_key)
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    groq_messages.extend([{"role": m["role"], "content": m["content"]} for m in messages])

    response = client.chat.completions.create(
        messages=groq_messages,
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content


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
        reply = get_groq_response(normalized)

        return jsonify({"reply": reply})

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
