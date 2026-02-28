# 🚀 Smart Task Assistant (Web Edition)

The **Smart Task Assistant** is a high-performance productivity dashboard that leverages **PocketFlow**  and local LLMs to transform simple task titles into actionable project plans. Inspired by modern project management tools, it features a sleek, responsive Web UI, drag-and-drop reordering, and AI-powered micro-step breakdowns.

## ✨ Key Features

* **AI Task Analysis**: Uses local LLMs (via Ollama) to automatically generate micro-steps and time estimates for every task.
* **Dynamic Web Dashboard**: A ClickUp-inspired interface with status groupings (READY, IN PROGRESS, COMPLETE).
* **Modal Task Creation**: A clean popup interface for adding tasks with detailed descriptions and native calendar date selection.
* **Drag-and-Drop Reordering**: Intuitively organize your priority list directly in the browser.
* **Persistent YAML Storage**: All tasks, metadata, and AI plans are saved to a local `tasks.yaml` file for easy access and backup.
* 
**PocketFlow Architecture**: Built using a node-based graph logic for robust state management.



---

## 🛠️ Tech Stack

* 
**Logic Engine**: [PocketFlow](https://www.google.com/search?q=https://github.com/marqbritt/PocketFlow) (Finite State Machine / Graph logic).


* **Backend**: FastAPI (Python).
* **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript.
* **AI Model**: Ollama (`gemma:2b`).
* **Data Format**: YAML (via `PyYAML`).

---

## 📋 Prerequisites

1. **Python 3.10+**
2. **Ollama**: Install from [ollama.com](https://ollama.com).
3. **Gemma Model**:
```bash
ollama pull gemma:2b

```



---

## 📂 Project Structure

* **`api.py`**: The FastAPI server that handles web requests and triggers the PocketFlow logic.
* **`flow.py`**: Defines the application's graph architecture, routing actions like `create`, `edit`, `status`, and `reorder`.
* **`nodes.py`**: Contains the core logic classes (Nodes) for validating input, processing AI steps, and managing the task list.
* **`index.html`**: The complete frontend dashboard, including the task modal and drag-and-drop logic.
* **`utils.py`**: Provides ISO-standard timestamps for consistent task logging.
* **`tasks.yaml`**: The local database file where all task data is stored.
* 
**`requirements.txt`**: List of Python dependencies including `pocketflow`.



---

## 🚀 Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/Rayns15/PocketFlow-Agent-Smart-Task-Assistant-WebUI.git
cd PocketFlow-Agent-Smart-Task-Assistant-WebUI

```

**2. Install dependencies**

```bash
pip install -r requirements.txt
pip install fastapi uvicorn dateparser ollama pyyaml

```

**3. Run the Backend API**

```bash
python api.py

```

**4. Launch the UI**
Simply open `index.html` in any modern web browser.

---

## 🧠 Application Logic Flow

The system operates on a directed graph where user actions in the browser trigger specific paths through the backend nodes:

1. **Input**: The API captures the web request.
2. **Process**: If a new task is created, the `ProcessNode` consults Ollama to break it down.
3. **Save**: The `SaveNode` updates the `tasks.yaml` file.
4. **Sync**: The frontend fetches the updated list and renders the new state instantly.

---

