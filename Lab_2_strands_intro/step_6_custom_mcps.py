from mcp.server import FastMCP
import random

mcp = FastMCP("RNG Server")

@mcp.tool(description="Generates a random Number using a minimum and maximum range")
def random_num(min: int = 1, max: int = 10) -> int:
    """Generate a random number between min and max (inclusive)."""

    return random.randint(min, max)

mcp.run(transport="stdio")