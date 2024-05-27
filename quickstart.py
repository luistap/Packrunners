# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START drive_quickstart]
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive"]

# Load the configuration
with open('config.json') as config_file:
  config = json.load(config_file)
  main_folder_id = config['MAIN_FOLDER_ID']


# extract the log files for all elements in the team folder
def get_log_files(service, team_number):

  folder_id = get_team_folder(team_number, service)
  

# retrieve a team's folder id
def get_team_folder(team_number, service):

      try:
        team_folder_name = f"TEAM {team_number}"  # Construct folder name dynamically based on team number
        # Construct the query to search for the folder by name within the main folder
        query = f"parents = '{main_folder_id}' and mimeType = 'application/vnd.google-apps.folder' and name = '{team_folder_name}'"
        
        # Perform the search
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        folders = response.get('files', [])
        
        if folders:
            # Assuming the first match is the correct one
            return folders[0]['id']
        else:
            print(f"No folder found with the name: {team_folder_name}")
            return None
      except HttpError as error:
        print(f"An error occurred: {error}")
        return None


# verify credentials
def auth_credentials():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)
    return service
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  auth_credentials()
# [END drive_quickstart]
