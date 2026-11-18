"""Runs the MCP server and calls its tools the same way Claude does.

Usage: python demo_client.py
"""

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call(session: ClientSession, name: str, args: dict):
    arg_text = ", ".join(f"{k}={v!r}" for k, v in args.items())
    print(f"→ {name}({arg_text})")
    result = await session.call_tool(name, args)
    items = [json.loads(c.text) for c in result.content]
    for item in items:
        print("  " + json.dumps(item, ensure_ascii=False))
    return items


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("✓ Connected to crm-demo MCP server")
            print("  Tools: " + ", ".join(t.name for t in tools.tools))
            customer = (await call(session, "find_customer", {"query": "acme"}))[0]
            await call(session, "list_orders", {"customer_id": customer["id"]})
            await call(
                session,
                "create_invoice",
                {"customer_id": customer["id"], "amount": 300, "note": "Monthly SEO"},
            )
            print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
