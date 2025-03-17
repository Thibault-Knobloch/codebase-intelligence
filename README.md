# codebase-intelligence
🧩 **Tibo** – a powerful command-line tool designed to index your codebase, generate call graphs, and chunk code into a vector database. With **tibo**, you can query your codebase using natural language and retrieve contextually relevant files, functions, and code snippets effortlessly.

<p align="center">
  <img width="759" alt="Tibo Workflow" src="https://github.com/user-attachments/assets/1475103e-9810-420f-8ec2-c25d905ea543" />
</p>

## Features
- **Codebase Indexing**: Scans and organizes your project for easy querying.
- **Call Graph Generation**: Maps relationships between functions and files.
- **Vector Database**: Embeds code chunks for fast, intelligent retrieval.
- **Natural Language Queries**: Ask questions about your code in plain English.
- **Context-Aware Results**: Returns relevant files and snippets with added context from the call graph.
  
## Installation
Get started with **tibo** by installing:
```
pip install tibo
```
Find the latest version and additional details on the [PyPI project page](https://pypi.org/project/tibo/).

## Usage
Follow these steps to integrate **tibo** into your workflow:

1. Configure the Tool - Set up **tibo** with your OpenAI API key:
```
tibo config
```


2. Index Your Project - Navigate to your project directory and index your codebase:
```
cd /path/to/your/project
tibo index
```
Note: This creates a .tibo folder in your project root to store indexed data, call graphs, and vector embeddings.


3. Query Your Codebase - Fetch relevant context by asking questions in natural language:
```
tibo fetch "my query to the codebase"
```
Results include the most relevant file names and code chunks.
Full output is saved in .tibo/query_output/query_output.json.


4. NEW Interact with Tibo Agent - chat with the ai agent to understnad the codebase better and get help with implementing new features:
```
tibo agent
```
NOTE: requires running tibo config and adding ANTHROPIC_API_KEY when prompted.
The agent can use the tibo fetching tools if you have run 'tibo index' before.
In the shell:
- type 'exit' or 'quit' to quit the agent shell
- type '#' followed by a command to execute a command directly in your terminal
- type 'reset' to reset the conversation history


## How It Works
**Configuration**: Link Tibo to your OpenAI API for LLM-powered enhancements.

**Indexing**: Processes codebase, builds call graph, chunks files, enhances with GPT-4o-mini, and stores vector embeddings locally.

**Querying**: Enhances your query with an LLM, matches it to the top relevant chunks, and supplements results with call graph context.


## Requirements
Python 3.7+
An OpenAI API key (required for LLM functionality)

## Contributing
We welcome contributions! Feel free to open issues or submit pull requests on our GitHub repository.

## License
MIT License
