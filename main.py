from fastapi import FastAPI, HTTPException
import subprocess
import os
import json
import sqlite3
from datetime import datetime
from collections import Counter
from pathlib import Path

app = FastAPI()

def execute_task(task: str):
    """Determines and executes the appropriate action based on task description."""
    if "install uv" in task and "run" in task:
        return install_and_run_uv()
    elif "format" in task and ".md" in task:
        return format_markdown()
    elif "count Wednesdays" in task:
        return count_wednesdays()
    elif "sort contacts" in task:
        return sort_contacts()
    elif "extract recent logs" in task:
        return extract_recent_logs()
    elif "extract H1 headings" in task:
        return extract_h1_headings()
    elif "extract email sender" in task:
        return extract_email_sender()
    elif "calculate total sales" in task:
        return calculate_total_sales()
    else:
        return "Task not recognized."

def install_and_run_uv():
    """Handles installing 'uv' and running the required script."""
    try:
        subprocess.run(["uv", "--version"], check=True)
    except FileNotFoundError:
        subprocess.run(["pip", "install", "uv"], check=True)

    user_email = os.getenv("USER_EMAIL", "default@example.com")
    subprocess.run(["python", "datagen.py", user_email], check=True)
    return f"Executed uv installation and script with {user_email}."

def format_markdown():
    """Formats a Markdown file using Prettier."""
    try:
        subprocess.run(["npx", "prettier", "--write", "/data/format.md"], check=True)
        return "Formatted /data/format.md successfully."
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error formatting: {str(e)}")

def count_wednesdays():
    """Counts the number of Wednesdays in /data/dates.txt."""
    try:
        with open("/data/dates.txt", "r") as file:
            dates = [line.strip() for line in file.readlines()]
        wednesdays = sum(1 for date in dates if datetime.strptime(date, "%Y-%m-%d").weekday() == 2)
        with open("/data/dates-wednesdays.txt", "w") as out_file:
            out_file.write(str(wednesdays))
        return f"Counted {wednesdays} Wednesdays and saved to /data/dates-wednesdays.txt."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting Wednesdays: {str(e)}")

def sort_contacts():
    """Sorts contacts by last name, then first name."""
    try:
        with open("/data/contacts.json", "r") as file:
            contacts = json.load(file)
        contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
        with open("/data/contacts-sorted.json", "w") as file:
            json.dump(contacts, file, indent=2)
        return "Sorted contacts successfully."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sorting contacts: {str(e)}")

def extract_recent_logs():
    """Extracts the first line of the 10 most recent .log files in /data/logs/."""
    try:
        log_dir = Path("/data/logs")
        log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
        with open("/data/logs-recent.txt", "w") as out_file:
            for log_file in log_files:
                with open(log_file, "r") as lf:
                    first_line = lf.readline().strip()
                    out_file.write(first_line + "\n")
        return "Extracted recent log entries successfully."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting logs: {str(e)}")

def extract_h1_headings():
    """Extracts H1 headings from Markdown files in /data/docs/."""
    try:
        index = {}
        for md_file in Path("/data/docs/").glob("*.md"):
            with open(md_file, "r") as file:
                for line in file:
                    if line.startswith("# "):
                        index[md_file.name] = line.strip("# ").strip()
                        break
        with open("/data/docs/index.json", "w") as out_file:
            json.dump(index, out_file, indent=2)
        return "Extracted H1 headings successfully."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting H1 headings: {str(e)}")

def extract_email_sender():
    """Extracts sender's email from /data/email.txt."""
    try:
        import re
        with open("/data/email.txt", "r") as file:
            content = file.read()
        match = re.search(r"From: (.+@.+\..+)", content)
        if match:
            email = match.group(1).strip()
            with open("/data/email-sender.txt", "w") as out_file:
                out_file.write(email)
            return f"Extracted email sender: {email}"
        return "No email found."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting email sender: {str(e)}")

def calculate_total_sales():
    """Calculates total sales for 'Gold' ticket type from SQLite DB."""
    try:
        conn = sqlite3.connect("/data/ticket-sales.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
        total_sales = cursor.fetchone()[0]
        conn.close()
        with open("/data/ticket-sales-gold.txt", "w") as file:
            file.write(str(total_sales))
        return f"Total sales for 'Gold' tickets: {total_sales}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating total sales: {str(e)}")

@app.post("/run")
async def run_task(task: str):
    """Parses and executes the task."""
    try:
        result = execute_task(task)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    """Returns the content of the specified file if it exists."""
    try:
        with open(path, "r") as file:
            content = file.read()
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



