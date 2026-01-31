# Hushh - AI Shopping Concierge

Your personal AI shopping assistant that remembers your preferences and helps you find the perfect products.

![Hushh Landing Page](https://via.placeholder.com/800x400?text=Hushh+AI+Shopping+Concierge)

## Features

- 🧠 **Smart Memory** - Remembers what you like and avoids what you don't
- 🎯 **Personalized** - AI-curated results matching your style
- 💬 **Natural Chat** - Just describe what you want in plain words
- 🔍 **Intelligent Search** - Filters by size, material, brand, style

## Quick Start (Download → Deploy in 10 minutes)

### Prerequisites

1. **Groq API Key** (Free) - Get one at [console.groq.com](https://console.groq.com)
2. **Render Account** (Free) - Sign up at [render.com](https://render.com)
3. **GitHub Account** - To push your code

### Step 1: Push to Your GitHub

```bash
# Unzip the downloaded file
cd Hushh

# Initialize new repo (if not already a git repo)
git init
git add .
git commit -m "Initial commit"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/Hushh.git
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `hushh-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your Groq API key
5. Click **Create Web Service**
6. Wait for deployment → Note your backend URL (e.g., `https://hushh-backend-xyz.onrender.com`)

### Step 3: Deploy Frontend on Render

1. Go to [render.com](https://render.com) → **New** → **Static Site**
2. Connect the same GitHub repo
3. Configure:
   - **Name**: `hushh-frontend`
   - **Root Directory**: `hushh-react-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - **Key**: `VITE_BACKEND_URL`
   - **Value**: Your backend URL from Step 2
5. Click **Create Static Site**

### Done! 🎉

Your app is live at your Render frontend URL!

---

## Local Development

### Backend

```bash
cd Hushh

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (Groq key)

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn main:app --reload
```

### Frontend

```bash
cd hushh-react-frontend

# Install dependencies
npm install

# Run
npm run dev
```

---

## Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your Groq API key (used via OpenAI client) |
| `PORT` | No | Server port (default: 8000) |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_BACKEND_URL` | ✅ Yes | Your backend URL (e.g., `https://hushh-backend.onrender.com`) |

---

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