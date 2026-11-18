#!/usr/bin/env python3
"""
Hermes Agent Bridge for Antigravity.
Enables agentic communication, session management, and task delegation to local Hermes Agent.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERMES_BIN = os.path.expanduser("~/.local/bin/hermes")
if not os.path.exists(HERMES_BIN):
    HERMES_BIN = "hermes"


def clean_ansi(text: str) -> str:
    """Strip ANSI escape sequences from terminal output."""
    ansi_regex = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_regex.sub("", text)


def get_status() -> dict:
    """Check Hermes agent and gateway health."""
    try:
        res = subprocess.run(
            [HERMES_BIN, "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = clean_ansi(res.stdout + res.stderr)
        return {
            "installed": True,
            "status_output": output.strip(),
            "exit_code": res.returncode,
        }
    except Exception as e:
        return {"installed": False, "error": str(e)}


def list_sessions(limit: int = 10) -> list:
    """List recent Hermes sessions."""
    try:
        res = subprocess.run(
            [HERMES_BIN, "sessions", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = clean_ansi(res.stdout).splitlines()
        sessions = []
        for line in lines[2 : 2 + limit]:
            if line.strip():
                sessions.append(line.strip())
        return sessions
    except Exception as e:
        return [f"Error: {e}"]


def send_query(
    prompt: str,
    session: str = None,
    timeout: int = 120,
    model: str = None,
    yolo: bool = True,
) -> dict:
    """
    Send an agentic prompt to Hermes.
    Uses --oneshot, -Q, and --format text to get a direct, parseable reply.
    """
    cmd = [
        HERMES_BIN,
        "chat",
        "-q",
        prompt,
        "--oneshot",
        "-Q",
        "--format",
        "text",
        "--source",
        "tool",
    ]

    if session:
        cmd.extend(["-c", session, "--create-if-missing"])

    if model:
        cmd.extend(["-m", model])

    if yolo:
        cmd.append("--yolo")

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout_clean = clean_ansi(res.stdout).strip()
        stderr_clean = clean_ansi(res.stderr).strip()

        # Extract meaningful response text
        response_text = stdout_clean if stdout_clean else stderr_clean

        return {
            "success": res.returncode == 0,
            "response": response_text,
            "exit_code": res.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Hermes query timed out after {timeout} seconds.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Hermes Agent Bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # query command
    query_parser = subparsers.add_parser("query", help="Send a prompt to Hermes")
    query_parser.add_argument("prompt", type=str, help="The prompt to send to Hermes")
    query_parser.add_argument("--session", "-s", type=str, default=None, help="Named session to continue")
    query_parser.add_argument("--model", "-m", type=str, default=None, help="Override model")
    query_parser.add_argument("--timeout", "-t", type=int, default=120, help="Timeout in seconds")
    query_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    # status command
    subparsers.add_parser("status", help="Get Hermes status")

    # sessions command
    subparsers.add_parser("sessions", help="List recent Hermes sessions")

    args = parser.parse_args()

    if args.command == "status":
        st = get_status()
        print(st.get("status_output") if "status_output" in st else json.dumps(st, indent=2))
    elif args.command == "sessions":
        sessions = list_sessions()
        for s in sessions:
            print(s)
    elif args.command == "query":
        result = send_query(
            prompt=args.prompt,
            session=args.session,
            timeout=args.timeout,
            model=args.model,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(result.get("response"))
            else:
                print(f"[Hermes Error] {result.get('error', 'Unknown failure')}")
                sys.exit(result.get("exit_code", 1))


if __name__ == "__main__":
    main()
