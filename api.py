from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from flow import task_flow
from typing import Optional

app = FastAPI(title="Smart Task Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    task: str
    priority: str
    calendar: str
    description: Optional[str] = None 

@app.get("/api/tasks")
def get_tasks():
    shared = {"action": "view"}
    task_flow.run(shared)
    return shared.get("summary_data", {"tasks": [], "total_minutes": 0})

@app.post("/api/tasks")
def create_task(payload: TaskCreate):
    shared = {
        "action": "create",
        "task_input": payload.task,
        "priority_input": payload.priority,
        "calendar_input": payload.calendar,
        "description_input": payload.description 
    }
    task_flow.run(shared)
    return {"status": "success"}

@app.post("/api/tasks/{task_id}/done")
def complete_task(task_id: int):
    shared = {"action": "done", "target_idx": task_id}
    task_flow.run(shared)
    return {"status": "success"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    shared = {"action": "delete", "target_idx": task_id}
    task_flow.run(shared)
    return {"status": "success"}

class TaskStatusUpdate(BaseModel):
    status: str

@app.patch("/api/tasks/{task_id}/status")
def update_task_status(task_id: int, payload: TaskStatusUpdate):
    shared = {
        "action": "status", 
        "target_idx": task_id, 
        "new_status": payload.status
    }
    task_flow.run(shared)
    return {"status": "success"}

class TaskReorder(BaseModel):
    old_index: int
    new_index: int

@app.post("/api/tasks/reorder")
def reorder_tasks(payload: TaskReorder):
    shared = {
        "action": "reorder",
        "old_index": payload.old_index,
        "new_index": payload.new_index
    }
    task_flow.run(shared)
    return {"status": "success"}

# --- NEW EDIT ENDPOINT ---
class TaskEdit(BaseModel):
    task: str
    description: Optional[str] = None
    priority: str
    calendar: str

@app.put("/api/tasks/{task_id}")
def edit_task(task_id: int, payload: TaskEdit):
    shared = {
        "action": "edit",
        "target_idx": task_id,
        "task_input": payload.task,
        "description_input": payload.description,
        "priority_input": payload.priority,
        "calendar_input": payload.calendar
    }
    task_flow.run(shared)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Smart Task Web API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)