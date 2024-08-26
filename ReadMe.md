# Webex Calling Automation Utilities

| Category | Filename           | Language | Description                                            |
| -------- | ------------------ | -------- | ------------------------------------------------------ |
| General  | BulkDeleteUsers.py | Python   | Script to bulk delete users from Control Hub           |
| Calling  | BulkSharedLines.py | Python   | Script to bulk assign shared lines to user's Webex App |

# Getting Started
### How to get your Webex Access Token
#### Personal Access Token
A personal access token is a short-lived access token you can use to make Webex API calls on your own behalf. Any actions taken through the API will be done as you. Personal access tokens expire 12 hours after you sign in to the Developer Portal and should not be used in production environments. 

You can grab your token [here](https://developer.webex.com/docs/getting-started)
### Tool Setup
#### Get the Code
**Cloning the Repo**
- `git clone https://github.com/LUSCollab/WebexAutomation.git`
- `cd WebexAutomation`
- **Setting up a Virtual Environment with [venv](https://docs.python.org/3/library/venv.html) is recommended**
- `pip install -r requirements.txt`

**Downloading the Repo**
- [Download Code Here](https://github.com/LUSCollab/WebexAutomation.git)
- Unzip to local folder
- **Setting up a Virtual Environment with [venv](https://docs.python.org/3/library/venv.html) is recommended**
- `pip install -r requirements.txt`

#### Running the utility
- Navigate to the folder of the utility you would like to run.
- Run `python <<utilityName>>.py`
- Follow the prompts to enter the data file and your personal access token.
# Known Issues
Refer [here](https://github.com/LUSCollab/WebexAutomation/issues) for issue tracking.
# Getting Help
If you have any questions, concerns, bug reports, etc., please create an issue against this repository.
