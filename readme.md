# TICR

### Windows Installation Notes
* **Python Launcher:** Ensure you check the "Add python.exe to PATH" option when installing Python.
* **Locked Files Error:** If you get an error saying `Unable to copy venvlauncher.exe`, it means a hidden terminal is still running the app. Close your terminal/VS Code windows and try again.

```bash
# Download the repo using git 
git clone https://github.com/arunjsingh/TICR 
cd TICR 
git checkout master 

# To execute the code 

# Install and run the backend portion of the TICR. 
make run 

# Install and run the frontend (UI) portion of the TICR. 

# Frontend will only run on CMD window, 
# If you are using a PowerShell terminal, you may need to run this command first. Keep # # in mind that depending on your machine's security settings, results may vary:

# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

npm install 
npm run dev
```
