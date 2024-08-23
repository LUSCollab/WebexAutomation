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
csvFilePath = 'Test.csv'
accessToken = 'MjJjNWU2ZDYtMWFmMi00ZTNjLWFmZWItZGViZGQyMDI0OWQ0ODVmMmNlZmMtZjJi_P0A1_e3266292-7ee3-4149-ae94-80a7ae54f891'
orgId = ''
records = []
loopCount = 0
errorCount = 0
userId = ''
desktopClientId = ''
lineId = ''
deviceIds = []
getMyDetailsUrl = 'https://webexapis.com/v1/people/me'
orgUrl = 'https://webexapis.com/v1/organizations'

### User Input ###
print('You will need the following:')
print('  1. The full file path for the input CSV file\n       (ex: C:\\Path\\To\\File.csv on Windows or ~/Scripts/exported_file.csv on Mac)')
print('  2. Webex API access token\n       (You can get this at https://developer.webex.com)\n')
# print('  3. The OrgId of the target Webex tenant if using a partner account\n')

### Validate Access to CSV File ###
validationSuccess = 0
while (validationSuccess == 0):
    if not csvFilePath:
        csvFilePath = input('Please ender the full file path of the CSV file you wish to use:  ')
    csvFilePath = os.path.expanduser(csvFilePath)
    if( not os.path.isfile(csvFilePath) ):
        print('❌ No Input CSV file found on your device at: ' + csvFilePath)
        print('Please check the file path you entered above and try again.\n')
        csvFilePath = ''
    else:
        validationSuccess = 1
        
print('✅ Input CSV file found at: ', csvFilePath, '\n')
timeStamp = datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S")
errorFilePath = os.path.join(os.path.dirname(csvFilePath),f"Log_{timeStamp}.csv")
validationSuccess = 0

