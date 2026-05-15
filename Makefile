# Define variables for Windows
VENV := venv
PYTHON := $(VENV)\Scripts\python.exe
PIP := $(VENV)\Scripts\pip.exe
UVICORN := $(VENV)\Scripts\uvicorn.exe
ALEMBIC := $(VENV)\Scripts\alembic.exe

# Default target runs everything in the new order
all: install

# Install orchestration: Python finishes entirely before Node is checked
install: install-py check-node install-js

# Create virtual environment and install Python requirements
install-py: $(PYTHON)
$(PYTHON): requirements.txt
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	powershell -Command "(Get-Item '$(PYTHON)').LastWriteTime = Get-Date"

# Check if Node.js/npm is installed (Only runs AFTER install-py completes)
check-node: install-py
	@powershell -Command "\
		if (Get-Command npm -ErrorAction SilentlyContinue) {\
			Write-Host '=> Python packages installed. Now checking for Node.js...' -ForegroundColor Green;\
			Write-Host '=> Node.js/npm detected.' -ForegroundColor Green;\
		} else {\
			Write-Host '==================================================' -ForegroundColor Red;\
			Write-Host 'PYTHON PACKAGES INSTALLED SUCCESSFULY, BUT...' -ForegroundColor Yellow;\
			Write-Host 'ERROR: Node.js and npm are not installed!' -ForegroundColor Red;\
			Write-Host 'Tailwind and Axios cannot be installed without them.' -ForegroundColor Yellow;\
			Write-Host 'Please download and install Node.js from:' -ForegroundColor Yellow;\
			Write-Host 'https://nodejs.org' -ForegroundColor Cyan;\
			Write-Host '==================================================' -ForegroundColor Red;\
			Exit 1;\
		}"

# Install Tailwind, PostCSS, Autoprefixer, and Axios (Runs AFTER check-node passes)
install-js: check-node package.json
	npm config set strict-ssl false
	npm install tailwindcss postcss autoprefixer axios
	npm config set strict-ssl true
	powershell -Command "(Get-Item 'node_modules').LastWriteTime = Get-Date"

# Starts the FastAPI server
run: install
	$(UVICORN) app.main:app --reload

# Database Migration Targets (Alembic + Postgres)
db-init: install-py
	$(ALEMBIC) init alembic

db-migrate: install-py
	@read -p "Enter migration message: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

db-upgrade: install-py
	$(ALEMBIC) upgrade head

# Clean up Python environment only (preserves node_modules)
clean:
	-powershell -Command "if (Test-Path $(VENV)) { Remove-Item -Recurse -Force $(VENV) }"
	-powershell -Command "Get-ChildItem -Recurse -Include __pycache__, *.pyc, *.pyo | Remove-Item -Recurse -Force"

.PHONY: all check-node install install-py install-js run db-init db-migrate db-upgrade clean
