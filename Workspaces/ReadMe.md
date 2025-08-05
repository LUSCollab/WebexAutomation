# Webex Calling Workspace Voicemail Enablement

Simple script that enabls a workspace's voicemail box in bulk.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Setup Instructions

### 1. How to get your Webex Access Token
#### Personal Access Token
A personal access token is a short-lived access token you can use to make Webex API calls on your own behalf. Any actions taken through the API will be done as you. Personal access tokens expire 12 hours after you sign in to the Developer Portal and should not be used in production environments. 

You can grab your token [here](https://developer.webex.com/docs/getting-started)

### 2. Create a Virtual Environment

Create a virtual environment to isolate project dependencies:

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**On Windows:**
```bash
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### 4. Install Requirements

With the virtual environment activated, install the project dependencies:

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

You can verify that everything is installed correctly by running:

```bash
pip list
```

This will show all installed packages in your virtual environment.

## Usage

The script will use the name of the workspace, so every workspace that needs to have voicemail enabled should be listed in the CSV file. An example CSV file has been provided. The script also assumes the workspace has been provisioned with a Workspace Professional license. 

You will need your personal Access Token and the Organization ID for the customer you are working in. 

```bash
python EnableVoicemail.py
```

## Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```

## Project Structure

```
Workspaces
├── venv/                # Virtual environment (auto-generated)
├── requirements.txt     # Project dependencies
├── EnableVoicemail.py   # Main application file
├── README.md            # This file
└── sampledata.csv       # Sample import CSV file
```

## Troubleshooting

### Common Issues

**Virtual environment activation not working:**
- Make sure you're in the correct directory
- On Windows, try running as administrator if you get permission errors
- Ensure Python is properly installed and added to PATH

**pip install fails:**
- Make sure your virtual environment is activated
- Try upgrading pip: `python -m pip install --upgrade pip`
- Check if you have the correct Python version installed

**Module not found errors:**
- Ensure your virtual environment is activated
- Verify all requirements are installed: `pip install -r requirements.txt`