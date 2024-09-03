__author__ = "Adam Thompson"
__date__ = "2024/08"

### Imports ###
import urllib.parse
import requests
import pandas as pd
import json
import os
import urllib
import time
import datetime

### Variable Definitions ###

csvFilePath = ''
accessTOken = ''
orgId = ''
loopCount = 0
errorCount = 0
locationId = ''

### API Endpoints ###
myDetailsUrl = 'https://webexapis.com/v1/people/me'
locationsUrl = 'https://webexapis.com/v1/locations'



### User Input ###
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
timeStamp = datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S")
logFilePath = os.path.join(os.path.dirname(csvFilePath),f"Log_{timeStamp}.csv")
validationSuccess = 0

### Validate Access Token ###
while (validationSuccess == 0):
    if not accessToken :
        accessToken = input('Please enter your access token:  ')
    # Get People API Call to validate access token.
    validationResponse = requests.get(myDetailsUrl,
                headers={'Authorization': 'Bearer ' + accessToken})
    if validationResponse.status_code == 401:
        # This means the access token was invalid.
        print('❌ Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
        accessToken = ''
    else:
        validationSuccess = 1

name = validationResponse.json()['firstName']
print('✅ Access token has been validated.\n')
validationSuccess = 0

       
### Read in csvFile ###
data = pd.read_csv(csvFilePath)
huntGroups = data.to_dict(orient='records')
totalHuntGroups = len(huntGroups)

with open(logFilePath, 'w') as logFile:
    logFile.write('Line,User,Message')

while (loopCount < totalHuntGroups):
    ### Get LocationId by name
    locationResponse = requests.get(f"{locationsUrl}?name={huntGroups['loopCount']['Location']}", 
                                    headers={'Authorization': 'Bearer ' + accessToken})
    locationId = locationResponse.json()['items'][0]['id']

    ### TODO: Add Error Handling

    ### Get Ids for all members
    members = huntGroups['loopCount']['members'].split(',')
    totalMembers = len(members)
    


    ### Create Hunt Group
    ## Generate Headers
    hgHeaders = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken
    }
    ## Generate Body
    hgBody = json.dumps({})
    ## Send Post Request
    hgResponse = requests.post(f"{locationsUrl}/{locationId}/huntGroups",
                               headers=hgHeaders, data=hgBody)

loopCount += 1
