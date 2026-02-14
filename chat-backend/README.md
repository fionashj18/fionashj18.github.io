# Chat with Fiona - Backend

Flask backend that powers the "Chat with Fiona" AI chatbot using Google Gemini.

## Setup

1. Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com).

2. Create a virtual environment and install dependencies:

```bash
cd chat-backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run locally (set your API key):

```bash
export GEMINI_API_KEY=your_key_here
python app.py
```

## Deploy to Render

1. Push the backend to GitHub:
   - **Option A:** Create a new repo with the contents of `chat-backend/` as the root.
   - **Option B:** If using the same portfolio repo, set Render's **Root Directory** to `chat-backend`.

2. Go to [render.com](https://render.com) → New → Web Service.

3. Connect your repo, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. Add environment variable: `GEMINI_API_KEY` = your API key.

5. After deploy, copy the public URL (e.g. `https://chat-fiona-xyz.onrender.com`).

6. In `chat.html` on your portfolio, replace `API_URL` with your Render URL:
   ```javascript
   const API_URL = 'https://chat-fiona-xyz.onrender.com';
   ```
