import anthropic
import click
from typing import Callable
from .tools.search_tool import web_search
from .tools.terminal_tool import execute_command, start_persistent_process
from .tools.tool_schemas import TOOL_SCHEMAS
from .tools.codebase_intteligence import get_project_info, get_relevant_code_files
from .tools.file_tool import read_file_content

systemPrompt = (
    "You are Tibo, a very technical and helpful ai coding assistant. You have access to tools and you should use them if you think they are needed to handle the task."
    "Your main goal is to assist the user in understanding the codebase from the current working directory and planning new features that the users request."
    "Some of the tools you have can help with gaining a better understanding of the codebase and fetching relevant files from the codebase. Try to choose and read the most relevant files, no need to read all files if you already have the context."
    "When asked to implement new features, use combination of getting relevant file context together with reading file contents to know what you need to change."
    "Be consise in your final answers, and reply in a conversational manner without extra warnings or considertions, stay short and technical in your answers."
)

class ClaudeAgent:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.model = "claude-3-5-sonnet-20240620"
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
                    # elif tool_name == "modify_file":
                    #     results = modify_file(tool_input["file_path"], tool_input["action"], tool_input["from_line"], tool_input["to_line"], tool_input["new_content"])
                    #     tool_response = [{
                    #         "type": "tool_result",
                    #         "tool_use_id": tool_id,
                    #         "content": results
                    #     }]
                    #     self.messages.append({"role": "user", "content": tool_response})
                    #     break
                    # elif tool_name == "create_file":
                    #     results = create_file(tool_input["file_path"], tool_input["content"])
                    #     tool_response = [{
                    #         "type": "tool_result",
                    #         "tool_use_id": tool_id,
                    #         "content": results
                    #     }]
                    #     self.messages.append({"role": "user", "content": tool_response})
                    #     break
                    # elif tool_name == "delete_file":
                    #     results = delete_file(tool_input["file_path"])
                    #     tool_response = [{
                    #         "type": "tool_result",
                    #         "tool_use_id": tool_id,
                    #         "content": results
                    #     }]
                    #     self.messages.append({"role": "user", "content": tool_response})
                    #     break
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