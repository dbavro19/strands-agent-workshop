"""
Execute Python code in a REPL environment with state persistence for Windows.

This module provides a tool for running Python code through a Strands Agent, with features like:
- Persistent state between executions
- Output capturing and formatting
- Error handling and logging
- State reset capabilities
- User confirmation for code execution

Usage with Strands Agent:
```python
from strands import Agent
from strands_tools import python_repl_windows

# Register the python_repl tool with the agent
agent = Agent(tools=[python_repl_windows])

# Execute Python code
result = agent.tool.python_repl_windows(code="print('Hello, world!')")

# Execute with state persistence (variables remain available between calls)
agent.tool.python_repl_windows(code="x = 10")
agent.tool.python_repl_windows(code="print(x * 2)")  # Will print: 20

# Reset the REPL state if needed
agent.tool.python_repl_windows(code="print('Fresh start')", reset_state=True)
```
"""

import logging
import os
import re
import select
import signal
import struct
import sys
import threading
import traceback
import types
import subprocess
import tempfile
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

import dill
from rich import box
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from strands.types.tools import ToolResult, ToolUse

from strands_tools.utils import console_util
from strands_tools.utils.user_input import get_user_input

# Initialize logging and set paths
logger = logging.getLogger(__name__)

# Tool specification
TOOL_SPEC = {
    "name": "python_repl_windows",
    "description": "Execute Python code in a REPL environment with state persistence on Windows.\n\n"
    "IMPORTANT SAFETY FEATURES:\n"
    "1. User Confirmation: Requires explicit approval before executing code\n"
    "2. Code Preview: Shows syntax-highlighted code before execution\n"
    "3. State Management: Maintains variables between executions\n"
    "4. Error Handling: Captures and formats errors with suggestions\n"
    "5. Development Mode: Can bypass confirmation in DEV environments\n\n"
    "Key Features:\n"
    "- Persistent state between executions\n"
    "- Output capturing and formatting\n"
    "- Error handling and logging\n"
    "- State reset capabilities\n\n"
    "Example Usage:\n"
    "1. Basic execution: code=\"print('Hello, world!')\"\n"
    '2. With state: First call code="x = 10", then code="print(x * 2)"\n'
    "3. Reset state: code=\"print('Fresh start')\", reset_state=True",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The Python code to execute"},
                "interactive": {
                    "type": "boolean",
                    "description": (
                        "Whether to enable interactive mode. "
                        "Default controlled by PYTHON_REPL_INTERACTIVE environment variable."
                    ),
                    "default": True,
                },
                "reset_state": {
                    "type": "boolean",
                    "description": (
                        "Whether to reset the REPL state before execution. "
                        "Default controlled by PYTHON_REPL_RESET_STATE environment variable."
                    ),
                    "default": False,
                },
            },
            "required": ["code"],
        }
    },
}


class OutputCapture:
    """Captures stdout and stderr output."""

    def __init__(self) -> None:
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def __enter__(self) -> "OutputCapture":
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> None:
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def get_output(self) -> str:
        """Get captured output from both stdout and stderr."""
        output = self.stdout.getvalue()
        errors = self.stderr.getvalue()
        if errors:
            output += f"\nErrors:\n{errors}"
        return output


