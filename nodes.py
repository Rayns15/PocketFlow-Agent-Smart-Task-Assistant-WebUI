from pocketflow import Node
from utils import get_current_timestamp
from datetime import datetime
import sys
import yaml
import ollama
import json
import os
import dateparser

class InputTaskNode(Node):
    def prep(self, shared): 
        if "task_list" not in shared:
            if os.path.exists("tasks.yaml"):
                try:
                    with open("tasks.yaml", "r") as f:
                        shared["task_list"] = yaml.safe_load(f) or []
                except yaml.YAMLError:
                    shared["task_list"] = []
            else:
                shared["task_list"] = []
        return shared

    def exec(self, shared):
        # Read the action injected by FastAPI (default to view)
        action = shared.get("action", "view")
        return {"action": action}

    def post(self, shared, prep_res, exec_res):
        action = exec_res["action"]
        if action == "create":
            shared["task_name"] = shared.get("task_input", "")
            shared["priority_input"] = shared.get("priority_input", "")
            shared["calendar"] = shared.get("calendar_input", "")
            # Capture the description from api.py and place it in the core 'shared' dict
            shared["description"] = shared.get("description_input", "") 
        elif action in ["done", "delete"]:
            shared["target_idx"] = shared.get("target_idx")
            
        return action

class ValidationNode(Node):
    def prep(self, shared): return shared.get("task_name", "")
    
    def exec(self, task_name):
        return "valid" if len(task_name.strip()) >= 3 else "invalid"
        
    def post(self, shared, prep_res, exec_res):
        if exec_res == "invalid":
            print("⚠️ Error: Task description too vague. Please provide more detail.")
        return exec_res

class CategorizeNode(Node):
    def prep(self, shared): 
        return shared.get("priority_input", "")
        
    def exec(self, prep_res):
        text = prep_res.lower()
        # Route logic branch based on user's direct input
        triggers = ["high", "urgent", "asap", "priority", "important", "critical"]
        if any(word in text for word in triggers):
            return "high_priority"
        return "low_priority"
        
    def post(self, shared, prep_res, exec_res):
        shared["priority"] = exec_res
        return exec_res

