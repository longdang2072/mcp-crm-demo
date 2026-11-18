"""MCP server that lets Claude search customers, read orders and create
invoices in a small CRM database."""

from contextlib import closing

from mcp.server.mcpserver import MCPServer

import crm

mcp = MCPServer("crm-demo")


@mcp.tool()
def find_customer(query: str) -> list[dict]:
    """Search customers by part of their name or email address."""
    with closing(crm.connect()) as conn:
        return crm.find_customer(conn, query)


@mcp.tool()
def list_orders(customer_id: int) -> list[dict]:
    """List all orders for a customer, using the id returned by find_customer."""
    with closing(crm.connect()) as conn:
        return crm.list_orders(conn, customer_id)


@mcp.tool()
def create_invoice(customer_id: int, amount: float, note: str = "") -> dict:
    """Create an invoice for a customer. Amount is in USD and must be positive."""
    with closing(crm.connect()) as conn:
        return crm.create_invoice(conn, customer_id, amount, note)


if __name__ == "__main__":
    mcp.run()
