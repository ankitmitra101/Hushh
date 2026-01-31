# Hushh - AI Shopping Concierge

Your personal AI shopping assistant that remembers your preferences and helps you find the perfect products.

![Hushh Landing Page](https://via.placeholder.com/800x400?text=Hushh+AI+Shopping+Concierge)

## Features

- 🧠 **Smart Memory** - Remembers what you like and avoids what you don't
- 🎯 **Personalized** - AI-curated results matching your style
- 💬 **Natural Chat** - Just describe what you want in plain words
- 🔍 **Intelligent Search** - Filters by size, material, brand, style

## Quick Start (Plug & Play)

The easiest way to run **Hushh** locally, even from a zip file.

### Option 1: One-Click Script (Recommended)

**Windows:**
1. Double-click `run_locally.bat` inside the folder.
2. It will automatically:
   - Create a virtual environment & install Python dependencies.
   - Install React frontend dependencies.
   - Start both servers and open your browser to the app.

**Mac / Linux:**
1. Open terminal in the folder.
2. Run: `bash run_locally.sh`

> **Note:** On first run, it will create a `.env` file. You may need to open it and add your `OPENAI_API_KEY` (Groq API Key) if the app doesn't respond.

---

### Option 2: Manual Setup

#### Backend
```bash
# Setup Env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit .env with your API key

# Run
uvicorn main:app --reload
```

#### Frontend
```bash
cd hushh-react-frontend
npm install
cp .env.example .env
npm run dev
```

---

## Deployment (Render/Vercel)

This project is configured for easy deployment.

**Backend (Render/Railway/Heroku):**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Env Vars:** `OPENAI_API_KEY` (Required)

**Frontend (Vercel/Netlify):**
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Env Vars:** `VITE_BACKEND_URL` (Set to your deployed backend URL)

## Project Structure

```
Hushh/
├── main.py                    # FastAPI backend
├── requirements.txt           # Python dependencies
├── agent_core/                # AI Agent logic
│   └── logic.py               # Shopping agent with sessions
├── mcp_server/                # MCP Tools (search, memory)
│   └── server.py
├── data/                      # Product catalog
│   └── catalog.json           # 28 sample products
└── hushh-react-frontend/      # React Frontend
    ├── src/
    │   ├── App.jsx            # Main app
    │   └── components/        # UI components
    └── package.json
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agents/run` | Send a shopping query |
| POST | `/agents/clear` | Clear conversation history |
| GET | `/agents/session/{id}` | Get session info |
| GET | `/health` | Health check |

---

## Customization

### Add Products

Edit `data/catalog.json` to add your own products:

```json
{
  "product_id": "your-001",
  "title": "Product Name",
  "price_inr": 1500,
  "brand": "Your Brand",
  "category": "footwear",
  "sub_category": "sneakers",
  "size": "9",
  "material": "Leather",
  "style_keywords": ["minimal", "white", "casual"]
}
```

### Categories

The system supports ANY category. Just set the `category` field:
- `footwear`, `apparel`, `accessories` (built-in)
- `toys`, `electronics`, `food`, `books` (or any custom category)

---

## Tech Stack

- **Backend**: Python, FastAPI, Groq (Llama 3.3)
- **Frontend**: React, Vite
- **AI**: MCP (Model Context Protocol) for tool use

---

## License

MIT

---

**Built with ❤️ using Hushh AI Platform**