# Simple-Agent-Tools

This repository contains all the commands and tools that [Simple Agent Core](https://github.com/reagent-systems/Simple-Agent-Core) uses to perform various operations. These modular commands enable the AI agent to interact with files, web resources, GitHub repositories, and system operations in a structured and extensible way.

## Overview

Simple-Agent-Tools serves as the command library for Simple Agent Core, providing a comprehensive set of tools organized into logical categories. Each command is implemented as a separate module with its own schema definition, making the system highly modular and easy to extend.

## Available Command Categories

### 📁 File Operations (`file_ops/`)
Commands for file and directory management:

- **`read_file`** - Read contents of a file
- **`write_file`** - Write content to a file
- **`append_file`** - Append content to an existing file
- **`edit_file`** - Edit specific parts of a file
- **`advanced_edit_file`** - Advanced file editing with multiple operations
- **`delete_file`** - Delete a file
- **`file_exists`** - Check if a file exists
- **`create_directory`** - Create a new directory
- **`list_directory`** - List contents of a directory
- **`save_json`** - Save data as JSON file
- **`load_json`** - Load data from JSON file
- **`screenshot`** - Take a screenshot and save it
- **`analyze_image_with_gpt4`** - Analyze images using GPT-4 Vision

### 🌐 Web Operations (`web_ops/`)
Commands for web interaction and data retrieval:

- **`web_search`** - Search the web for information
- **`web_scrape`** - Scrape content from web pages
- **`raw_web_read`** - Read raw content from web URLs
- **`fetch_json_api`** - Fetch data from JSON APIs
- **`extract_links`** - Extract links from web pages

### 🐙 GitHub Operations (`github_ops/`)
Commands for GitHub repository management and interaction:

- **`git_clone`** - Clone a GitHub repository
- **`github_fork_clone`** - Fork and clone a repository
- **`github_create_repo`** - Create a new GitHub repository
- **`github_create_branch`** - Create a new branch
- **`github_read_files`** - Read files from a GitHub repository
- **`github_add_files`** - Add files to a repository
- **`github_create_issue`** - Create a new issue
- **`github_create_pr`** - Create a pull request
- **`github_approve_pr`** - Approve a pull request
- **`github_merge_pr`** - Merge a pull request
- **`github_close_pr`** - Close a pull request
- **`github_reopen_pr`** - Reopen a pull request
- **`github_comment`** - Add comments to issues/PRs
- **`repo_reader`** - Read repository information
- **`pr_reader`** - Read pull request details
- **`issue_reader`** - Read issue details

### 💾 Data Operations (`data_ops/`)
Commands for data processing and analysis:

- **`text_analysis`** - Analyze and process text data

### ⚙️ System Operations (`system_ops/`)
Commands for system-level operations:

- **`screenshot`** - Take system screenshots

## Architecture

Each command follows a consistent structure:

```
commands/
├── category_name/
│   ├── command_name/
│   │   └── __init__.py    # Contains the command function and schema
│   └── ...
└── ...
```

### Command Structure

Each command module (`__init__.py`) contains:

1. **Function Implementation** - The actual command logic
2. **Schema Definition** - JSON schema defining parameters and description
3. **Registration** - Automatic registration with the command system

Example command structure:
```python
from commands import register_command

def my_command(param1: str, param2: int = 5) -> dict:
    """Command implementation"""
    # Command logic here
    return {"result": "success"}

MY_COMMAND_SCHEMA = {
    "type": "function",
    "function": {
        "name": "my_command",
        "description": "Description of what this command does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Parameter description"},
                "param2": {"type": "integer", "description": "Optional parameter", "default": 5}
            },
            "required": ["param1"]
        }
    }
}

register_command("my_command", my_command, MY_COMMAND_SCHEMA)
```

## Integration with Simple Agent Core

These commands are automatically discovered and loaded by Simple Agent Core through the command registration system. The agent can then use any of these commands through function calling, making it capable of:

- Managing files and directories
- Searching and scraping the web
- Interacting with GitHub repositories
- Processing and analyzing data
- Taking screenshots and analyzing images

## Contributing

When adding new commands to this repository:

1. **Choose the Right Category** - Place your command in the appropriate category directory, or create a new category if needed
2. **Follow the Structure** - Each command should be in its own subdirectory with an `__init__.py` file
3. **Include Proper Schema** - Define a complete JSON schema for your command
4. **Register the Command** - Use the `register_command` function to make it available
5. **Document Your Command** - Include clear descriptions and parameter documentation

### Contribution Guidelines

1. **Documentation**: All updates should include necessary documentation updates, especially if they affect existing protocol structures.
2. **Code Reviews**: All new code contributions require code review approval from at least one senior developer.
3. **Testing**: Ensure your commands work correctly with Simple Agent Core before submitting.

### Commit References

To link commits to specific GitHub issues, use `#number` in your commit message, where `number` corresponds to the issue ID.

Example:
- `Fixes #123` – Links the commit to issue #123, marking it as fixed.
- `Closes #456` – Links the commit to issue #456, closing it upon merge.

### Reserved Keywords

Use these keywords in commit messages for consistency:

- **Resolve**: Use when a commit fixes an issue
- **Fix**: For bug fixes
- **Close**: When the commit closes an issue entirely
- **Refactor**: For code improvements without changing functionality
- **Add**: For new features or commands
- **Remove**: For deleting commands or code

### Good Commit Guidelines

1. **Be Descriptive**: Clearly state what the commit accomplishes
2. **Use Imperative Mood**: Start with a verb, as if giving a command
3. **Reference Issues**: Use the issue number where applicable
4. **Separate Concepts**: Make separate commits for different types of changes
5. **Keep It Short**: Limit subject lines to 50 characters when possible

#### Example Good Commit Messages

- `Add #203 - New web_scrape command for content extraction`
- `Fix #215 - Correct parameter validation in github_create_pr`
- `Refactor file_ops commands for better error handling`
- `Remove deprecated raw_file_read command`

## Related Projects

- **[Simple Agent Core](https://github.com/reagent-systems/Simple-Agent-Core)** - The main AI agent framework that uses these commands

## License

This project is licensed under the same terms as Simple Agent Core. See the LICENSE file for details.
