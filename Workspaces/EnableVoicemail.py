__author__ = "Adam Thompson"
__date__ = "2025/07"

### Imports ###
import urllib.parse
import requests
import pandas as pd
import json
import os
import urllib
import time
import datetime
import logging

### Variable Definitions ###

csvFilePath = ''
accessToken = ''
orgId = ''
loopCount = 0
errorCount = 0
callingLicenseId = ''
workspaceLicenseId = ''

### API Endpoints ###
getMyDetailsUrl = 'https://webexapis.com/v1/people/me'
getLicensesUrl = 'https://webexapis.com/v1/licenses'
getLocationUrl = 'https://webexapis.com/v1/locations'

workspaceUrl = 'https://webexapis.com/v1/workspaces'
deviceUrl = 'https://webexapis.com/v1/devices'

### Logging Configuration
logger = logging.getLogger(__name__)
timeStamp = datetime.datetime.now().strftime("%Y_%m_%d")
logging.basicConfig(
    filename=f"WorkspaceLog_{timeStamp}.log",
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p', 
    encoding='utf-8', 
    level=logging.DEBUG)

### Validate Access to CSV File ###
validationSuccess = 0
while (validationSuccess == 0):
    if not csvFilePath:
        csvFilePath = input('Please ender the full file path of the CSV file you wish to use:  ')
    csvFilePath = os.path.expanduser(csvFilePath)
    if (not os.path.isfile(csvFilePath)):
        print('❌ No Input CSV file found on your device at: ' + csvFilePath)
        print('Please check the file path you entered above and try again.\n')
        csvFilePath = ''
    else:
        validationSuccess = 1

print('✅ Input CSV file found at: ', csvFilePath, '\n')
validationSuccess = 0

### Validate Access Token ###
while (validationSuccess == 0):
    if not accessToken :
        accessToken = input('Please enter your access token:  ')
    # Get People API Call to validate access token.
    validationResponse = requests.get(getMyDetailsUrl, headers={'Authorization': 'Bearer ' + accessToken})
    if validationResponse.status_code == 401:
        # This means the access token was invalid.
        print('❌ Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
        accessToken = ''
    else:
        validationSuccess = 1

# name = validationResponse.json()['firstName']
print('✅ Access token has been validated.\n')
validationSuccess = 0

### Get OrgId ###
while validationSuccess == 0:
    if not orgId:
        orgId = input('Please enter the orgId: ')
    org_response = requests.get(f"https://webexapis.com/v1/organizations/{orgId}", headers={'Authorization': 'Bearer ' + accessToken})
    if org_response.status_code == 200:
        orgId = org_response.json()['id']
        validationSuccess = 1
    else:
        print('❌ OrgId was invalid.  Please check your orgId was entered correctly and hasn\'t expired and try again below.\n')
        orgId = ''

print('✅ The entered orgId has been validated.\n')
validationSuccess = 0

### Read in csvFile ###
data = pd.read_csv(csvFilePath)
workspaces = data.to_dict(orient='records')
totalWorkspaces = len(workspaces)

while (loopCount < totalWorkspaces):
    ### Get Workspace ID
    logging.debug(f"Working on workspace: {workspaces[loopCount]['Display Name']}")
    print(f"Working on workspace: {workspaces[loopCount]['Display Name']}")
    getWsResponse = requests.get(f"{workspaceUrl}?orgId={orgId}&displayName={urllib.parse.quote(workspaces[loopCount]['Display Name'])}", headers={'Authorization': 'Bearer ' + accessToken})
    workspacdId = getWsResponse.json()['items'][0]['id']

    getWsVMStatus = requests.get(f"https://webexapis.com/v1/telephony/config/workspaces/{workspacdId}/voicemail?orgId={orgId}", headers={'Authorization': 'Bearer ' + accessToken})
    vmStatus = getWsVMStatus.json()['enabled']

    logging.debug(f"Configuring voicemail for workspace: {workspaces[loopCount]['Display Name']}")
    workspaceBody = json.dumps({
        "enabled": True,
        "notifications": {
            "enabled": False,
        },
        "sendAllCalls": {
                "enabled": False
        },
        "sendBusyCalls": {
                "enabled": True,
                "greeting": "DEFAULT"
        },
        "sendUnansweredCalls": {
                "enabled": True,
                "greeting": "DEFAULT",
                "numberOfRings": 3
        },
        "transferToNumber": {
                "enabled": False
        },
        "emailCopyOfMessage": {
                "enabled": False,
        }
    })

    workspaceeHeaders = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken
    }
    workspaceResponse = requests.put(f"https://webexapis.com/v1/telephony/config/workspaces/{workspacdId}/voicemail?orgId={orgId}", headers=workspaceeHeaders, data=workspaceBody)

    if workspaceResponse.status_code == 204:
        print(f"     Voicemail successfully enabled")
    else:
        print(f"     Error: Voicemail not enabled")

    loopCount += 1
