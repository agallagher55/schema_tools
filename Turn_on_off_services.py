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

# TODO: Update so you can use keyword (dev, qa, prod) to start/stop service

# server_name = "gisapp-int-dev.halifax.ca" #DEV

# server_name = "gisappa-int-qa.halifax.ca" #QA Use this
server_name = "gisappa-int.halifax.ca"  # PROD use this.  This needs to be run on DC1-GIS-APP-P22 or DCQ-GIS-APP-P23

baseURL = "https://" + server_name + ":6443/arcgis"
servicesURL = baseURL + "/admin/services/"

username = "siteadmin"
# password = "panas0n1c" #DEV
# password = "t0m@t0e"  # QA
password = "e33pl@nt"  # PROD

services = [
    servicesURL + "DDE/dde_map.MapServer",
    servicesURL + "HRMRegistry/HRMBaseData.MapServer",
    servicesURL + "CityWorks/Cityworks_Assets.MapServer",
    servicesURL + "CityWorks/Cityworks_Map.MapServer",
]

print servicesURL


def openURL(url, params=None, protocol=None):
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
            request.add_header('referer', baseURL)
            response = urllib2.urlopen(request)

        else:
            encoded_params = str.encode(urllib.urlencode(params))
            request = urllib2.Request(url)
            request.add_header('referer', baseURL)
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


def createToken(baseURL, username, password):
    print("\nCreating token...")
    tokenURL = "{}/tokens/generateToken".format(baseURL)
    params = {"username": username,
              "password": password,
              "client": 'referer',
              "referer": baseURL}

    resp = openURL(tokenURL, params)

    print(tokenURL)
    print(params)
    print(resp)

    if "token" in resp:
        return resp['token']

    else:
        raise Exception("Can't get token: {}".format(resp))

    return token


def startStopService(service, start_or_stop):
    print("{}ING Service...".format(start_or_stop.upper()))

    serviceName = urllib2.urlparse.urlparse(service).path.split("/")[-1]
    resp = openURL("{}/{}".format(service, start_or_stop), params)

    if "status" in resp and resp['status'] == 'success':
        print("Successfully {}ED {}".format(start_or_stop, serviceName))

    else:
        print("Unable to {} {}.\n {}".format(start_or_stop, serviceName, resp))


if __name__ == "__main__":

    token = createToken(baseURL, username, password)
    params = {"token": token}

    ##    try:
    ##        for s in services:
    ##            print s
    ##            startStopService(s, "STOP")
    ##            time.sleep(60) # make sure all locks are gone
    ##    except:
    ##        tb = sys.exc_info()[2]
    ##        tbinfo = traceback.format_tb(tb)[0]
    ##        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
    ##                str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
    ##        for s in services:
    ##            print s
    ##            startStopService(s, "START")
    ##        exit()

    try:
        for service in services:
            print service
            startStopService(service, "START")
            # startStopService(service, "STOP")

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
