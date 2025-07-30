# School Agent Simple - AI-Powered Educational Chatbot

A complete AI chatbot system with multiple models, Grade 9 educational content, and a beautiful UI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
python main.py
```

The backend will start on http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the frontend:
```bash
npm start
```

The frontend will open on http://localhost:3000

## 📚 Features

- **Multiple AI Models**:
  - Study Companion (General academic help)
  - Everest Scholar (School-specific information)
  - Research Scholar (Advanced web research)

- **Grade 9 Content**: Integrated educational PDFs for:
  - Earth Science & Atmosphere
  - Solar System & Space
  - Mathematics (Geometry, Circles, Triangles)
  - Physics (Earthquakes)

- **Modern UI**:
  - No login required
  - Dark/Light mode
  - Keyboard shortcuts (Cmd/Ctrl + K)
  - Export conversations
  - Agent selector (opens upward)

## 🎯 Usage

1. Start both backend and frontend servers
2. Open http://localhost:3000 in your browser
3. Select an AI model from the dropdown
4. Start chatting!

## ⚙️ Configuration

- Backend API: `backend/main.py` (Port 8000)
- Frontend Config: `frontend/src/config.js`
- API Key: Located in `backend/main.py` line 78

## 📁 Project Structure

```
school-agent-simple/
├── backend/           # Python FastAPI backend
│   ├── main.py       # Main server file
│   ├── *.py          # Supporting modules
│   └── chatbot.db    # Database file
├── frontend/          # React frontend
│   ├── src/          # Source code
│   ├── public/       # Static files
│   └── package.json  # Dependencies
└── Grade_9_info/     # Educational PDFs
```

## 🛠️ Troubleshooting

- **Port in use**: Kill existing processes or change ports
- **API errors**: Check backend is running on port 8000
- **Can't select agents**: Clear browser cache and refresh

## 📝 Notes

- The Qwen API key is included for demo purposes
- Database includes pre-indexed Grade 9 content
- All UI improvements have been applied