#!/usr/bin/env python3
"""
Render Mermaid diagram using kroki.io API (free, no auth needed)
"""

import base64
import urllib.request
import zlib
from pathlib import Path

MERMAID_CODE = """
flowchart TB
    subgraph SpeakMCP["SpeakMCP (Main Orchestrator)"]
        direction TB
        Voice["Voice Input"]
        MainAgent["Main Agent"]
        ACP["ACP Protocol Layer"]
    end

    subgraph SubAgents["Sub-Agents via ACP"]
        direction TB
        Internal["Internal Sub-Agent<br/>(SpeakMCP calling itself)"]
        Augi["Augi<br/>(Augment Code)"]
        ClaudeCode["Claude Code"]
    end

    subgraph Tools["MCP Tools"]
        direction TB
        Terminal["Terminal"]
        FileSystem["File System"]
        Browser["Browser"]
        Custom["Custom MCP Servers"]
    end

    Voice --> MainAgent
    MainAgent --> ACP
    ACP -->|"Delegate Task"| Internal
    ACP -->|"Delegate Task"| Augi
    ACP -->|"Delegate Task"| ClaudeCode

    Internal -->|"Return Output"| ACP
    Augi -->|"Return Output"| ACP
    ClaudeCode -->|"Return Output"| ACP

    MainAgent --> Tools
    Internal --> Tools
    Augi --> Tools
    ClaudeCode --> Tools

    style SpeakMCP fill:#1a1a2e,stroke:#16213e,color:#fff
    style SubAgents fill:#0f3460,stroke:#16213e,color:#fff
    style Tools fill:#533483,stroke:#16213e,color:#fff
    style MainAgent fill:#e94560,stroke:#fff,color:#fff
    style ACP fill:#00b4d8,stroke:#fff,color:#000
"""

def encode_diagram(diagram: str) -> str:
    """Encode diagram for kroki.io URL"""
    compressed = zlib.compress(diagram.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    return encoded

def main():
    output_path = Path(__file__).parent / "diagrams" / "multi_agent_orchestration.png"
    output_path.parent.mkdir(exist_ok=True)

    # Encode the diagram
    encoded = encode_diagram(MERMAID_CODE)

    # Build kroki.io URL
    url = f"https://kroki.io/mermaid/png/{encoded}"

    print(f"Fetching diagram from kroki.io...")

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            png_data = response.read()

            with open(output_path, 'wb') as f:
                f.write(png_data)

            print(f"✓ Saved: {output_path}")
            print(f"  Size: {len(png_data) // 1024} KB")

    except Exception as e:
        print(f"✗ Failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
