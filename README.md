# **Inventory System - Team Setup Guide**
(Python + Flask + HTML/CSS + SQLite)
This is a student-built web-based inventory system. This README is written for first-time setup only, so follow it exactly to avoid breaking the setup.

### **NOTE:**
If you have not installed the required tools yet, do that before cloning the project. This guide assumes you can open a terminal and run basic commands.
> ### Required tools:
> - Python 3.x (check by running: python --version)
> - VS Code (code editor)
> - Git (version control; check by running: git --version)

> ### Optional tool supports for view and testing (recommended):
> - DB Browser for SQLite (to view tables/records later)
> - Postman or Insomnia (to test endpoints later)
> - GitHub Desktop (optional if you struggle with terminal Git)


### Clone the repository for the first time
> Where to type commands: Use the VS Code terminal (Terminal -> New Terminal) or your system terminal. Make sure you are in the folder where you want the project to live (example: Desktop).
1) Clone and enter the project folder:
``git clone <REPO_URL> cd inventory-system``
2) Confirm you are in the correct 
```
# macOS/Linux/PowerShell
pwd
ls
# Windows CMD
cd
dir
```
You should see files like app/, run.py, requirements.txt, and .gitignore in the project root.

> ### Create your .gitignore correctly (avoid .gitignore.txt)
>***Important: the file must be named exactly ".gitignore" (no .txt). Some Windows setups hide file extensions, which can accidentally create ".gitignore.txt".***

> How to create it safely:
- the file in the project root (same level as app/ and run.py).
- Name it exactly: .gitignore
- If you already have .gitignore.txt, rename it to .gitignore.

 __Recommended .gitignore contents:__
```.venv/
__pycache__/
*.pyc
instance/
*.sqlite
.env
.vscode/
```

### Set up local-only files/folders (these will NOT appear after pulling)
When you pull/clone the repo, you only receive the shared code. Each member must create local-only items on their own machine.

#### A. Create a virtual environment (local Python setup)
Run these commands in the project root (inventory-system/):
```
python -m venv .venv
```

#### Activate the virtual environment:
```
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```
If PowerShell blocks activation, close the terminal, open a NEW PowerShell terminal, then run:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

#### B. Install Python packages (dependencies)
With the venv activated, run:
```
pip install -r requirements.txt
```

#### C. Instance folder and SQLite database
> The instance/ folder is where the local SQLite database will be created later. It can be empty at the start.
- If instance/ does not exist locally, create it in the project root.
- The database file (example: inventory.sqlite) will appear only after the database setup code runs.

#### D. Environment file (.env) when the team adds configuration
Later, the project may include a .env.example file. Each member will create their own .env locally by copying it.
```
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```
Never rename .env to .env.txt. It must be exactly .env.

### Run the project (local)
In the project root, with __venv activated__:
```
python run.py
```
Open your browser at: ``http://127.0.0.1:5000/``
_Stop the server by pressing CTRL + C in the terminal._

### Quick reference: where to put your work files
>- HTML pages: app/templates/
>- CSS files: app/static/css/
>- JavaScript files: app/static/js/
>- Python routes (page links): app/routes/
>- Do not place new code files directly in the project root unless instructed by the team lead.

### Troubleshooting basics
>- If a command fails, confirm you are in the project root (inventory-system/) and your venv is activated.
>- If you see “Template not found”, confirm the folder is named app/templates (plural).
>- If pip installs fail, upgrade pip: python -m pip install --upgrade pip, then retry.
