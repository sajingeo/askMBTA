from __future__ import print_function
import requests
import time
import datetime
import pytz
import dateutil.parser


def main():
    print(seach_mbta("12759", "CT2"))


def seach_mbta(stop_id, route_id_str):
    try:
        route_id = int(route_id_str)
    except:
        if (route_id_str == "CT2"):
            route_id = 747

    API_KEY = "xxxxxxxxxxxxxxxxxxxxxx"
    payload = {'api_key': API_KEY, 'route': route_id, 'stop' : stop_id, 'format': 'json'}
    url_p_route = "https://api-v3.mbta.com/predictions"
    print(payload)
    r = requests.get(url_p_route, params=payload)
    res = r.json()  ## josonfy the string
    # print (res) ## this is for logging and should not released!!
    # function returns -1 if there is an error
    foundStop = False
    stop_id = str(stop_id)

    print(res)
    # try:
    timeNow = datetime.datetime.now(pytz.utc)
    for predicton in res["data"]:
        attributes = predicton['attributes']
        departure_time = attributes['departure_time']
        outTimeFound = dateutil.parser.parse(departure_time)
        break

    timeNow = datetime.datetime.now(pytz.utc)

    if (outTimeFound >= timeNow):
        time_diff = outTimeFound - timeNow
        minutesForNextBus = (time_diff.seconds // 60) % 60
    else:
        print("time not found")
        return -1

    outString = "The next " + route_id_str + " bus will arrive at stop " + stop_id + " in " + str(
        minutesForNextBus) + " Minutes "
    print(outString)
    return outString
    # except:
    #     print ("some other error")
    #     return -1


if __name__ == "__main__":
    main()
