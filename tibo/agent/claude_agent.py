import anthropic
import click
from typing import Callable
from .tools.search_tool import web_search
from .tools.terminal_tool import execute_command, start_persistent_process
from .tools.tool_schemas import TOOL_SCHEMAS
from .tools.codebase_intteligence import get_project_info, get_relevant_code_files
from .tools.file_tool import read_file_content, modify_file, create_file, delete_file


systemPrompt = """
You are Tibo, a technical coding assistant with a structured approach to problem-solving. Your interaction follows this MANDATORY framework:

You interact with user in conversational way and are especially skilled at explaining codebases and planning new feature implementation.

CONTEXT GATHERING
   - Use get_project_info when gathering context
   - Identify key files and architecture before any implementation work
   - Prioritize files based on relevance to the current task
   - do not rely on assumptions from file names, make sure to check contents of the files to be sure about your implementaiton plan
   - Stop gathering context when you have enough information to plan implementation

TASK PLANNING
   - Present a numbered implementation plan with these specific sections:
     a) Files to modify/create/delete (with exact paths)
     b) Dependencies and imports required (if relevant)
     c) Implementation steps with expected outcomes
   - make sure you verify the validity of the plan. Especially ask yourself these questions: 
        is this enough for implement the netire feature? 
        did we consider all the relevant files? Also the connected compoenents and services that are needed?
   - MANDATORY: End with "Do you approve this plan?" and wait for explicit confirmation
   - IMPORTANT: do not rely on assumptions from file names, make sure to check contents of the files to be sure about your implementaiton plan

EXECUTION
   - NEVER implement changes without explicit user approval
   - When approval received, execute changes one file at a time
   - After each file modification, confirm the change was made and show the modified section
   - Maintain existing code style and formatting
   - Ensure from_line and to_line are within valid range (0 to file length)
   - When creating a file, make sure you first understand the structure of the folders. You can run simple ls commands with the execute_command tool for this.
   - For update actions, to_line should be the line AFTER the last line to be replaced

VERIFICATION
   - After implementation, suggest a way to test the changes

YOU MUST WAIT for user confirmation between task planning and execution. NEVER skip the confirmation step.
IMPORTANT: do not make assumptions about file contents. You need to check inside files to be sure, do not rely on names of files.
Respond concisely with technical precision, avoiding unnecessary explanations.
"""

class ClaudeAgent:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.model = "claude-3-sonnet-20240229"
        self.messages = []

    def process_query(self, query: str, stop_animation: Callable[[], None], run_thinking_animation: Callable[[], None]) -> str:
        self.messages.append({"role": "user", "content": query})
        final_answer = ""

        while True:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0,
                system=systemPrompt,
                tools=TOOL_SCHEMAS,
                tool_choice={"type": "auto", "disable_parallel_tool_use": True},
                messages=self.messages
            )

            self.messages.append({"role": "assistant", "content": resp.content})

            tool_called = False
            combined_text = []

            for block in resp.content:
                if block.type == "tool_use":
                    tool_called = True
                    tool_name = block.name
                    tool_id = block.id
                    tool_input = block.input

                    stop_animation()
                    click.secho(f"{tool_name}: ", fg="bright_magenta", bold=True, nl=False)
                    click.secho(f"{tool_input}", bold=True)

                    if tool_name == "web_search":
                        results = web_search(tool_input["query"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "execute_command":
                        results = execute_command(tool_input["command"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "start_persistent_process":
                        results = start_persistent_process(tool_input["command"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "get_project_info":
                        results = get_project_info()
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "get_relevant_code_files":
                        results = get_relevant_code_files(tool_input["query"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "read_file_content":
                        results = read_file_content(tool_input["file_path"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "modify_file":
                        results = modify_file(tool_input["file_path"], tool_input["action"], tool_input["from_line"], tool_input["to_line"], tool_input["new_content"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "create_file":
                        results = create_file(tool_input["file_path"], tool_input["content"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    elif tool_name == "delete_file":
                        results = delete_file(tool_input["file_path"])
                        tool_response = [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": results
                        }]
                        self.messages.append({"role": "user", "content": tool_response})
                        break
                    new_stop_animation = run_thinking_animation()

                elif block.type == "text":
                    combined_text.append(block.text)

            if not tool_called:
                final_answer = "".join(combined_text)
                break
        
        if tool_called:
            new_stop_animation()
        return final_answer

    def reset_conversation(self):
        self.messages = []