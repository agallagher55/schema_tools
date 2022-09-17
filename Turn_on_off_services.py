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
        "base_url": "https://gisappa-int.halifax.ca:6443/arcgis",  # PROD use this.  This needs to be run on DC1-GIS-APP-P22 or DCQ-GIS-APP-P23
    },
}


def openURL(url, params=None, protocol=None, base_url=None):
    try:
        print("Opening URL...")

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

    print("\tToken URL: " + tokenURL)
    print("\tParams: {}".format(params))
    print("\tResponse: {}".format(resp))

    if "token" in resp:
        return resp.get('token')

    else:
        # TODO: Create custom error 'Token Error'
        raise Exception("Can't get token: {}".format(resp))


def startStopService(service, start_or_stop, token, base_url):
    print("\n{}ING Service...".format(start_or_stop.upper()))

    params = {"token": token}

    service_name = urllib2.urlparse.urlparse(service).path.split("/")[-1]
    resp = openURL(url="{}/{}".format(service, start_or_stop), params=params, base_url=base_url)

    if resp.get("status") == 'success':
        print("\tSuccessfully {}ED {}".format(start_or_stop, service_name))

    else:
        print("\tUnable to {} {}.".format(start_or_stop, service_name))
        print("\t*'{}'".format(', '.join(resp.get("messages"))))


if __name__ == "__main__":
    ENVIRONMENT = "DEV"  # QA, PROD
    SERVICE_UPDATE = "START"

    base_url = SERVICE_CONFIG.get(ENVIRONMENT).get("base_url")
    services_url = "{}/admin/services/".format(base_url)

    pw = SERVICE_CONFIG.get(ENVIRONMENT).get("password")

    token = createToken(base_url, USERNAME, pw)

    services = [
        services_url + "DDE/dde_map.MapServer",
        # services_url + "HRM/ReGIS_EMO.MapServer",
        # servicesURL + "HRMRegistry/HRMBaseData.MapServer",
        # servicesURL + "CityWorks/Cityworks_Assets.MapServer",
        # servicesURL + "CityWorks/Cityworks_Map.MapServer",
    ]

    try:
        for service in services:
            print "\nProcessing service: '{}'...".format(service)
            startStopService(service, SERVICE_UPDATE, token, base_url)

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
