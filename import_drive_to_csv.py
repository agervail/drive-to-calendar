# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Google+ Domains API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
from dateutil import parser
import datetime
import pandas as pd

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

def download_file(service, drive_file):
  """Download a file's content.

  Args:
    service: Drive API service instance.
    drive_file: Drive File instance.

  Returns:
    File's content if successful, None otherwise.
  """
  download_url = drive_file.get('downloadUrl')
  if download_url:
    resp, content = service._http.request(download_url)
    if resp.status == 200:
      #print 'Status: %s' % resp
      return content
    else:
      print 'An error occurred: %s' % resp
      return None
  else:
    # The file doesn't have any content stored on Drive.
    return None

# Parser for command-line arguments.
pars = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/drive',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

def main(argv):
  # Parse the command-line flags.
  flags = pars.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Google+ Domains API.
  #service = discovery.build('plusDomains', 'v1', http=http)

  drive_service = discovery.build('drive', 'v2', http=http)

  try:
    print "Success!"
    #import ipdb; ipdb.set_trace()
    training_dir = '0B1uVehMk_uX7VEUtSkI3ZnRyMXc'
    files = drive_service.files().list(q="'0B1uVehMk_uX7VEUtSkI3ZnRyMXc' in parents").execute()
    content = {}
    #import ipdb;ipdb.set_trace()
    for i in files['items']:
      if 'text/plain' in i['mimeType'] and not i['labels']['trashed']:
        #download the file
        f_id = i['id']
        fichier = drive_service.files().get(fileId=f_id).execute()
        dt = parser.parse(fichier['createdDate'])
        print dt
        content[dt] = download_file(drive_service, fichier)
        #move the file to old directory
        new_dir = {'id': '0B1uVehMk_uX7QndaR2poTFZ3OFE'}
        drive_service.parents().insert(fileId=f_id, body=new_dir).execute()
        drive_service.parents().delete(fileId=f_id, parentId=training_dir).execute()
    
    if len(content) > 0:
      act = {}
      for d in content.keys():
        dd = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute)
        c = content[d]
        ret = c.find('\n')
        if ret != -1 :
          c = c[:c.find('\n')]
        h = c.split()[-1].split('.')[0].split(':')
        if len(h) == 2:
          t = datetime.time(minute=int(h[0]), second=int(h[1]))
        elif len(h) == 3:
          t = datetime.time(hour=int(h[0]), minute=int(h[1]), second=int(h[2]))
        else:
          import ipdb; ipdb.set_trace()
          print 'ERROR' + str(h)
          
        act[dd] = t
      print act
      
      
      
      minutes = {}
      for k in act.keys():
        minutes[k] = act[k].hour * 60 + act[k].minute

      df = pd.DataFrame(minutes.values(),index=minutes.keys(), columns=['duree'])
      df = df.sort_index()
      #df.plot()
      df.to_csv('df_seances.csv', header=True)

    sdf = open('df_seances.csv', 'r')
    if os.path.isfile('seances.csv'):
      sf = open('seances.csv', 'a')
      sdf.readline()
    else:
      sf = open('seances.csv', 'w')
    
    for l in sdf.readlines():
      sf.write(l)
    
    #import ipdb; ipdb.set_trace()
  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
