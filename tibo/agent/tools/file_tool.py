def read_file_content(file_path):
    """Read a file and return its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    

def modify_file(file_path, action, from_line=None, to_line=None, new_content=None):
    """
    Modify a file using 0-based line numbers with improved error handling.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        max_index = len(lines)
        
        if action not in {'insert', 'delete', 'update'}:
            return f"Error: Invalid action '{action}'. Use 'insert', 'delete', or 'update'."
        
        # Auto-correct line numbers to be within bounds
        from_line = max(0, min(from_line, max_index))
        to_line = max(from_line, min(to_line, max_index))
        
        if isinstance(new_content, str):
            new_lines = [line + '\n' if not line.endswith('\n') else line for line in new_content.splitlines()]
        elif isinstance(new_content, list):
            new_lines = [line + '\n' if not line.endswith('\n') else line for line in new_content]
        else:
            new_lines = []
        
        if action == 'insert':
            lines[from_line:from_line] = new_lines
            result = f"Successfully inserted {len(new_lines)} lines at line {from_line}"
            
        elif action == 'delete':
            deleted_count = to_line - from_line
            del lines[from_line:to_line]
            result = f"Successfully deleted {deleted_count} lines from line {from_line} to {to_line-1}"
            
        elif action == 'update':
            deleted_count = to_line - from_line
            del lines[from_line:to_line]
            lines[from_line:from_line] = new_lines
            result = f"Successfully updated {deleted_count} lines with {len(new_lines)} new lines starting at line {from_line}"
        
        with open(file_path, 'w') as file:
            file.writelines(lines)
            
        return result
        
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"
    except Exception as e:
        return f"Error: {str(e)}"



def create_file(file_path, content=""):
    """
    Create a new file with the specified content.

    :param file_path: Path where the new file should be created.
    :param content: Content to write to the new file (string or list of strings).
    """
    # Convert content to a string with newlines if it's a list
    if isinstance(content, list):
        final_content = '\n'.join(content) + '\n'
    else:
        final_content = content + '\n' if content else ''
    
    with open(file_path, 'w') as file:
        file.write(final_content)


def delete_file(file_path):
    """
    Delete a file at the specified path.

    :param file_path: Path to the file to be deleted.
    """
    import os
    if os.path.exists(file_path):
        os.remove(file_path)