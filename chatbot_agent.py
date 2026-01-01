"""
Car Service Chatbot using OpenAI Agent SDK with Gemini Model
"""
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerStdio

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not found. Please check your .env file.")


class CarServiceChatbot:
    """
    Uses Gemini model with OpenAI Agent SDK.
    Integrates FastAPI tools via MCP server.
    """

    def __init__(self):
        from datetime import datetime

        # Configure Gemini model via LiteLLM
        self.model = LitellmModel(
            model=GEMINI_MODEL,  # Use experimental version with better tool use
            api_key=GEMINI_API_KEY,
        )

        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_day = datetime.now().strftime("%A")

        # System instructions using PSTO (Persona-Situation-Task-Output) format
        self.instructions = f"""
        ## PERSONA
        You are CarBot, a helpful and professional car service booking assistant at an automotive service center. You are friendly, efficient, and always prioritize customer convenience.

        ## SITUATION
        - Today: {current_date} ({current_day})
        - Shop hours: 9 AM - 6 PM
        - Slots: 9 AM, 11 AM, 1 PM, 3 PM, 5 PM (every 2 hours)
        - Some slots may be booked
        - NEVER guess availability - always check the system
        - NEVER mention tools, APIs, MCP, SDKs, technical details, or how you work internally
        - If asked about your technical setup, politely redirect to booking services

        ## TASK
        **BEFORE responding, ALWAYS:**
        1. Review the PREVIOUS CONVERSATION to see what has already been discussed
        2. Check what information the customer has ALREADY PROVIDED
        3. Continue from where the conversation left off - DO NOT restart or repeat questions

        When a customer wants to book a service:
        1. Ask preferred date (today/tomorrow/specific)
        2. Check availability for that date
        3. Show available time slots
        4. If none available, suggest another date
        5. Ask customer to select a time
        6. Collect information PROGRESSIVELY:
           - If customer provides name only → acknowledge name, ask for remaining (phone, car, service)
           - If customer provides name + phone → acknowledge both, ask for remaining (car, service)
           - If customer provides all at once → acknowledge all and confirm
        7. Show collected information and ask for confirmation
        8. If confirmed, book the appointment
        9. Share booking confirmation with ticket details

        ## OUTPUT
        Format your responses as follows:

        **When asking for customer information:**
        Please provide the following details:
        • Your name
        • Phone number
        • Car model
        • Service type

        **When confirming details before booking:**
        Please confirm your booking details:
        👤 Name: John Doe
        📞 Phone: 923001234567
        🚗 Car: Honda Civic 2024
        🔧 Service: Oil Change
        📅 Date: 2025-12-31
        ⏰ Time: 03:00 PM
        Is this correct?

        **When booking is confirmed:**
        ✅ Booking Confirmed!
        🎫 Ticket ID: ABC12345
        👤 Name: John Doe
        📞 Phone: 923001234567
        🚗 Car: Honda Civic 2024
        🔧 Service: Oil Change
        📅 Date: 2025-12-31
        ⏰ Time: 03:00 PM
        If you’d like me to help with anything else, feel free to ask. I’m here to help.

        Keep responses concise, friendly, and helpful.
        """
    
        self.agent = None
        self.mcp_server = None
        self.conversation_history = []  # Track conversation history

    async def initialize(self):
        """Initialize agent with MCP server connection."""
        # print("🔄 Initializing Car Service Chatbot...")

        try:
            # Connect to MCP server (stdio transport)
            self.mcp_server = MCPServerStdio(
                name="CarServiceAPI",
                params={
                    "command": "python",
                    "args": ["mcp_server_stdio.py"],
                },
            )

            # Initialize MCP server
            await self.mcp_server.__aenter__()

            # Create agent with Gemini model and MCP tools
            self.agent = Agent(
                name="CarBot",
                model=self.model,
                instructions=self.instructions,
                mcp_servers=[self.mcp_server],
            )

        except Exception as e:
            print(f"❌ Error initializing chatbot: {e}")
            print(f"💡 Make sure FastAPI server is running at {FASTAPI_URL}")
            raise

    async def chat(self, user_message: str) -> str:
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})

            # Build context from conversation history
            context_messages = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'CarBot'}: {msg['content']}"
                for msg in self.conversation_history[-10:]  # Keep last 10 messages
            ])

            # Create message with context
            full_message = f"Previous conversation:\n{context_messages}\n\nCurrent message: {user_message}" if len(self.conversation_history) > 1 else user_message

            # Run agent with user message
            result = await Runner.run(
                self.agent,
                full_message,
            )

            # Extract final output
            response = result.final_output

            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            return f"Error: {str(e)}"

    async def cleanup(self):
        """Cleanup resources."""
        if self.mcp_server:
            await self.mcp_server.__aexit__(None, None, None)
        print("\n👋 Chatbot session ended.")


async def main():
    """Main interactive chatbot loop."""

    # Initialize chatbot
    chatbot = CarServiceChatbot()
    await chatbot.initialize()

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\nCarBot: Thank you! Come back again. Goodbye! 👋")
                break

            # Get response from agent
            print("\nCarBot: ", end="", flush=True)
            response = await chatbot.chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nCarBot: Thank you! Come back again. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

    # Cleanup
    await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
