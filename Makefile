# Define variables for Windows
VENV := venv
PYTHON := $(VENV)\Scripts\python.exe
PIP := $(VENV)\Scripts\pip.exe
UVICORN := $(VENV)\Scripts\uvicorn.exe

# Default target
all: install

# Create virtual environment and install requirements
install: $(VENV)\Scripts\activate

$(VENV)\Scripts\activate: requirements.txt
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	powershell -Command "(Get-Item '$@').LastWriteTime = Get-Date"

# New Run target: starts the FastAPI server
run:
	$(PYTHON) -m uvicorn app.main:app --reload


# Clean up the environment
clean:
	-powershell -Command "if (Test-Path $(VENV)) { Remove-Item -Recurse -Force $(VENV) }"
	-powershell -Command "Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force"


.PHONY: all install clean run
