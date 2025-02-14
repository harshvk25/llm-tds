from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/run")
async def run_task(task: str):
    """
    Placeholder for executing automation tasks based on natural language instructions.
    """
    return {"message": f"Task '{task}' received and will be processed."}

@app.get("/read")
async def read_file(path: str):
    """
    Returns the content of the specified file if it exists.
    """
    try:
        with open(path, "r") as file:
            content = file.read()
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

