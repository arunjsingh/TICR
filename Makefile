ifeq ($(OS),Windows_NT)
  PYTHON_EXE = venv\Scripts\python.exe
  PIP_EXE = venv\Scripts\pip.exe
  CLEAN_CMD = if exist venv rmdir /s /q venv
  TOUCH = echo done > venv\.venv_timestamp
  VENV_CREATE_CMD = py -m venv venv --clear
  PIP_UPGRADE_CMD = $(PYTHON_EXE) -m pip install --disable-pip-version-check --upgrade pip
  
  # Windows-specific Ollama commands
  OLLAMA_EXE = ollama
  INSTALL_OLLAMA_CMD = powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com' -OutFile 'OllamaSetup.exe'; Start-Process 'OllamaSetup.exe' -ArgumentList '/silent' -Wait; Remove-Item 'OllamaSetup.exe'"
else
  PYTHON_EXE = venv/bin/python
  PIP_EXE = venv/bin/pip
  CLEAN_CMD = rm -rf venv
  TOUCH = touch venv/.venv_timestamp
  VENV_CREATE_CMD = python3 -m venv venv
  PIP_UPGRADE_CMD = $(PIP_EXE) install --disable-pip-version-check --upgrade pip
  
  # Unix-specific Ollama commands
  OLLAMA_EXE = ollama
  INSTALL_OLLAMA_CMD = curl -fsSL https://ollama.com | sh
endif

# Define the Qwen model parameter size you want (e.g., 7b, 14b, coder:7b)
MODEL_NAME = qwen2.5:14b

.PHONY: all clean run setup-ollama pull-model

# Included setup-ollama and pull-model into the default build sequence
all: setup-ollama pull-model venv/.venv_timestamp

setup-ollama:
	@echo "Checking if Ollama is installed..."
	@$(OLLAMA_EXE) --version >nul 2>&1 || (echo "Ollama not found. Installing Ollama..." && $(INSTALL_OLLAMA_CMD))

pull-model: setup-ollama
	@echo "Downloading and preparing Qwen model ($(MODEL_NAME))..."
	@$(OLLAMA_EXE) pull $(MODEL_NAME)

venv/.venv_timestamp: requirements.txt
	@echo "Creating virtual environment and installing packages..."
	$(VENV_CREATE_CMD)
	$(PIP_UPGRADE_CMD)
	$(PIP_EXE) install --disable-pip-version-check -r requirements.txt
	@$(TOUCH)

run: all
	$(PYTHON_EXE) -m uvicorn app.main:app --reload

clean:
	@$(CLEAN_CMD)

