import sys
import traceback
import json
import urllib2
import urllib
import ConfigParser
import datetime
import os
import shutil
import arcpy
import httplib

USERNAME = "siteadmin"

SERVICE_CONFIG = {
    "DEV": {
        "password": "panas0n1c",
        "base_url": "https://gisapp-int-dev.halifax.ca:6443/arcgis",
    },
    "QA": {
        "password": "t0m@t0e",
        "base_url": "https://gisappa-int-qa.halifax.ca:6443/arcgis",
    },
    "PROD": {
        "password": "e33pl@nt",
        "base_url": "https://gisappa-int.halifax.ca:6443/arcgis",
    },
}


def openURL(url, params=None, protocol=None, base_url=None):
    try:
        print("\nOpening URL...")

        if params:
            params.update(dict(f="json"))

        else:
            params = dict(f="json")

        if protocol:
            encoded_params = str.encode(urllib.urlencode(params))
            encoded_params = encoded_params.decode("utf-8")

            url = "{0}?{1}".format(url, encoded_params)

            request = urllib2.Request(url)
            request.add_header('referer', base_url)

            response = urllib2.urlopen(request)

        else:
            encoded_params = str.encode(urllib.urlencode(params))
            request = urllib2.Request(url)
            request.add_header('referer', base_url)
            response = urllib2.urlopen(request, encoded_params)

        decodedResponse = response.read().decode('utf-8')
        jsonResponse = json.loads(decodedResponse)

        return jsonResponse

    except urllib2.HTTPError as e:
        return e

    except urllib2.URLError as e:
        return e

    except Exception as e:
        print(e)
        logger.error(e)


def createToken(base_url, username, password):
    print("\nCreating token...")

    tokenURL = "{}/tokens/generateToken".format(base_url)
    params = {
        "username": username,
        "password": password,
        "client": 'referer',
        "referer": base_url
    }

    resp = openURL(url=tokenURL, params=params, base_url=base_url)

    print("Token URL: " + tokenURL)
    print("Params: {}".format(json.dumps(params, indent=4)))
    print("Response: {}".format(json.dumps(resp, indent=4)))

    if "token" in resp:
        return resp.get('token')

    else:
        raise Exception("Can't get token: {}".format(resp))


def startStopService(service, start_or_stop, token, base_url):
    print("\n{}ING Service...".format(start_or_stop.upper()))

    params = {"token": token}

    service_name = urllib2.urlparse.urlparse(service).path.split("/")[-1]
    resp = openURL(url="{}/{}".format(service, start_or_stop), params=params, base_url=base_url)

    if resp.get("status") == 'success':
        print("\tSuccessfully {}ED {}".format(start_or_stop, service_name))

    else:
        print("\tERROR: Unable to {} {}.".format(start_or_stop, service_name))
        print("\t*'{}'".format(', '.join(resp.get("messages"))))


if __name__ == "__main__":
    # PROD needs to be run on DC1-GIS-APP-P22 or DCQ-GIS-APP-P23

    services = [
        "HRMRegistry/ParkingServices.MapServer",
        # "HRMRegistry/HRMBaseData.MapServer",
        # "CityWorks/Cityworks_Assets.MapServer",
        # "CityWorks/Cityworks_Map.MapServer",

        # "HRM/ReGIS_EMO.MapServer",
        # "DDE/dde_map.MapServer",
    ]

    for env in [
        "DEV", 
        "QA", 
        "PROD"
    ]:

        base_url = SERVICE_CONFIG.get(env).get("base_url")
        pw = SERVICE_CONFIG.get(env).get("password")

        services_url = "{}/admin/services/".format(base_url)
        
        token = createToken(base_url, USERNAME, pw)

        for update in "STOP", "START":
            print("\nUpdating {} server services...".format(env))

            try:
                for service in services:
                    full_service_url = services_url + service

                    print("\nService: '{}'...".format(full_service_url))
                    startStopService(full_service_url, update, token, base_url)

            except:
                tb = sys.exc_info()[2]
                tbinfo = traceback.format_tb(tb)[0]
                pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                        str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
