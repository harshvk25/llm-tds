import os
import openai
import re
import shutil

# Set API Key for AI Proxy
openai.api_key = os.getenv("AI_PROXY_KEY")

DATA_DIR = "/data"

def is_safe_path(path):
    """Ensure the path is inside /data/"""
    abs_path = os.path.abspath(path)
    return abs_path.startswith(os.path.abspath(DATA_DIR))

def execute_task(task: str):
    """Uses LLM to interpret and execute tasks with security constraints."""
    function_name = interpret_task(task)

    # Ensure the task is safe
    if ".." in task or not is_safe_path(task):
        return "Security Error: Access outside /data is not allowed."

    if "delete" in task.lower():
        return "Security Error: Deleting files is not permitted."

    task_mapping = {
        "install_and_run_uv": install_and_run_uv,
        "format_markdown": format_markdown,
        "count_wednesdays": count_wednesdays,
        "sort_contacts": sort_contacts,
        "extract_recent_logs": extract_recent_logs,
        "extract_h1_headings": extract_h1_headings,
        "extract_email_sender": extract_email_sender,
        "calculate_total_sales": calculate_total_sales,
    }

    if function_name in task_mapping:
        return task_mapping[function_name]()
    else:
        return f"Unrecognized task: {task}"





