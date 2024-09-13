__author__ = "Adam Thompson"
__date__ = "2024/09"

### Imports ###
import requests
import pandas as pd
import json
import os
import time
import datetime
import logging

### Logging Configuration
logger = logging.getLogger(__name__)
timeStamp = datetime.datetime.now().strftime("%Y_%m_%d")
logging.basicConfig(
    filename=f"HuntGroupLog_{timeStamp}.log",
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p', 
    encoding='utf-8', 
    level=logging.DEBUG)

### Variable Definitions ###
csvFilePath = 'Test.csv'
accessToken = 'MWI4ZmNjNTUtMDc3MC00MmJhLTljZTAtNmUxOGMzYWQ3MjIzNTE5ZmY1YWItOGNm_P0A1_e3266292-7ee3-4149-ae94-80a7ae54f891'
orgId = ''
loopCount = 0
errorCount = 0
locationId = ''

### API Endpoints ###
myDetailsUrl = 'https://webexapis.com/v1/people/me'
locationsUrl = 'https://webexapis.com/v1/locations'
numbersUrl = 'https://webexapis.com/v1/telephony/config/numbers'
hgUrl = 'https://webexapis.com/v1/telephony/config/locations/'


### User Input ###
### Validate Access to CSV File ###
validationSuccess = 0
while (validationSuccess == 0):
    if not csvFilePath:
        csvFilePath = input('Please ender the full file path of the CSV file you wish to use:  ')
    csvFilePath = os.path.expanduser(csvFilePath)
    if (not os.path.isfile(csvFilePath)):
        logging.error(f"Selected CSV at {csvFilePath} not found")
        print('❌ No Input CSV file found on your device at: ' + csvFilePath)
        print('Please check the file path you entered above and try again.\n')
        csvFilePath = ''
    else:
        validationSuccess = 1

logging.info(f"Input file, {csvFilePath} has been successfully found")
print('✅ Input CSV file found at: ', csvFilePath, '\n')
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
        logging.error(f"Access token provided is not valid")
        print('❌ Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
        accessToken = ''
    else:
        validationSuccess = 1

name = validationResponse.json()['firstName']
logging.info('Access token has been validated')
print('✅ Access token has been validated.\n')
validationSuccess = 0

       
### Read in csvFile ###
data = pd.read_csv(csvFilePath, keep_default_na=False)
huntGroups = data.to_dict(orient='records')
totalHuntGroups = len(huntGroups)
logging.debug(f"{totalHuntGroups} record(s) have been read in")

while (loopCount < totalHuntGroups):
    ### Get LocationId by name
    logging.debug(f"Starting request for id of location {huntGroups[loopCount]['Location']}")
    locationResponse = requests.get(f"{locationsUrl}?name={huntGroups[loopCount]['Location']}", 
                                    headers={'Authorization': 'Bearer ' + accessToken})
    
    ### Handle Too Many Requests
    if (locationResponse.status_code == 429):
        logging.debug(f"Status Code: {locationResponse.status_code} -- Retrying request in 30 seconds")
        time.sleep(30)
        locationResponse = requests.get(f"{locationsUrl}?name={huntGroups[loopCount]['Location']}", 
                                    headers={'Authorization': 'Bearer ' + accessToken})
    
    if (locationResponse.status_code != 200 or len(locationResponse.json()['items']) == 0):
        if (locationResponse.status_code != 200):
            logging.error(f"Get locationId API call error: {str(locationResponse.status_code)} for location {str(huntGroups[loopCount]['Location'])}")
        else:
            logging.error(f"No location found with name {huntGroups[loopCount]['Location']}")
    else:
        locationId = locationResponse.json()['items'][0]['id']
        logging.debug(f"Id {locationId} found for location named {huntGroups[loopCount]['Location']}")

        ### Get Ids for all members
        members = huntGroups[loopCount]['Members'].split(',')
        
        #### Loop through identified extensions
        logging.info(f'Starting looping through {len(members)} members to get id')
        logging.debug(f"Member list: {members}")
        memberIds = []
        for member in members:
            logging.debug(f"Getting id for phoneNumber/extension: {member}")
            if (len(member) >= 10):
                parameter = f"phoneNumber={member}"
            else:
                parameter = f"extension={member}"

            numberResponse = requests.get(f"{numbersUrl}?{parameter}", headers={'Authorization': 'Bearer ' + accessToken})

            if (numberResponse.status_code != 200 or len(numberResponse.json()['phoneNumbers']) == 0):
                if (numberResponse.status_code != 200):
                    logging.error(f"Get numberId API call error: {str(numberResponse.status_code)} for {member}")
                else:
                    logging.error(f"No numberId for {member} found")
            else:
                memberId = numberResponse.json()['phoneNumbers'][0]['owner']['id']
                memberIds.append({"id": memberId})
                logging.debug(f"Id {memberId} found for phoneNumber/extension {member}")

        ### Create Hunt Group
        #### Generate Headers
        hgHeaders = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + accessToken
        }
        #### Generate Body
        hgBody = json.dumps(
            {
                "name": huntGroups[loopCount]['Name'],
                "phoneNumber": huntGroups[loopCount]['PhoneNumber'],
                "extension": huntGroups[loopCount]['Extension'],
                "firstName": huntGroups[loopCount]['FirstName'],
                "lastName": huntGroups[loopCount]['LastName'],
                "callPolicies": {
                    "policy": huntGroups[loopCount]['RingPolicy'],
                    "waitingEnabled": True,
                    "groupBusyEnabled": True,
                    "allowMembersToControlGroupBusyEnabled": True,
                    "noAnswer": {
                        "nextAgentEnabled": False,
                        "nextAgentRings": 5,
                        "forwardEnabled": False,
                        "numberOfRings": 15,
                        "destinationVoicemailEnabled": False
                        },
                    "businessContinuity": {
                        "enabled": False,
                        "destinationVoicemailEnabled": False
                        }
                    },
                "agents": memberIds,
                "enabled": True,
                "huntGroupCallerIdForOutgoingCallsEnabled": True
            })
        #### Send Post Request
        hgResponse = requests.post(f"{hgUrl}/{locationId}/huntGroups",
                                headers=hgHeaders, data=hgBody)
        
        if (hgResponse.status_code != 201 or len(hgResponse.json() == 0)):
            if (hgResponse.status_code != 201):
                logging.error(f"Create Hunt Group API call error: {huntGroups[loopCount]['Name']}::{str(hgResponse.status_code)}")
            else:
                logging.error(f"Error creating hunt group: {huntGroups[loopCount]['Name']}")
        else:
            logging.info(f"Hunt Group {huntGroups[loopCount]['Name']} successfully created")

        loopCount += 1
