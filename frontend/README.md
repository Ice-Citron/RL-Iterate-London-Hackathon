# Frontend Orchestrator

A web-based orchestrator for managing ethical hacking challenges with AI agents.

## Features

- **Challenge Selection**: Browse and select from available security challenges
- **Agent Execution**: Run the trainee agent on selected challenges
- **Judge Evaluation**: Evaluate agent responses with the LLM judge
- **Real-time Feedback**: See agent responses and judge scores in real-time

## Setup

### 1. Configure Endpoints

The frontend expects the following services:

- **Trainee Agent**: `http://localhost:4000`
  - Endpoint: `POST /complete_task`
  - Request: `{ "task_description": "string" }`
  - Response: `{ "summary": "string" }`

- **Judge Server**: `http://localhost:8080`
  - Endpoint: `POST /verify`
  - Request: `{ "task_description": "string", "agent_response": "string" }`
  - Response: `{ "score": number, "summary": "string" }`

- **Frontend**: `http://localhost:8000`

### 2. Serve the Frontend

You can use any static file server. Here are a few options:

#### Option 1: Python HTTP Server
```bash
cd frontend
python -m http.server 8000
```

#### Option 2: Node.js http-server
```bash
npm install -g http-server
cd frontend
http-server -p 8000
```

#### Option 3: VS Code Live Server
Install the "Live Server" extension and right-click on `index.html` → "Open with Live Server"

### 3. Start Required Services

Make sure both services are running:

```bash
# Terminal 1: Start the judge server
uvicorn server:app --host 127.0.0.1 --port 8080

# Terminal 2: Start your trainee agent on port 4000
# (Your agent implementation)

# Terminal 3: Serve the frontend
cd frontend
python -m http.server 8000
```

### 4. Open in Browser

Navigate to `http://localhost:8000` in your web browser.

## Usage

1. **Select a Challenge**: Click on any challenge card in the left panel
2. **Run Agent**: Click the "Run Agent" button to execute the trainee agent
3. **View Response**: The agent's response will appear in the middle panel
4. **Evaluate**: Click "Evaluate Response" to get the judge's assessment
5. **View Score**: The judge's score and summary will appear in the right panel

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # All styling and animations
├── script.js           # Application logic and API calls
├── challenges.json     # Challenge definitions
└── README.md          # This file
```

## Customization

### Adding New Challenges

Edit `challenges.json`:

```json
{
  "id": "unique-id",
  "title": "Challenge Title",
  "description": "What the agent needs to accomplish",
  "difficulty": "Easy|Medium|Hard",
  "category": "Category Name"
}
```

### Changing API Endpoints

Edit the `CONFIG` object in `script.js`:

```javascript
const CONFIG = {
    AGENT_API: 'http://localhost:4000',
    JUDGE_API: 'http://localhost:8080',
    FRONTEND_PORT: 8000
};
```

## CORS Issues

If you encounter CORS errors, make sure your backend services include appropriate CORS headers. For FastAPI (judge server), add:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
