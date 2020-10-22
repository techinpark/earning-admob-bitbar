#!/usr/bin/env LC_ALL=en_US.UTF-8 /usr/local/bin/python3

# <bitbar.title>Admob</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Fernando</bitbar.author>
# <bitbar.author.github>Fernando</bitbar.author.github>
# <bitbar.image></bitbar.image>
# <bitbar.desc>admob earning</bitbar.desc>
# <bitbar.dependencies>python3</bitbar.dependencies>
# <bitbar.abouturl>localhost</bitbar.abouturl>

import os
import pickle

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

API_NAME = 'admob'
API_VERSION = 'v1'
API_SCOPE = 'https://www.googleapis.com/auth/admob.report'

# Store refresh tokens in a local disk file. This file contains sensitive
# authorization information.
TOKEN_FILE = '/Users/fernando/Documents/05.bitbar/admob/token.pickle'

def load_user_credentials():
  # Name of a file containing the OAuth 2.0 information for this
  # application, including client_id and client_secret, which are found
  # on the Credentials tab on the Google Developers Console.
  print(os.path.dirname(__file__))
  client_secrets = os.path.join(
      os.path.dirname(__file__), '/admob/client_secrets.json')
      
  return client_secrets


# Authenticate user and create AdMob Service Object.
def authenticate():
  """Authenticates a user and creates an AdMob Service Object.

  Returns:
    An AdMob Service Object that is authenticated with the user using either
    a client_secrets file or previously stored access and refresh tokens.
  """

  # The TOKEN_FILE stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
      credentials = pickle.load(token)

    if credentials and credentials.expired and credentials.refresh_token:
      credentials.refresh(Request())

  # If there are no valid stored credentials, authenticate using the
  # client_secrets file.
  else:
    client_secrets = load_user_credentials()
    flow = Flow.from_client_secrets_file(
        client_secrets,
        scopes=[API_SCOPE],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    # Redirect the user to auth_url on your platform.
    auth_url, _ = flow.authorization_url()
    print('Please go to this URL: {}\n'.format(auth_url))

    # The user will get an authorization code. This code is used to get the
    # access token.
    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)
    credentials = flow.credentials

  # Save the credentials for the next run.
  with open(TOKEN_FILE, 'wb') as token:
    pickle.dump(credentials, token)

  # Build the AdMob service.
  admob = build(API_NAME, API_VERSION, credentials=credentials)
  return admob


# Set the 'PUBLISHER_ID' which follows the format "pub-XXXXXXXXXXXXXXXX".
# See https://support.google.com/admob/answer/2784578
# for instructions on how to find your publisher ID.
PUBLISHER_ID = 'pub-XXXXXXXXXXXXXXXX'


def generate_network_report(service, publisher_id):
  """Generates and prints a network report.

  Args:
    service: An AdMob Service Object.
    publisher_id: An ID that identifies the publisher.
  """

  # Set date range. AdMob API only supports the account default timezone and
  # "America/Los_Angeles", see
  # https://developers.google.com/admob/api/v1/reference/rest/v1/accounts.networkReport/generate
  # for more information.
  date_range = {
      'start_date': {'year': 2020, 'month': 9, 'day': 1},
      'end_date': {'year': 2020, 'month': 12, 'day': 31}
  }

  # Set dimensions.
  dimensions = ['MONTH', 'APP', 'PLATFORM']

  # Set metrics.
  metrics = ['ESTIMATED_EARNINGS']

  # Set sort conditions.
  #sort_conditions = {'dimension': 'DATE', 'order': 'DESCENDING'}

  # Set dimension filters.
  # dimension_filters = {
  #     'dimension': 'APP',
  #     'matches_any': {
  #         'values': ['ca-app-pub-2107785439138018~1137371846']
  #     }
  # }

  localizationSettings= {
    'currencyCode': 'USD',
    'languageCode': 'en-US'
  }

  # Create network report specifications.
  report_spec = {
      'date_range': date_range,
      'dimensions': dimensions,
      'metrics': metrics,
      'localizationSettings': localizationSettings
      #'sort_conditions': [sort_conditions],
      #'dimension_filters': [dimension_filters]
  }

  # Create network report request.
  request = {'report_spec': report_spec}

  # Execute network report request.
  result = service.accounts().networkReport().generate(
      parent='accounts/{}'.format(publisher_id), body=request).execute()

  # Display results.  
  agg = {}
  for record in result[1:-1]:
      if record["row"]["dimensionValues"]["MONTH"]["value"] not in agg.keys():
          agg[record["row"]["dimensionValues"]["MONTH"]["value"]] = 0
      agg[record["row"]["dimensionValues"]["MONTH"]["value"]] += int(record["row"]["metricValues"]["ESTIMATED_EARNINGS"]["microsValue"])/1000000

  value = agg['202010']
  print(f"💰 ${value:,.2f}")
  


def main():
  service = authenticate()
  generate_network_report(service, PUBLISHER_ID)


if __name__ == '__main__':
  main()