class UpdateTaskNode(Node):
    """New Node to handle removing completed tasks."""
    def prep(self, shared):
        return shared.get("target_idx"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        idx, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            completed_task = task_list.pop(idx)
            print(f"\n✅ Marked '{completed_task['task']}' as done!")
        else:
            print(f"\n⚠️ Task number {idx + 1 if idx is not None else 'unknown'} not found.")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class ChangeStatusNode(Node):
    """Updates the status of an existing task."""
    def prep(self, shared):
        return shared.get("target_idx"), shared.get("new_status"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        idx, new_status, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            task_list[idx]["status"] = new_status
            print(f"🔄 Updated task {idx} status to {new_status}")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class ReorderTasksNode(Node):
    """Moves a task from one position to another in the list."""
    def prep(self, shared):
        return shared.get("old_index"), shared.get("new_index"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        old_index, new_index, task_list = prep_res
        if old_index is not None and new_index is not None:
            if 0 <= old_index < len(task_list) and 0 <= new_index < len(task_list):
                # Remove from old position and insert at new position
                task = task_list.pop(old_index)
                task_list.insert(new_index, task)
                print(f"🔄 Reordered task from {old_index} to {new_index}")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class DeleteTaskNode(Node):
    """New Node to handle deleting tasks without marking them done."""
    def prep(self, shared):
        return shared.get("target_idx"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        idx, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            deleted_task = task_list.pop(idx)
            print(f"\n🗑️ Deleted '{deleted_task['task']}' from the board.")
        else:
            print(f"\n⚠️ Task number {idx + 1 if idx is not None else 'unknown'} not found.")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class EditTaskDetailsNode(Node):
    """Updates the text, description, priority, and date of an existing task."""
    def prep(self, shared):
        return (
            shared.get("target_idx"),
            shared.get("task_input"),
            shared.get("description_input"),
            shared.get("priority_input"),
            shared.get("calendar_input"),
            shared.get("task_list", [])
        )
        
    def exec(self, prep_res):
        idx, task, desc, priority, cal, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            # Format HTML5 datetime-local (YYYY-MM-DDTHH:MM) to our DB format
            if cal and "T" in cal:
                cal = cal.replace("T", " ")
                if len(cal) == 16: 
                    cal += ":00" # Add seconds
            
            task_list[idx]["task"] = task
            task_list[idx]["description"] = desc
            task_list[idx]["priority"] = priority.upper()
            if cal:
                task_list[idx]["time"] = cal
                
            print(f"✏️ Updated task {idx} details")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class SaveNode(Node):
    """Updated to handle saving the task list to a YAML file."""
    def prep(self, shared): 
        return shared.get("task_list", [])
        
    def exec(self, task_list):
        try:
            with open("tasks.yaml", "w") as f:
                # default_flow_style=False ensures it looks like standard block YAML
                yaml.dump(task_list, f, sort_keys=False, default_flow_style=False)
            return "success"
        except Exception as e:
            print(f"⚠️ Error saving tasks to disk: {e}")
            return "error"
            
    def post(self, shared, prep_res, exec_res):
        return "default"

class ProcessNode(Node):
    def prep(self, shared): 
        return shared["task_name"], shared["priority"], shared.get("calendar", ""), shared.get("description", "")
        
    def exec(self, prep_res):
        task, priority, calendar, description = prep_res
        
        # --- BILINGUAL DATE PARSING LOGIC ---
        if calendar.strip():
            # Now explicitly supports Romanian and English
            parsed_date = dateparser.parse(calendar.strip(), languages=['ro', 'en'])
            schedule = parsed_date.strftime("%Y-%m-%d %H:%M:%S") if parsed_date else calendar.strip()
        else:
            schedule = get_current_timestamp()
            
        print(f"\n🧠 Thinking... breaking down '{task}' and estimating time...")
        
        prompt = (
            f"Break down the following task into 3 to 5 concise, actionable steps. "
            f"Estimate the time in minutes for each step. "
            f"Return ONLY a valid JSON list of dictionaries. "
            f"Use exactly this format: [{{\"step\": \"Action description\", \"estimated_minutes\": 15}}]. "
            f"Task: {task}. "
            f"Description: {description}" # Add description for context
        )
        
        try:
            resp = ollama.chat(
                model="gemma:2b",
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2}, 
                format="json" 
            )
            
            llm_output = resp["message"]["content"].strip()
            if llm_output.startswith("```json"):
                llm_output = llm_output.replace("```json", "").replace("```", "").strip()
            micro_steps = json.loads(llm_output)
            
        except Exception as e:
            micro_steps = [
                {"step": "Review task requirements", "estimated_minutes": 5},
                {"step": f"Manual execution required (Error: {e})", "estimated_minutes": 0}
            ]

        assistant_response = {
            "intent": "process_and_breakdown_task",
            "entities": {"task_name": task},
            "priority": priority,
            "micro_steps": micro_steps,
            "suggested_schedule": schedule,
            "actions": [f"save_to_memory('{task}')"]
        }
        
        yaml_output = yaml.dump(assistant_response, sort_keys=False, default_flow_style=False)
        
        print("🤖 Smart Task Assistant Output:")
        print(yaml_output)
        
        return "Success", schedule, assistant_response

    # (Keep your existing post method for ProcessNode exactly the same)
    def post(self, shared, prep_res, exec_res):
        status, schedule, assistant_response = exec_res
        shared["task_list"].append({
            "task": shared["task_name"],
            # Grab description from the shared state
            "description": shared.get("description", ""), 
            "priority": shared["priority"].upper(),
            "time": schedule,  
            "status": "READY",
            "full_yaml": assistant_response
        })
        return "default"

class SummaryNode(Node):
    def prep(self, shared): return shared
    def exec(self, shared):
        total_minutes = 0
        
        for item in shared.get("task_list", []):
            task_minutes = 0
            yaml_data = item.get("full_yaml", {})
            micro_steps = yaml_data.get("micro_steps", [])
            
            if isinstance(micro_steps, list):
                for step in micro_steps:
                    if isinstance(step, dict):
                        task_minutes += step.get("estimated_minutes", 0)
            elif isinstance(micro_steps, dict):
                task_minutes += micro_steps.get("estimated_minutes", 0)
                
            total_minutes += task_minutes
            item["calculated_minutes"] = task_minutes # Save to item for the frontend
            
        # Attach the data to shared so FastAPI can return it as JSON
        shared["summary_data"] = {
            "tasks": shared.get("task_list", []),
            "total_minutes": total_minutes
        }
        return "Finished"
        
    def post(self, shared, prep_res, exec_res):
        return "default"
    
class CheckDeadlinesNode(Node):
    """Proactively checks for tasks due within an hour or overdue."""
    def prep(self, shared):
        return shared.get("task_list", [])

    def exec(self, task_list):
        now = datetime.now()
        alerts = []
        
        for item in task_list:
            time_str = item.get("time", "")
            try:
                # We expect the strict format "YYYY-MM-DD HH:MM:SS" we set up earlier
                task_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                time_diff = (task_time - now).total_seconds()
                
                # If due in the next 3600 seconds (1 hour) and not in the past
                if 0 <= time_diff <= 3600:
                    mins_left = int(time_diff // 60)
                    alerts.append(f"🔔 REMINDER: '{item['task']}' is due in {mins_left} minutes!")
                # If the time has already passed
                elif time_diff < 0:
                    alerts.append(f"⚠️ OVERDUE: '{item['task']}' was due at {time_str}!")
            except ValueError:
                # Skip tasks that don't have a valid, parseable strict timestamp
                pass
        
        # Print alerts if any exist
        if alerts:
            print("\n" + "❗"*20)
            for alert in alerts:
                print(alert)
            print("❗"*20)
            
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"
    
class EditTaskDetailsNode(Node):
    """Updates the text, description, priority, and date of an existing task."""
    def prep(self, shared):
        return (
            shared.get("target_idx"),
            shared.get("task_input"),
            shared.get("description_input"),
            shared.get("priority_input"),
            shared.get("calendar_input"),
            shared.get("task_list", [])
        )
        
    def exec(self, prep_res):
        idx, task, desc, priority, cal, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            # Format HTML5 datetime-local (YYYY-MM-DDTHH:MM) to our DB format
            if cal and "T" in cal:
                cal = cal.replace("T", " ")
                if len(cal) == 16: 
                    cal += ":00" # Add seconds
            
            task_list[idx]["task"] = task
            task_list[idx]["description"] = desc
            task_list[idx]["priority"] = priority.upper()
            if cal:
                task_list[idx]["time"] = cal
                
            print(f"✏️ Updated task {idx} details")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"