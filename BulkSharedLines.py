__author__ = "Adam Thompson"
__date__ = "2024/08"

### Imports ###
import urllib.parse
import requests
import pandas as pd
import json
import os
import csv
import urllib
import time
import datetime

### Variable Definitions ###
csvFilePath = ''
accessToken = ''
orgId = ''
records = []
loopCount = 0
errorCount = 0
userId = ''
desktopClientId = ''
lineId = ''
getMyDetailsURL = 'https://webexapis.com/v1/people/me'

### User Input ###
print('You will need the following:')
print('  1. The full file path for the input CSV file\n       (ex: C:\Path\To\File.csv)')
print('  2. Webex API access token\n       (You can get this at https://developer.webex.com)')
print('  3. The OrgId of the target Webex tenant if using a partner account')

### Validate Access to CSV File ###
validationSuccess = 0
while (validationSuccess == 0):
    if not csvFilePath:
        csvFilePath = input('Please ender the full file path of the CSV file you wish to use:  ')
    csvFilePath = os.path.expanduser(csvFilePath)
    if( not os.path.isfile(csvFilePath) ):
        print('No Input CSV file found on your device at: ' + csvFilePath)
        print('Please check the file path you entered above and try again.\n')
        csvFilePath = ''
    else:
        validationSuccess = 1
print('Input CSV file found at: ', csvFilePath, '\n')
timeStamp = datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S")
errorFilePath = os.path.join(os.path.dirname(csvFilePath),f"Errors_{timeStamp}.csv")
validationSuccess = 0

