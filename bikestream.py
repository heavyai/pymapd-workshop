import sys
import string
import os
import time
import datetime
import pandas as pd
import numpy as np
import requests
from multiprocessing import Pool

# simple function to be p.map[ped]
def get_url(url):

    r = None
    try:
        r = (requests.get(url, timeout=2).json(), url)
    except:
        pass

    return r

def feedlist(df, feedtype):
    return df[df["feedtype"] == feedtype].feedurl

def main():
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    #round to minute, set the same for all records
    #this is so that each load represents same time period
    start_time = int(datetime.datetime.now().replace(second=0, microsecond=0).timestamp())
    str_start_time = '%s' % (datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
    
    # read in endpoints
    endpoints_df = pd.read_csv("./gbfs_endpoints.csv")
    
    # no reason for 4 specifically, just "some" parallelism
    p = Pool(4)
    
    #### free_bike_status
    bike_status = p.map(get_url, feedlist(endpoints_df, "free_bike_status"))
    
    #make df, make url column to know where data came from, append to list
    bike_status_df_list = []
    for x in bike_status:
        if x is not None:
            df = pd.DataFrame(x[0]["data"]["bikes"])
            df["baseurl"] = x[1].replace("/free_bike_status.json", "")
            bike_status_df_list.append(df)
    
    #make single table with specified columns so no surprise columns happen
    bike_status_df = pd.concat(bike_status_df_list, axis=0, sort=False)[['baseurl',
                                                                         'bike_id',
                                                                         'is_disabled',
                                                                         'is_reserved',
                                                                         'lat',
                                                                         'lon',
                                                                         'jump_ebike_battery_level',
                                                                         'name',
                                                                         'jump_vehicle_type',
                                                                         'vehicle_type'
                                                                        ]]
    #this will be the filter key in immerse, and match key if needed
    bike_status_df['accessed_on'] = str_start_time
    bike_status_df.to_csv("/tmp/kinesis/bike-status.csv", header=False, index=False)
    
main()
