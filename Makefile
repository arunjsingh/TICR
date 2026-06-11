ifeq ($(OS),Windows_NT)
  PYTHON_EXE = venv\Scripts\python.exe
  PIP_EXE = venv\Scripts\pip.exe
  CLEAN_CMD = if exist venv rmdir /s /q venv
  TOUCH = echo done > venv\.venv_timestamp
  VENV_CREATE_CMD = py -m venv venv --clear
  # Windows Fix: Upgrade pip via the python module tool instead of the pip executable
  PIP_UPGRADE_CMD = $(PYTHON_EXE) -m pip install --disable-pip-version-check --upgrade pip
else
  PYTHON_EXE = venv/bin/python
  PIP_EXE = venv/bin/pip
  CLEAN_CMD = rm -rf venv
  TOUCH = touch venv/.venv_timestamp
  VENV_CREATE_CMD = python3 -m venv venv
  PIP_UPGRADE_CMD = $(PIP_EXE) install --disable-pip-version-check --upgrade pip
endif

.PHONY: all clean run

all: venv/.venv_timestamp

venv/.venv_timestamp: requirements.txt
	@echo "Creating virtual environment and installing packages..."
	$(VENV_CREATE_CMD)
	$(PIP_UPGRADE_CMD)
	$(PIP_EXE) install --disable-pip-version-check -r requirements.txt
	@$(TOUCH)

run: venv/.venv_timestamp
	$(PYTHON_EXE) -m uvicorn app.main:app --reload

clean:
	@$(CLEAN_CMD)