### Validate Access Token ###
while (validationSuccess == 0):
    if not accessToken :
        accessToken = input('Please enter your access token:  ')
    # Get People API Call to validate access token.
    validationResponse = requests.get(getMyDetailsURL,
                headers={'Authorization': 'Bearer ' + accessToken})
    if validationResponse.status_code == 401:
        # This means the access token was invalid.
        print('Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
        accessToken = ''
    else:
        name = validationResponse.json()['firstName']
        validationSuccess = 1
print(f"Congrats {name}, your input file and Access Token have validated succesfully.\n")


### Read in CSV ###
# This script assumes that the extensions being added
# already exist within Webex Control Hub either on a 
#  - user extension
#  - virtual extension
#  - workspace extension 
#
# Required Headers: email, number01, number02, number03, number04, number05
#
#
data = pd.read_csv(csvFilePath)
records = data.to_dict(orient='records')
totalRecords = len(records)

with open(errorFilePath, 'w') as csvFile:
    csvFile.write('User Email, API Call Response Code, Response Message\n')

while (loopCount < totalRecords):
    # Get People API Call to get UserId
    listPeopleAPI = F"https://webexapis.com/v1/people?email={urllib.parse.quote_plus(records[loopCount]['email'])}"
    response = requests.get(listPeopleAPI, headers={'Authorization': 'Bearer ' + accessToken})

    while response.status_code == 429:
        time.sleep(30)
        response = requests.get(listPeopleAPI, headers={'Authorization': 'Bearer ' + accessToken})

    if response.status_code != 200 or len(response.json()['items']) == 0:
        # Error Handling
        if response.status_code != 200:
            print('    Error: Get User Id API Call Error', str(response.status_code), 'on user', str(records[loopCount]['email']))
            errorMessage = response.json()['message']
        else:
            print('    Error: User not found for email', str(records[loopCount]['email']))
            errorMessage = 'No user found with that email'
        with open(errorFilePath, 'a') as csvErrFile:
            csvErrFile.write(str(records[loopCount]) + ',' + str(response.status_code) + ',' + errorMessage + '\n')
        errorCount += 1
    else:
        ## Get Application Id
        ## TODO Handle updates to phone devices
        for user in response.json()['items']:
            userId = user['id']
            appIdUrl = f"https://webexapis.com/v1/people/{userId}/features/applications"
            appIdResponse = requests.get(appIdUrl, headers={'Authorization': 'Bearer ' + accessToken})

            while appIdResponse.status_code == 429:
                time.sleep(30)
                appIdResponse = requests.get(appIdUrl, headers={'Authorization': 'Bearer ' + accessToken})

            if appIdResponse.status_code != 200 or len(appIdResponse.json()) == 0:
                # Error Handling
                if appIdResponse.status_code != 200:
                    print('    Error: Get desktopClientId API Call Error', str(appIdResponse.status_code), 'on user', str(records[loopCount]['email']))
                    errorMessage = appIdResponse.json()['message']
                else:
                    print('    Error: Application Services not found for email', str(records[loopCount]['email']))
                    errorMessage = 'Application Services not found for email'
                with open(errorFilePath, 'a') as csvErrFile:
                    csvErrFile.write(str(records[loopCount]['email']) + ',' + str(appIdResponse.status_code) + ',' + errorMessage + '\n')
                errorCount += 1
            else:
                desktopClientId = appIdResponse.json()['desktopClientId']

                # TODO handle up to 5 defined extensions
                # Create array of numbers
                
                ## Get Id for device to be shared
                lineIdUrl = f"https://webexapis.com/v1/telephony/config/numbers?phoneNumber={records[loopCount]['number']}"
                print(lineIdUrl)
                lineIdResponse = requests.get(lineIdUrl, headers={'Authorization': 'Bearer ' + accessToken})

                if lineIdResponse.status_code != 200 or len(lineIdResponse.json()['phoneNumbers']) == 0:
                    # Error Handling
                    if lineIdResponse.status_code != 200:
                        print('    Error: Get lineId API Call Error', str(lineIdResponse.status_code), 'on user', str(records[loopCount]['email']))
                        errorMessage = lineIdResponse.json()['message']
                    else:
                        print(f"    Error: Phone Number/Extension {records[loopCount]['number']} not found', {str(records[loopCount]['email'])}")
                        errorMessage = f"Phone Number/Extension {records[loopCount]['number']} not found"
                    with open(errorFilePath, 'a') as csvErrFile:
                        csvErrFile.write(str(records[loopCount]['email']) + ',' + str(lineIdResponse.status_code) + ',' + errorMessage + '\n')
                    errorCount += 1
                else:
                    # Set Line Id
                    lineId = lineIdResponse.json()['phoneNumbers'][0]['owner']['id']
                    
                    tempMember = {
                        "members": []
                    }
                    sharedLineUrl = f"https://webexapis.com/v1/telephony/config/people/{userId}/applications/{desktopClientId}/members"
                    memberResponse = requests.get(sharedLineUrl, headers={'Authorization': 'Bearer ' + accessToken})

                    ## TODO Add Error Handling
                    i = 0
                    membersList = memberResponse.json()['members']
                    # print(membersList['members'])
                    for member in membersList:
                        temp = {
                            "id": member['id'],
                            "primaryOwner": member['primaryOwner'],
                            "port": member['port'],
                            "lineType": member['lineType'],
                            "lineWeight": 1,
                            "hotlineEnabled": member['hotlineEnabled'],
                            "allowCallDeclineEnabled": member['allowCallDeclineEnabled']
                        }
                        tempMember['members'].append(temp)
                        i += 1
                    # Add the new extension to the member list
                    temp = {
                            "id": lineId,
                            "primaryOwner": False,
                            "port": i+1,
                            "lineType": "SHARED_CALL_APPEARANCE",
                            "lineWeight": 1,
                            "hotlineEnabled": False,
                            "allowCallDeclineEnabled": True
                        }
                    tempMember['members'].append(temp)

                    payload = json.dumps(tempMember)
                    updateSharedResponse = requests.put(sharedLineUrl, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken}, data=payload)
                    
                    # TODO Error Handling
                    print(updateSharedResponse.status_code)
                    # Test Printing Data
                    # print(json.dumps(tempMember, indent=2))

                    
                
    loopCount += 1