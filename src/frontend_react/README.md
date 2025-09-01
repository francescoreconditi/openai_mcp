# React Frontend for Chatbot MCP

This is a React-based frontend for the OpenAI + MCP chatbot application.

## Features

- 💬 Real-time chat interface
- 🎤 Voice recording and transcription
- 🔧 MCP tools integration
- 📊 System status monitoring
- 🎨 Modern, responsive UI

## Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

```bash
# Start development server
npm start
```

The application will be available at http://localhost:3000

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Runs the test suite

## Project Structure

```
src/
├── components/       # React components
│   ├── ChatContainer.js
│   ├── Message.js
│   ├── MessageInput.js
│   ├── Sidebar.js
│   └── VoiceRecorder.js
├── services/        # API services
│   ├── audioService.js
│   ├── chatService.js
│   └── healthService.js
├── styles/          # CSS styles
│   ├── App.css
│   ├── ChatContainer.css
│   ├── Message.css
│   ├── MessageInput.css
│   ├── Sidebar.css
│   └── VoiceRecorder.css
├── App.js          # Main app component
└── index.js        # Entry point
```

## Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_MCP_URL=http://localhost:8001
```

## Voice Recording

The voice recording feature uses the Web Audio API to capture audio from the user's microphone. The audio is then sent to the backend for transcription using OpenAI Whisper.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.