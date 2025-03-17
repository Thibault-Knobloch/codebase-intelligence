import subprocess

def execute_command(command):
    """
    Executes a shell command in the given directory (or current directory if None).
    """
    try:
        result = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr.strip()}"
    

def start_persistent_process(command):
    """
    Starts a long-running process in the background and returns its process ID (PID).
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return f"Process started successfully with PID: {process.pid}"