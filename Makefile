ifeq ($(OS),Windows_NT)
    PYTHON_EXE = venv\Scripts\python.exe
    PIP_EXE = venv\Scripts\pip.exe
    CLEAN_CMD = if exist venv rmdir /s /q venv
    # Uses native cmd to write a fresh file, avoiding PowerShell crashes
    TOUCH = echo done > venv\.venv_timestamp
else
    PYTHON_EXE = venv/bin/python
    PIP_EXE = venv/bin/pip
    CLEAN_CMD = rm -rf venv
    TOUCH = touch venv/.venv_timestamp
endif

.PHONY: all clean run

all: venv/.venv_timestamp

# Use forward slashes for the target name to stop Make from misinterpreting slashes
venv/.venv_timestamp: requirements.txt
	@echo "Creating virtual environment and installing packages..."
	python -m venv venv
	$(PIP_EXE) install --upgrade pip
	$(PIP_EXE) install -r requirements.txt
	@$(TOUCH)

run: venv/.venv_timestamp
	$(PYTHON_EXE) -m uvicorn app.main:app --reload

clean:
	@$(CLEAN_CMD)
