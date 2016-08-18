from __future__ import print_function

import argparse
import base64
from email.mime.text import MIMEText
import sys
import httplib2
import os
import logging

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

log = logging.getLogger('gmailbot')

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def main(argv=sys.argv):
  """Shows basic usage of the Gmail API.

  Creates a Gmail API service object and outputs a list of label names
  of the user's Gmail account.
  """
  logging.basicConfig()
  log.setLevel(logging.INFO)

  parser = argparse.ArgumentParser(parents=[tools.argparser])
  parser.add_argument('account')
  subparsers = parser.add_subparsers(dest='command')

  print_labels_subparser = subparsers.add_parser('print-labels')

  feedback_pings_subparser = subparsers.add_parser('feedback-pings')
  feedback_pings_subparser.add_argument('users', help='Comma separated list of users')

  flags = parser.parse_args()
  service = create_service(flags.account, flags)

  if flags.command == 'print-labels':
    print_labels(service)
  elif flags.command == 'feedback-pings':
    feedback_pings(flags, service)


def feedback_pings(flags, service):
  pingees = set(user + '@infer.com' for user in flags.users.split(','))
  seen_pingees = set()
  messageIds = service.users().messages().list(userId='me', q='to:product-feedback@infer.com newer_than:7d').execute()
  log.info('got %s messages', len(messageIds['messages']))
  for messageId in messageIds['messages']:
    message = service.users().messages().get(userId='me', id=messageId['id']).execute()
    headers = {header['name']: header['value'] for header in message['payload']['headers']}
    for pingee in pingees - seen_pingees:
      if pingee in headers['From']:
        seen_pingees.add(pingee)
        break
  log.info('pinging the following people: %s', ', '.join(sorted(pingees - seen_pingees)))
  for pingee in pingees - seen_pingees:
    message = create_message(
        'product-feedback@infer.com', pingee, 'Product feedback!',
        'Just a friendly reminder to share any customer learnings/feedback from the past week, if you have any (no need to reply if none).  Thanks!')
    send_message(service, 'me', message)


def print_labels(service):
  results = service.users().labels().list(userId='me').execute()
  labels = results.get('labels', [])
  if not labels:
    print('No labels found.')
  else:
    print('Labels:')
    for label in labels:
      print(label['name'])


def create_service(account, flags=None):
  credentials = get_credentials(account, flags)
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('gmail', 'v1', http=http)
  return service

def get_credentials(account, flags=None):
  """Gets valid user credentials from storage.

  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.

  Returns:
      Credentials, the obtained credential.
  """
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.gmailbot')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir, '%s.json' % account)

  store = oauth2client.file.Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatibility with Python 2.6
      credentials = tools.run(flow, store)
    print('Storing credentials to ' + credential_path)
  return credentials

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  return service.users().messages().send(userId=user_id, body=message).execute()

if __name__ == '__main__':
  main()