### Validate Access Token ###
while (validationSuccess == 0):
    if not accessToken :
        accessToken = input('Please enter your access token:  ')
    # Get People API Call to validate access token.
    validationResponse = requests.get(getMyDetailsUrl,
                headers={'Authorization': 'Bearer ' + accessToken})
    if validationResponse.status_code == 401:
        # This means the access token was invalid.
        print('❌ Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
        accessToken = ''
    else:
        name = validationResponse.json()['firstName']
        validationSuccess = 1

name = validationResponse.json()['firstName']
print('✅ Access token has been validated.\n')
validationSuccess = 0

### Check if using a partner account ###
# while (validationSuccess == 0):
#     orgResponse = requests.get(orgUrl, headers={'Authorization': 'Bearer ' + accessToken})
#     organizations = orgResponse.json()['items']

#     if len(orgResponse.json()['items']) > 1:
#         orgEntry = input('Looks like you are using a partner account, please enter the target OrgId:  ')
#         for org in organizations:
#             if org['id'] == orgEntry:
#                 found = True
            
#         if found:
#             orgId = orgEntry
#             validationSuccess = 1
#         else:
#             print('Unable to validate OrgId. \n')

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
            
            ### Get Device Id(s) for update associated devices
            devIdUrl = f"https://webexapis.com/v1/devices?personId={userId}"
            devIdResponse = requests.get(devIdUrl, headers={'Authorization': 'Bearer ' + accessToken})

            while devIdResponse.status_code == 429:
                time.sleep(30)
                devIdResponse = requests.get(devIdUrl, headers={'Authorization': 'Bearer ' + accessToken})

            if devIdResponse.status_code != 200 or len(devIdResponse.json()['items']) == 0:
                if devIdResponse.status_code != 200:
                    print('    Error: Get deviceId API Call Error', str(devIdResponse.status_code), 'on user', str(records[loopCount]['email']))
                    errorMessage = devIdResponse.json()['message']
                else:
                    print(f"    No devices associated for user {records[loopCount]['email']}")
            else:
                for device in devIdResponse.json()['items']:
                    deviceIds.append({"id": device['id']})
            
            ### Get Appliation ID for updating the Webex App devices
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
                lineIdUrl = f"https://webexapis.com/v1/telephony/config/numbers?extension={records[loopCount]['number']}"
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
                    
                    ### Handle any devices assigned to the user ###
                    if len(deviceIds) > 0:
                        for device in deviceIds:
                            devSharedLineUrl = f"https://webexapis.com/v1/telephony/config/devices/{device['id']}/members"
                            devMemberResponse = requests.get(devSharedLineUrl, headers={'Authorization': 'Bearer ' + accessToken})
                            devMembers = devMemberResponse.json()['members']
                            memberList = {
                                "members": []
                            }

                            j = 0
                            for devMember in devMembers:
                                temp = {
                                    "id": devMember['id'],
                                    "primaryOwner": devMember['primaryOwner'],
                                    "port": devMember['port'],
                                    "lineType": devMember['lineType'],
                                    "lineWeight": 1,
                                    "hotlineEnabled": devMember['hotlineEnabled'],
                                    "allowCallDeclineEnabled": devMember['allowCallDeclineEnabled']
                                }
                                memberList['members'].append(temp)
                                j += 1
                            
                            newMember = {
                                "id": lineId,
                                "primaryOwner": False,
                                "port": j+1,
                                "lineType": "SHARED_CALL_APPEARANCE",
                                "lineWeight": 1,
                                "hotlineEnabled": False,
                                "allowCallDeclineEnabled": True
                            }
                            memberList['members'].append(newMember)
                            devPayload = json.dumps(memberList)
                            updateDevharedResponse = requests.put(devSharedLineUrl, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken}, data=devPayload)

                            if updateDevharedResponse.status_code != 204:
                            # Error Handling
                                if updateDevharedResponse.status_code != 204:
                                    print('    Error: Adding Shared Line to Device Error', str(updateDevharedResponse.status_code), 'on user', str(records[loopCount]['email']))
                                    errorMessage = updateDevharedResponse.json()['message']
                                else:
                                    print(f"    Error: There was a problem adding {records[loopCount]['number']}, {str(records[loopCount]['email'])}")
                                    errorMessage = f"Error adding {records[loopCount]['number']} to {records[loopCount]['email']}"
                                with open(errorFilePath, 'a') as csvErrFile:
                                    csvErrFile.write(str(records[loopCount]['email']) + ',' + str(updateDevharedResponse.status_code) + ',' + errorMessage + '\n')
                                errorCount += 1
                            else:
                                print(f"Device: {records[loopCount]['number']} has been added to {records[loopCount]['email']}")
                    ### Reset Device Id List
                    deviceIds = []


                    tempMember = {
                        "members": []
                    }
                    appSharedLineUrl = f"https://webexapis.com/v1/telephony/config/people/{userId}/applications/{desktopClientId}/members"
                    appMemberResponse = requests.get(appSharedLineUrl, headers={'Authorization': 'Bearer ' + accessToken})

                    ## TODO Add Error Handling
                    i = 0
                    membersList = appMemberResponse.json()['members']
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
                    updateAppSharedResponse = requests.put(appSharedLineUrl, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken}, data=payload)
                    
                    if updateAppSharedResponse.status_code != 204:
                    # Error Handling
                        if updateAppSharedResponse.status_code != 204:
                            print('    Error: Adding Shared Line Error', str(updateAppSharedResponse.status_code), 'on user', str(records[loopCount]['email']))
                            errorMessage = updateAppSharedResponse.json()['message']
                        else:
                            print(f"    Error: There was a problem adding {records[loopCount]['number']}, {str(records[loopCount]['email'])}")
                            errorMessage = f"Error adding {records[loopCount]['number']} to {records[loopCount]['email']}"
                        with open(errorFilePath, 'a') as csvErrFile:
                            csvErrFile.write(str(records[loopCount]['email']) + ',' + str(updateAppSharedResponse.status_code) + ',' + errorMessage + '\n')
                        errorCount += 1
                    else:
                        print(f"WebexApp: {records[loopCount]['number']} has been added to {records[loopCount]['email']}")
    
    ### Move on to next record
    loopCount += 1