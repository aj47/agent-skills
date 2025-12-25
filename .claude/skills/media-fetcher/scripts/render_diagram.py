#!/usr/bin/env python3
"""
Render Mermaid diagrams to PNG images.

Usage:
    python render_diagram.py diagram.mmd --output media/diagrams/
    python render_diagram.py --code "flowchart TD; A-->B" --name my_diagram

Requires @mermaid-js/mermaid-cli (mmdc):
    npm install -g @mermaid-js/mermaid-cli
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def check_mmdc_installed() -> bool:
    """Check if mermaid-cli (mmdc) is installed."""
    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def render_diagram(
    input_path: Path = None,
    code: str = None,
    output_dir: Path = None,
    output_name: str = None,
    theme: str = "default",
    background: str = "white",
    width: int = 800
) -> dict:
    """
    Render a Mermaid diagram to PNG.

    Either input_path OR code must be provided.

    Returns dict with status and details.
    """
    result = {
        "success": False,
        "input": str(input_path) if input_path else "inline code",
        "path": None,
        "error": None
    }

    output_dir = output_dir or Path("media/diagrams/")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine output filename
    if output_name:
        output_filename = f"{output_name}.png"
    elif input_path:
        output_filename = input_path.stem + ".png"
    else:
        output_filename = "diagram.png"

    output_path = output_dir / output_filename

    # Handle inline code by writing to temp file
    temp_file = None
    if code:
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.mmd',
            delete=False
        )
        temp_file.write(code)
        temp_file.close()
        input_path = Path(temp_file.name)

    try:
        # Build mmdc command
        cmd = [
            "mmdc",
            "-i", str(input_path),
            "-o", str(output_path),
            "-t", theme,
            "-b", background,
            "-w", str(width),
            # Use puppeteer config for better rendering
            "--puppeteerConfigFile", "/dev/null"
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if proc.returncode == 0 and output_path.exists():
            result["success"] = True
            result["path"] = str(output_path)
        else:
            error_msg = proc.stderr or proc.stdout or "Unknown error"
            # Clean up common mmdc error messages
            if "Could not find" in error_msg:
                result["error"] = "Mermaid syntax error - check diagram code"
            else:
                result["error"] = error_msg.strip()

    except subprocess.TimeoutExpired:
        result["error"] = "Rendering timed out (>60 seconds)"
    except Exception as e:
        result["error"] = str(e)
    finally:
        # Clean up temp file
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except:
                pass

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Render Mermaid diagrams to PNG"
    )

    # Input options (one required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input_file",
        nargs="?",
        help="Mermaid diagram file (.mmd)"
    )
    input_group.add_argument(
        "--code", "-c",
        help="Inline Mermaid diagram code"
    )

    parser.add_argument(
        "--output", "-o",
        default="media/diagrams/",
        help="Output directory (default: media/diagrams/)"
    )
    parser.add_argument(
        "--name", "-n",
        help="Output filename (without extension)"
    )
    parser.add_argument(
        "--theme", "-t",
        default="default",
        choices=["default", "forest", "dark", "neutral"],
        help="Diagram theme (default: default)"
    )
    parser.add_argument(
        "--background", "-b",
        default="white",
        help="Background color (default: white)"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=800,
        help="Output width in pixels (default: 800)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    # Check mmdc is installed
    if not check_mmdc_installed():
        print("Error: mermaid-cli (mmdc) is not installed", file=sys.stderr)
        print("Install with: npm install -g @mermaid-js/mermaid-cli", file=sys.stderr)
        sys.exit(1)

    # Determine input
    input_path = Path(args.input_file) if args.input_file else None

    if input_path and not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = render_diagram(
        input_path=input_path,
        code=args.code,
        output_dir=Path(args.output),
        output_name=args.name,
        theme=args.theme,
        background=args.background,
        width=args.width
    )

    if result["success"]:
        print(f"✓ Rendered: {result['path']}", file=sys.stderr)
    else:
        print(f"✗ Failed: {result['error']}", file=sys.stderr)

    if args.json:
        print(json.dumps(result, indent=2))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
