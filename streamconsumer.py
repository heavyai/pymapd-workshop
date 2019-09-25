import boto3
import json
from datetime import datetime
import time
import base64
import pandas as pd
import os
import sys
from pymapd import connect

# Connect to the OmniSci database
def connect_to_omnisci(str_user, str_password, str_host, str_dbname, isCloud):
  try:
    if (isCloud):
      connection = connect(user=str_user, password=str_password, host=str_host, dbname=str_dbname, port=443, protocol='https')
    else:
      connection = connect(user=str_user, password=str_password, host=str_host, dbname=str_dbname, port=6274)
  except Exception as ex:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print(message)
    if 'OmniSci Core not ready, try again' in message:
      print("Set connection to RETRY!")
      connection = "RETRY"
    else:
      connection = "ERROR"
  return connection


# Connect to OmniSci with 5 trys, this applies to OmniSci cloud instance which is paused during inactivity
for i in range(5):
  # connecting to a non-OmniSci Cloud instance
  # connection = connect_to_omnisci("mapd", "HyperInteractive", "localhost", "mapd", False)
  # connecting to an OmniSci Cloud instance
  connection = connect_to_omnisci("Access Key", "Secret Key", "use2-api.mapd.cloud", "mapd", True)
  if connection == "RETRY":
    # recommended time to sleep is 20 seconds before instance wakes up
    time.sleep(20)
    continue
  if connection == "ERROR":
    sys.exit(1)
  print(connection)
  break

query = 'CREATE TABLE IF NOT EXISTS bike_status (baseurl TEXT ENCODING DICT(32), bike_id TEXT ENCODING DICT(32), is_disabled BOOLEAN, is_reserved BOOLEAN, lat FLOAT, lon FLOAT, jump_ebike_battery_level TEXT ENCODING DICT(8), name TEXT ENCODING DICT(32), jump_vehicle_type TEXT ENCODING DICT(8), vehicle_type TEXT ENCODING DICT(8), accessed_on TIMESTAMP)'
connection.execute(query)
print(connection.get_table_details('bike_status'))

my_stream_name = 'bike-status'
kinesis_client = boto3.client('kinesis', region_name='us-east-1')
response = kinesis_client.describe_stream(StreamName=my_stream_name)
my_shard_id = response['StreamDescription']['Shards'][0]['ShardId']
shard_iterator = kinesis_client.get_shard_iterator(StreamName=my_stream_name,
                                                      ShardId=my_shard_id,
                                                      ShardIteratorType='LATEST')
my_shard_iterator = shard_iterator['ShardIterator']


totalrows = 0
fullList = []
while 1==1:
    record_response = kinesis_client.get_records(ShardIterator=my_shard_iterator, Limit=1000)
    if (len(record_response['Records']) <= 0):
      my_shard_iterator = record_response['NextShardIterator']
      time.sleep(10.0/1000.0)
      continue
    for res in record_response["Records"]:
      record_data = res["Data"].decode("utf-8")
      record_data = record_data.rstrip('\n')
      list = record_data.split(',')
      if (len(list) != 11):
        print('Warning: length of list %d not accepted' % (len(list)))
        continue
      fullList.append(list)
    df = pd.DataFrame(fullList, columns=['baseurl', 'bike_id', 'is_disabled', 'is_reserved', 'lat', 'lon', 'jump_ebike_battery_level', 'name', 'jump_vehicle_type', 'vehicle_type', 'accessed_on'])
    df['accessed_on'] = pd.to_datetime(df['accessed_on'], format='%Y-%m-%d %H:%M:%S')
    df['lat'] = pd.to_numeric(df['lat'], downcast='float')
    df['lon'] = pd.to_numeric(df['lon'], downcast='float')
    df['is_disabled'] = df['is_disabled'].astype('bool')
    df['is_reserved'] = df['is_reserved'].astype('bool')
    print(df.head())
    totalrows += df.shape[0]
    print('load omnisci table, rows loaded = %d' % (totalrows))
    connection.load_table('bike_status', df, preserve_index=False)
    fullList.clear()
    del df
    #
    my_shard_iterator = record_response['NextShardIterator']
    if my_shard_iterator is None:
      print('producer closed, exit!')
      break
    # small wait
    time.sleep(10.0/1000.0)

connection.close()
