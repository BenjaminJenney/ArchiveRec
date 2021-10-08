from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import email
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
#user_id = 'me'
#search_string = 'subject:this is a test'

def get_message(service, user_id, msg_id):
    try:
        message= service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        
        print("raw messsage:", message['raw'])
        
        msg_byte = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        print("byte message:", msg_byte)

        msg_str = email.message_from_bytes(msg_byte)

        content_types = msg_str.get_content_maintype()

        if content_types == 'multipart':
            plain_text, html_text = msg_str.get_payload()
            print('this is the message body: ')
            print(plain_text.get_payload())
            return plain_text.get_payload()
        else:
            return msg_str.get_payload()
    except(errors.HttpError, error):
        print("An error occured: %s") % error

def search_messages(service, user_id, search_string):
    try:
        #this is the basically the object access pattern for google api, need service object, users() for user inbox, messages from user inbox, do stuff: list, get, etc. 
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()
        
        number_results = search_id['resultSizeEstimate']
        if number_results > 0:
            message_ids = search_id['messages']
            final_list = []
            for ids in message_ids:
                final_list.append(ids['id'])
                print(final_list)
            return final_list
        else:
            print('There were 0 results for that search string, returning an empty string')
            return ""

    except (errors.HttpError, error):
        print("An error occured: %s") % error


def get_service():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

service = get_service()
message_ids = search_messages(service, 'me', 'Receipt')
get_message(service, 'me', message_ids[1])
