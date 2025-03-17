TOOL_SCHEMAS = [
{
    "name": "web_search",
    "description": "Perform a web search and get formatted results",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    }
}, 
{
    "name": "execute_command",
    "description": "Execute a shell command and return the output",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to execute"},
        },
        "required": ["command"]
    }
},
{
    "name": "start_persistent_process",
    "description": "Start a long-running process (e.g., a server) and keep it running in the background.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to start the persistent process."
            }
        },
        "required": ["command"]
    }
},
{
    "name": "get_project_info",
    "description": "Retrieve the project structure and optional description from the project data file.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
},
{
    "name": "get_relevant_code_files",
    "description": "Fetches relevant files from the project based on the query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query to find relevant code files"}
        },
        "required": ["query"]
    }
},
{
    "name": "read_file_content",
    "description": "Read the content of a specific file and return it as a string",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string", 
                "description": "The absolute path to the file to read"
            }
        },
        "required": ["file_path"]
    }
},
{
    "name": "modify_file",
    "description": "Modify a file by inserting, deleting, or updating a range of lines.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The absolute path to the file to modify"
            },
            "action": {
                "type": "string",
                "enum": ["insert", "delete", "update"],
                "description": "The modification action to perform: 'insert' to add new lines, 'delete' to remove lines, 'update' to modify lines."
            },
            "from_line": {
                "type": "integer",
                "minimum": 1,
                "description": "The starting line number (1-based index) of the range to modify. Required for all actions."
            },
            "to_line": {
                "type": "integer",
                "minimum": 1,
                "description": "The ending line number (1-based index) of the range to modify. Optional, defaults to from_line if not provided."
            },
            "new_content": {
                "type": ["string", "array"],
                "items": {
                    "type": "string"
                },
                "description": "The new content for insertion or update. Can be a string or list of strings. Required for 'insert' and 'update'."
            }
        },
        "required": ["file_path", "action", "from_line"],
        "dependencies": {
            "new_content": {
                "oneOf": [
                    {
                        "properties": {
                            "action": {
                                "enum": ["insert", "update"]
                            },
                            "new_content": {
                                "type": ["string", "array"]
                            }
                        },
                        "required": ["new_content"]
                    },
                    {
                        "properties": {
                            "action": {
                                "enum": ["delete"]
                            }
                        }
                    }
                ]
            }
        },
    }
},
{
    "name": "create_file",
    "description": "Create a new file with the specified content.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The absolute path where the new file should be created"
            },
            "content": {
                "type": ["string", "array"],
                "items": {
                    "type": "string"
                },
                "description": "The content to write to the new file. Can be a string or list of strings.",
                "default": ""
            }
        },
        "required": ["file_path"],
    }
},
{
    "name": "delete_file",
    "description": "Delete a file at the specified path.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The absolute path to the file to be deleted"
            }
        },
        "required": ["file_path"],
    }
}
]