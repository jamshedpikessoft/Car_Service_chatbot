"""
MCP Server using stdio transport (works with OpenAI Agent SDK)
Fetches data from FastAPI backend
"""
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

# Create MCP server
app = Server("car-service-mcp")

# FastAPI backend URL
FASTAPI_BASE_URL = "http://localhost:8000"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_available_slots",
            description=(
                """Retrieves all available car service time slots from the database. Automatically filters out past time slots for today and only shows future available slots. Returns a JSON object with success status, total count, and array of slot objects. Each slot contains date (YYYY-MM-DD format) and time (HH:MM AM/PM format). 
                never guess or assume slot availability."""
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Optional date filter in YYYY-MM-DD format (e.g., '2025-12-31'). If provided, only slots for that specific date will be returned. If omitted, returns all available slots for all dates."
                    }
                }
            }
        ),
        Tool(
            name="book_car_service",
            description=(
                """Creates a new car service booking appointment with customer details and generates a unique ticket ID. Validates that the requested slot is available before booking. Returns booking confirmation with ticket ID, customer info, and appointment details. Use this tool ONLY after collecting all required customer information and confirming their preferred slot."""
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer (e.g., 'John Doe')"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Customer's phone number with country code (e.g., '+1 123-456-7890')"
                    },
                    "car_model": {
                        "type": "string",
                        "description": "Make and model of the car with year (e.g., 'Honda Civic 2024')"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of service needed (e.g., 'Oil Change', 'Full Service', 'Brake Check', 'Tire Rotation')"
                    },
                    "date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format (e.g., '2025-12-31')"
                    },
                    "time": {
                        "type": "string",
                        "description": "Appointment time in HH:MM AM/PM format (e.g., '03:00 PM'). Must match an available slot."
                    }
                },
                "required": ["customer_name", "phone", "car_model", "service_type", "date", "time"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution - fetches data from FastAPI backend"""

    if name == "get_available_slots":
        try:
            # Call FastAPI backend
            async with httpx.AsyncClient() as client:
                params = {}
                if "date" in arguments and arguments["date"]:
                    params["date"] = arguments["date"]

                print(f"[MCP] Calling FastAPI: GET {FASTAPI_BASE_URL}/api/slots with params: {params}")
                response = await client.get(f"{FASTAPI_BASE_URL}/api/slots", params=params)
                response.raise_for_status()

                result = response.json()
                print(f"[MCP] FastAPI returned {result['total_slots']} slots")

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
        except Exception as e:
            print(f"[MCP] Error calling FastAPI: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Failed to fetch slots from backend: {str(e)}"
                })
            )]

    elif name == "book_car_service":
        try:
            # Call FastAPI backend
            async with httpx.AsyncClient() as client:
                booking_data = {
                    "customer_name": arguments["customer_name"],
                    "phone": arguments["phone"],
                    "car_model": arguments["car_model"],
                    "service_type": arguments["service_type"],
                    "date": arguments["date"],
                    "time": arguments["time"]
                }

                print(f"[MCP] Calling FastAPI: POST {FASTAPI_BASE_URL}/api/book")
                response = await client.post(f"{FASTAPI_BASE_URL}/api/book", json=booking_data)
                response.raise_for_status()

                result = response.json()
                print(f"[MCP] Booking successful! Ticket: {result['ticket_id']}")

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
        except httpx.HTTPStatusError as e:
            print(f"[MCP] Booking failed: {e.response.text}")
            error_detail = e.response.json().get("detail", str(e))
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": error_detail
                })
            )]
        except Exception as e:
            print(f"[MCP] Error calling FastAPI: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Failed to book service: {str(e)}"
                })
            )]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run MCP server with stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