class ReplState:
    """Manages persistent Python REPL state."""

    def __init__(self) -> None:
        # Initialize namespace
        self._namespace = {
            "__name__": "__main__",
        }
        # Setup state persistence
        self.persistence_dir = os.path.join(Path.cwd(), "repl_state")
        os.makedirs(self.persistence_dir, exist_ok=True)
        self.state_file = os.path.join(self.persistence_dir, "repl_state.pkl")
        self.load_state()

    def load_state(self) -> None:
        """Load persisted state with reset on failure."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "rb") as f:
                    saved_state = dill.load(f)
                self._namespace.update(saved_state)
                logger.debug("Successfully loaded REPL state")
            except Exception as e:
                # On error, remove the corrupted state file
                logger.debug(f"Error loading state: {e}. Removing corrupted state file.")
                try:
                    os.remove(self.state_file)
                    logger.debug("Removed corrupted state file")
                except Exception as remove_error:
                    logger.debug(f"Error removing state file: {remove_error}")

                # Initialize fresh state
                logger.debug("Initializing fresh REPL state")

    def save_state(self, code: Optional[str] = None) -> None:
        """Save current state."""
        try:
            # Execute new code if provided
            if code:
                exec(code, self._namespace)

            # Filter namespace for persistence
            save_dict = {}
            for name, value in self._namespace.items():
                if not name.startswith("_"):
                    try:
                        # Try to pickle the value
                        dill.dumps(value)
                        save_dict[name] = value
                    except BaseException:
                        continue

            # Save state
            with open(self.state_file, "wb") as f:
                dill.dump(save_dict, f)
            logger.debug("Successfully saved REPL state")

        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def execute(self, code: str) -> None:
        """Execute code and save state."""
        exec(code, self._namespace)
        self.save_state()

    def get_namespace(self) -> dict:
        """Get current namespace."""
        return dict(self._namespace)

    def clear_state(self) -> None:
        """Clear the current state and remove state file."""
        try:
            # Clear namespace to defaults
            self._namespace = {
                "__name__": "__main__",
            }

            # Remove state file if it exists
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
                logger.info("REPL state cleared and file removed")

            # Save fresh state
            self.save_state()

        except Exception as e:
            logger.error(f"Error clearing state: {e}")

    def get_user_objects(self) -> Dict[str, str]:
        """Get user-defined objects for display."""
        objects = {}
        for name, value in self._namespace.items():
            # Skip special/internal objects
            if name.startswith("_"):
                continue

            # Handle each type separately to avoid unreachable code
            if isinstance(value, (int, float, str, bool)):
                objects[name] = repr(value)

        return objects


# Create global state instance
repl_state = ReplState()


def clean_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class WindowsProcessManager:
    """Manages subprocess-based Python execution with state synchronization for Windows."""

    def __init__(self, callback: Optional[Callable] = None):
        self.process = None
        self.output_buffer: List[str] = []
        self.input_buffer: List[str] = []
        self.stop_event = threading.Event()
        self.callback = callback
        self.temp_file = None
        self.exit_code = None

    def start(self, code: str) -> None:
        """Start subprocess with code execution."""
        # Create a temporary file to store the code
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False)
        
        # Write the code to the temporary file
        with open(self.temp_file.name, 'w') as f:
            # Import the namespace from the state file if it exists
            setup_code = """
import sys
import os
import dill
from pathlib import Path

# Setup state persistence
persistence_dir = os.path.join(Path.cwd(), "repl_state")
state_file = os.path.join(persistence_dir, "repl_state.pkl")

# Initialize namespace
namespace = {"__name__": "__main__"}

# Load state if it exists
if os.path.exists(state_file):
    try:
        with open(state_file, "rb") as f:
            saved_state = dill.load(f)
        namespace.update(saved_state)
    except Exception:
        pass

# Update globals with namespace
globals().update(namespace)

