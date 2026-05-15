# Define variables for Windows
VENV       := venv
PYTHON     := $(VENV)\Scripts\python.exe
PIP        := $(VENV)\Scripts\pip.exe
UVICORN    := $(VENV)\Scripts\uvicorn.exe
ALEMBIC    := $(VENV)\Scripts\alembic.exe

# Default target
all: install

# Create virtual environment and install requirements
install: $(PYTHON)

$(PYTHON): requirements.txt
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	powershell -Command "(Get-Item '$(PYTHON)').LastWriteTime = Get-Date"

# Starts the FastAPI server
run: install
	$(UVICORN) app.main:app --reload

# Database Migration Targets (Alembic + Postgres)
db-init: install
	$(ALEMBIC) init alembic

db-migrate: install
	@read -p "Enter migration message: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

db-upgrade: install
	$(ALEMBIC) upgrade head

# Clean up the environment
clean:
	-powershell -Command "if (Test-Path $(VENV)) { Remove-Item -Recurse -Force $(VENV) }"
	-powershell -Command "Get-ChildItem -Recurse -Include __pycache__, *.pyc, *.pyo | Remove-Item -Recurse -Force"

.PHONY: all install run db-init db-migrate db-upgrade clean
