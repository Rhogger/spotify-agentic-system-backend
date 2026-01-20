import os
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client


class SpotifyMCPClient:
    def __init__(self):
        self.server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000/sse")

    @asynccontextmanager
    async def connect(self):
        """
        Conecta ao servidor MCP via HTTP (SSE).
        """
        print(f"🔌 Tentando conectar ao MCP em: {self.server_url}")

        try:
            async with sse_client(self.server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            print(f"❌ Erro ao conectar no MCP: {e}")
            raise e

    async def list_tools(self):
        """Lista todas as ferramentas disponíveis"""
        async with self.connect() as session:
            result = await session.list_tools()
            return result.tools

    async def call_tool(self, tool_name: str, arguments: dict = None) -> Any:
        """Chama uma ferramenta específica"""
        if arguments is None:
            arguments = {}

        async with self.connect() as session:
            result = await session.call_tool(tool_name, arguments)
            return result.content