# Execute the user code
"""
            f.write(setup_code)
            f.write(code)

        # Start the subprocess
        self.process = subprocess.Popen(
            [sys.executable, self.temp_file.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Start output reader threads
        stdout_reader = threading.Thread(target=self._read_stdout)
        stdout_reader.daemon = True
        stdout_reader.start()

        stderr_reader = threading.Thread(target=self._read_stderr)
        stderr_reader.daemon = True
        stderr_reader.start()

    def _read_stdout(self) -> None:
        """Read and process subprocess stdout."""
        for line in iter(self.process.stdout.readline, ''):
            cleaned = clean_ansi(line)
            self.output_buffer.append(cleaned)
            if self.callback:
                self.callback(cleaned)
        
        # Store exit code when process completes
        self.exit_code = self.process.poll()

    def _read_stderr(self) -> None:
        """Read and process subprocess stderr."""
        for line in iter(self.process.stderr.readline, ''):
            cleaned = clean_ansi(line)
            self.output_buffer.append(cleaned)
            if self.callback:
                self.callback(cleaned)

    def write_input(self, input_data: str) -> None:
        """Write input to the subprocess."""
        if self.process and self.process.poll() is None:
            self.process.stdin.write(input_data + "\n")
            self.process.stdin.flush()
            self.input_buffer.append(input_data)

    def get_output(self) -> str:
        """Get complete output with ANSI codes removed and binary content truncated."""
        raw = "".join(self.output_buffer)
        clean = clean_ansi(raw)

        # Handle binary content
        def format_binary(text: str, max_len: int = None) -> str:
            if max_len is None:
                max_len = int(os.environ.get("PYTHON_REPL_BINARY_MAX_LEN", "100"))
            if "\\x" in text and len(text) > max_len:
                return f"{text[:max_len]}... [binary content truncated]"
            return text

        return format_binary(clean)

    def stop(self) -> None:
        """Stop subprocess and clean up."""
        self.stop_event.set()

        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
        # Clean up temporary file
        if self.temp_file and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except OSError:
                pass


output_buffer: List[str] = []


def python_repl_windows(tool: ToolUse, **kwargs: Any) -> ToolResult:
    """Execute Python code with persistent state and output streaming for Windows."""
    console = console_util.create()

    tool_use_id = tool["toolUseId"]
    tool_input = tool["input"]

    code = tool_input["code"]
    interactive = tool_input.get("interactive", True)
    reset_state = tool_input.get("reset_state", False)

    # Check for development mode
    strands_dev = os.environ.get("DEV", "").lower() == "true"

    # Check for non_interactive_mode parameter
    non_interactive_mode = kwargs.get("non_interactive_mode", False)

    try:
        # Handle state reset if requested
        if reset_state:
            console.print("[yellow]Resetting REPL state...[/]")
            repl_state.clear_state()
            console.print("[green]REPL state reset complete[/]")

        # Show code preview
        console.print(
            Panel(
                Syntax(code, "python", theme="monokai"),
                title="[bold blue]Executing Python Code[/]",
            )
        )

        # Add permissions check - only show confirmation dialog if not in DEV mode and not in non_interactive mode
        if not strands_dev and not non_interactive_mode:
            # Create a table with code details for better visualization
            details_table = Table(show_header=False, box=box.SIMPLE)
            details_table.add_column("Property", style="cyan", justify="right")
            details_table.add_column("Value", style="green")

            # Add code details
            details_table.add_row("Code Length", f"{len(code)} characters")
            details_table.add_row("Line Count", f"{len(code.splitlines())} lines")
            details_table.add_row("Mode", "Interactive" if interactive else "Standard")
            details_table.add_row("Reset State", "Yes" if reset_state else "No")

            # Show confirmation panel
            console.print(
                Panel(
                    details_table,
                    title="[bold blue]🐍 Python Code Execution Preview",
                    border_style="blue",
                    box=box.ROUNDED,
                )
            )
            # Get user confirmation
            user_input = get_user_input(
                "<yellow><bold>Do you want to proceed with Python code execution?</bold> [y/*]</yellow>"
            )
            if user_input.lower().strip() != "y":
                cancellation_reason = (
                    user_input
                    if user_input.strip() != "n"
                    else get_user_input("Please provide a reason for cancellation:")
                )
                error_message = f"Python code execution cancelled by the user. Reason: {cancellation_reason}"
                error_panel = Panel(
                    f"[bold blue]{error_message}[/bold blue]",
                    title="[bold blue]❌ Cancelled",
                    border_style="blue",
                    box=box.ROUNDED,
                )
                console.print(error_panel)
                return {
                    "toolUseId": tool_use_id,
                    "status": "error",
                    "content": [{"text": error_message}],
                }

        # Track execution time and capture output
        start_time = datetime.now()
        output = None

        try:
            if interactive:
                console.print("[green]Running in interactive mode...[/]")
                proc_mgr = WindowsProcessManager()
                proc_mgr.start(code)

                # Wait for completion
                if proc_mgr.process:
                    proc_mgr.process.wait()
                    exit_code = proc_mgr.process.returncode
                else:
                    exit_code = -1

                # Get output and clean up
                output = proc_mgr.get_output()
                proc_mgr.stop()

                # Save state if execution succeeded
                if exit_code == 0:
                    repl_state.save_state(code)
            else:
                console.print("[blue]Running in standard mode...[/]")
                captured = OutputCapture()
                with captured as output_capture:
                    repl_state.execute(code)
                    output = output_capture.get_output()
                    if output:
                        console.print("[cyan]Output:[/]")
                        console.print(output)

            # Show execution stats
            duration = (datetime.now() - start_time).total_seconds()
            user_objects = repl_state.get_user_objects()

            status = f"✓ Code executed successfully ({duration:.2f}s)"
            if user_objects:
                status += f"\nUser objects in namespace: {len(user_objects)} items"
                for name, value in user_objects.items():
                    status += f"\n - {name} = {value}"
            console.print(f"[bold green]{status}[/]")

            # Return result with output
            return {
                "toolUseId": tool_use_id,
                "status": "success",
                "content": [{"text": output if output else "Code executed successfully"}],
            }

        except RecursionError:
            console.print("[yellow]Recursion error detected - resetting state...[/]")
            repl_state.clear_state()
            # Re-raise the exception after cleanup
            raise

    except Exception as e:
        error_tb = traceback.format_exc()
        error_time = datetime.now()

        console.print(
            Panel(
                Syntax(error_tb, "python", theme="monokai"),
                title="[bold red]Python Error[/]",
                border_style="red",
            )
        )

        # Log error with details
        errors_dir = os.path.join(Path.cwd(), "errors")
        os.makedirs(errors_dir, exist_ok=True)
        error_file = os.path.join(errors_dir, "errors.txt")

        error_msg = f"\n[{error_time.isoformat()}] Python REPL Error:\nCode:\n{code}\nError:\n{error_tb}\n"

        with open(error_file, "a") as f:
            f.write(error_msg)
        logger.debug(error_msg)

        # If it's a recursion error, suggest resetting state
        suggestion = ""
        if isinstance(e, RecursionError):
            suggestion = "\nTo fix this, try running with reset_state=True"

        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": f"{error_msg}{suggestion}"}],
        }