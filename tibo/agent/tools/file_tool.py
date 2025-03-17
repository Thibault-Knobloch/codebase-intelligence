def read_file_content(file_path):
    """Read a file and return its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    

def modify_file(file_path, action, from_line=None, to_line=None, new_content=None):
    """
    Modify a file by inserting, deleting, or updating a range of lines.

    :param file_path: Path to the file to be modified.
    :param action: Action to perform: 'insert', 'delete', or 'update'.
    :param from_line: Starting line number (1-based index) of the range to modify.
    :param to_line: Ending line number (1-based index) of the range to modify (optional, defaults to from_line if not provided).
    :param new_content: The new content for insertion or update (string or list of strings).
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # If to_line is not provided, set it equal to from_line
    if to_line is None:
        to_line = from_line

    # Validate line numbers
    if from_line is not None and to_line is not None:
        if not (0 < from_line <= to_line <= len(lines) + 1):
            raise ValueError("Invalid line number range")

    if action == 'insert' and from_line is not None and new_content is not None:
        # Convert new_content to list of lines if it's a single string
        if isinstance(new_content, str):
            new_lines = [line + '\n' for line in new_content.split('\n') if line]
        else:
            new_lines = [line + '\n' for line in new_content]
        lines[from_line - 1:from_line - 1] = new_lines

    elif action == 'delete' and from_line is not None:
        if 0 < from_line <= len(lines):
            del lines[from_line - 1:to_line]

    elif action == 'update' and from_line is not None and new_content is not None:
        # Convert new_content to list of lines if it's a single string
        if isinstance(new_content, str):
            new_lines = [line + '\n' for line in new_content.split('\n') if line]
        else:
            new_lines = [line + '\n' for line in new_content]
        del lines[from_line - 1:to_line]
        lines[from_line - 1:from_line - 1] = new_lines

    with open(file_path, 'w') as file:
        file.writelines(lines)

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