ifeq ($(OS),Windows_NT)
  PYTHON_EXE = venv\Scripts\python.exe
  PIP_EXE = venv\Scripts\pip.exe
  CLEAN_CMD = if exist venv rmdir /s /q venv
  TOUCH = echo done > venv\.venv_timestamp
  
  # Automatically check if 'py' launcher exists, otherwise use 'python'
  VENV_CREATE_CMD = where py >nul 2>nul && py -m venv venv || python -m venv venv
else
  PYTHON_EXE = venv/bin/python
  PIP_EXE = venv/bin/pip
  CLEAN_CMD = rm -rf venv
  TOUCH = touch venv/.venv_timestamp
  VENV_CREATE_CMD = python3 -m venv venv
endif

.PHONY: all clean run

all: venv/.venv_timestamp

venv/.venv_timestamp: requirements.txt
	@echo "Creating virtual environment and installing packages..."
	$(VENV_CREATE_CMD)
	$(PIP_EXE) install --upgrade pip
	$(PIP_EXE) install /-r requirements.txt
	@$(TOUCH)

run: venv/.venv_timestamp
	$(PYTHON_EXE) -m uvicorn app.main:app --reload

clean:
	@$(CLEAN_CMD)
