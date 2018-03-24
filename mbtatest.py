from __future__ import print_function
import requests
import time
import datetime
import pytz
import dateutil.parser


def main():
    print(seach_mbta("70063", "Red line"))
    # print(seach_mbta("1419", "69"))


def seach_mbta(stop_id, route_id_str):
    is_train = False
    try:
        route_id = int(route_id_str)
    except:
        if (route_id_str == "CT2"):
            route_id = 747
        if (route_id_str.lower().find("red")==0):
            is_train = True
            route_id = "Red"
        if (route_id_str.find("blue")==0):
            is_train = True
            route_id = "Blue"
        if (route_id_str.find("orange")==0):
            is_train = True
            route_id = "Orange"

    API_KEY = "xxxxxx"
    payload = {'api_key': API_KEY, 'route': route_id, 'stop': stop_id, 'format': 'json'}
    url_p_route = "https://api-v3.mbta.com/predictions"
    print (payload)
    r = requests.get(url_p_route, params=payload)
    res = r.json()  ## josonfy the string
    # print (res) ## this is for logging and should not released!!
    # function returns -1 if there is an error
    foundStop = False
    stop_id = str(stop_id)

    url_p_stop_name = "https://api-v3.mbta.com/stops"
    payload_stop_name = {'api_key': API_KEY, 'id': stop_id, 'format': 'json'}
    r_name = requests.get(url_p_stop_name, params=payload_stop_name)
    res_name = r_name.json()
    #print(res_name)

    # print (res)
    # try:
    for predicton in res["data"]:
        attributes = predicton['attributes']
        departure_time = attributes['departure_time']
        outTimeFound = dateutil.parser.parse(departure_time)
        break
    timeNow = datetime.datetime.now(pytz.utc)

    for stop_id_info in res_name["data"]:
        stop_name = stop_id_info['attributes']['name']

    if (outTimeFound >= timeNow):
        time_diff = outTimeFound - timeNow
        minutesForNextBus = (time_diff.seconds // 60) % 60
    else:
        print("time not found")
        return -1
    if (is_train):
        outString = "The next " + route_id_str + " line train will arrive at stop " + stop_name + " in " + str(minutesForNextBus) + " Minutes "
    else:
        outString = "The next " + route_id_str + " bus will arrive at stop " + stop_name.replace(
            "@", "and").replace(" St", "") + " in " + str(minutesForNextBus) + " Minutes "
    print (outString)
    # except:
    #     print("some other error")


if __name__ == "__main__":
    main()
