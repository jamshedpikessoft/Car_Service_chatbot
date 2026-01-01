# Car Service Chatbot

A smart car service booking chatbot powered by Google Gemini AI, FastAPI, and the OpenAI Agent SDK. This system allows customers to check available time slots and book car service appointments through an interactive conversational interface.

## Features

- 🤖 **AI-Powered Chatbot**: Natural conversation using Google Gemini AI
- 📅 **Slot Management**: Check available time slots in real-time
- 🎫 **Booking System**: Book appointments with automatic ticket generation
- 🔄 **MCP Integration**: Model Context Protocol for tool communication
- ⚡ **FastAPI Backend**: High-performance REST API for slot and booking management

## System Architecture

The system consists of three main components:

1. **FastAPI Backend** ([fastapi_backend.py](fastapi_backend.py)) - REST API server managing slots and bookings
2. **MCP Server** ([mcp_server_stdio.py](mcp_server_stdio.py)) - Middleware connecting chatbot to FastAPI
3. **Chatbot Agent** ([chatbot_agent.py](chatbot_agent.py)) - AI-powered conversational interface

## Prerequisites

- Python 3.10 or higher
- Google Gemini API Key
- Terminal/Command Prompt

## Installation Guide

### Step 1: Create Virtual Environment

A virtual environment isolates your project dependencies from other Python projects.

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You'll see `(venv)` prefix in your terminal when the virtual environment is active.

### Step 2: Install Dependencies

With your virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework for the backend API
- Uvicorn - ASGI server to run FastAPI
- Google Generative AI - Gemini model SDK
- OpenAI Agents - Agent framework
- LiteLLM - Model provider integration
- MCP - Model Context Protocol
- And other dependencies

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# On Windows
type nul > .env

# On macOS/Linux
touch .env
```

Add the following configuration to your `.env` file:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini/gemini-2.0-flash-exp

# FastAPI Server Configuration
FASTAPI_URL=http://localhost:8000
```

**To get your Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in the `.env` file

## How to Run the Application

The application requires running two Python files in a specific order:

### Terminal 1: Start FastAPI Backend Server

First, start the FastAPI backend server that manages slots and bookings.

```bash
# Make sure virtual environment is activated
python fastapi_backend.py
```

**Expected Output:**
```
============================================================
🚗 Car Service Booking FastAPI Server
============================================================
Server URL: http://localhost:8000
API Docs: http://localhost:8000/docs
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The FastAPI server will:
- Run on `http://localhost:8000`
- Provide interactive API documentation at `http://localhost:8000/docs`
- Manage available time slots (9 AM, 11 AM, 1 PM, 3 PM, 5 PM)
- Handle booking requests and generate ticket IDs

**Keep this terminal window running!**

### Terminal 2: Start Chatbot Agent

Open a **new terminal window** and start the chatbot agent.

```bash
# Navigate to project directory
cd /path/to/Car_Service_chatbot

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run chatbot
python chatbot_agent.py
```

**Expected Output:**
```
You:
```

The chatbot is now ready to interact!

## How to Use the Chatbot

### Example Conversation Flow

```
You: Hi, I want to book a car service

CarBot: Hello! I'd be happy to help you book a car service. When would you
like to schedule your appointment? (today, tomorrow, or a specific date)

You: Tomorrow

CarBot: Let me check available slots for tomorrow (2026-01-02)...

Available slots for 2026-01-02:
• 09:00 AM
• 11:00 AM
• 01:00 PM
• 03:00 PM
• 05:00 PM

Which time works best for you?

You: 3 PM

CarBot: Great! Please provide the following details:
• Your name
• Phone number
• Car model
• Service type

You: John Doe, 923001234567, Honda Civic 2024, Oil Change

CarBot: Please confirm your booking details:
👤 Name: John Doe
📞 Phone: 923001234567
🚗 Car: Honda Civic 2024
🔧 Service: Oil Change
📅 Date: 2026-01-02
⏰ Time: 03:00 PM

Is this correct?

You: Yes

CarBot: ✅ Booking Confirmed!
🎫 Ticket ID: A7X9K2M5
👤 Name: John Doe
📞 Phone: 923001234567
🚗 Car: Honda Civic 2024
🔧 Service: Oil Change
📅 Date: 2026-01-02
⏰ Time: 03:00 PM

Your appointment has been successfully booked! Please save your ticket ID.
```

### Commands

- Type your messages naturally to interact with the bot
- Type `exit`, `quit`, or `bye` to end the conversation
- Press `Ctrl+C` to force quit

## Project Structure

```
Car_Service_chatbot/
│
├── fastapi_backend.py      # FastAPI REST API server
├── mcp_server_stdio.py     # MCP server middleware
├── chatbot_agent.py        # AI chatbot agent
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── README.md              # This file
```

## API Endpoints

The FastAPI backend provides the following endpoints:

### GET /
Health check endpoint
```json
{
  "status": "running",
  "service": "Car Service Booking API",
  "version": "1.0.0"
}
```

### GET /api/slots
Get available time slots

**Query Parameters:**
- `date` (optional): Filter by date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "total_slots": 5,
  "slots": [
    {
      "date": "2026-01-02",
      "time": "09:00 AM",
      "available": true
    }
  ]
}
```

### POST /api/book
Book a car service appointment

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "phone": "923001234567",
  "car_model": "Honda Civic 2024",
  "service_type": "Oil Change",
  "date": "2026-01-02",
  "time": "03:00 PM"
}
```

**Response:**
```json
{
  "success": true,
  "ticket_id": "A7X9K2M5",
  "customer_name": "John Doe",
  "phone": "923001234567",
  "car_model": "Honda Civic 2024",
  "service_type": "Oil Change",
  "date": "2026-01-02",
  "time": "03:00 PM",
  "message": "Booking confirmed! Ticket: A7X9K2M5"
}
```

## Troubleshooting

### Issue: "GEMINI_API_KEY environment variable not found"
**Solution:** Make sure your `.env` file exists and contains a valid Gemini API key.

### Issue: "Error initializing chatbot"
**Solution:** Ensure the FastAPI backend is running on `http://localhost:8000` before starting the chatbot.

### Issue: "Connection refused"
**Solution:** Check if the FastAPI server is running. You should see it running in Terminal 1.

### Issue: "Module not found"
**Solution:** Make sure you've activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Chatbot not responding
**Solution:**
1. Check if both terminals are running
2. Verify your internet connection (required for Gemini API)
3. Check your Gemini API key is valid and has quota remaining

## Deactivating Virtual Environment

When you're done working with the project:

```bash
deactivate
```

This will return you to your system's default Python environment.

## Technologies Used

- **Python 3.8+** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server
- **Google Gemini AI** - Large language model for conversational AI
- **OpenAI Agent SDK** - Agent framework for building AI agents
- **LiteLLM** - Unified interface for multiple LLM providers
- **MCP (Model Context Protocol)** - Protocol for tool integration
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure environment variables are correctly set
4. Make sure both servers are running in the correct order

---

**Made with ❤️ using Google Gemini AI and FastAPI**