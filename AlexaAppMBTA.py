"""
search MBTA bus based on stop ID and bus route number.
Sample "my stop id is one four one nine and stop id is sixty nine"

"""

from __future__ import print_function
import requests
import time
import datetime
import pytz

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "findNextBusIntent":
        return find_next_bus(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif ((intent_name == "AMAZON.StartOverIntent") or (intent_name == "AMAZON.RepeatIntent")):
        return get_welcome_response()
    else:
        return stopSession()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Boston T-time"
    speech_output = "Welcome to the boston T. time. " \
                    "Please tell me your stop I D and route number, " \
                    "For example my stop I D is one four one nine and route number is sixty nine. You can also say ask boston t. time when is the next 69 bus at stop 1419. "
    card_text = "Welcome to the Boston T-time" \
                "Please tell me your stop ID, and route number. " \
                "For example \"my stop ID is 1419 and route number is 69\". You can also say \" ask boston T-time when is the next 69 bus at stop 1419."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your stop I. D. and route number. " \
                    "my stop I. D. is one four one nine. and route number is 69. "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, card_text, should_end_session))

def get_help_response():
    """ Print/Say help text
    """

    session_attributes = {}
    card_title = "Boston T-time"
    speech_output = "With the Boston T. time app you can find when the next bus would arrive at your stop. " \
                    "To use the app you should know the STOP I D and Route Number. " \
                    "The route number is usually the bus number, and stop I D can be found on the M. B. T. A. Bus Stop Sign. " \
                    "The stop I D can also be found online from the M. B. T. A. website. " \
                    "Can you please tell me your stop I D and bus number ? "
    card_text = "With the Boston T-time app you can find when the next bus would arrive at your stop.  " \
                "To use the app you should know the STOP ID and Route Number. " \
                "The route number is usually the bus number, and stop ID can be found on the MBTA Bus Stop Sign. " \
                "You can also find the STOP ID at http://www.mbta.com/rider_tools/realtime_bus/. " \
                "You can tigger the app by saying Alexa, ask Boston T-time. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "With the Boston T. time app you can find when the next bus would arrive at your stop. " \
                    "To use the app you should know the STOP I D and Route Number. " \
                    "The route number is usually the bus number, and stop I D can be found on the M. B. T. A. Bus Stop Sign. " \
                    "The stop I D can also be found online from the M. B. T. A. website. You can check the alexa app for a link. " \
                    "Can you please tell me your stop I D and bus number ?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, card_text, should_end_session))

def find_next_bus(intent, session):
    """ sets stop id into session"""

    card_title = "Boston T-time"
    session_attributes = {}
    error = False
    try:
        if 'StopId' in intent['slots']:
            myStopID = int(intent['slots']['StopId']['value'])
            if 'routeId' in intent['slots']:
                myRouteId = intent['slots']['routeId']['value']
                
                speech_output = seach_mbta(myStopID,myRouteId)
                if (speech_output == -1):
                    error = True
                    speech_output = "There was an error with the request, please try another stop id and route."

                reprompt_text = None
            else:
                error = True
                speech_output = "I'm not sure what your route number is. " \
                            "Please try again. "
                reprompt_text = "I'm not sure what your route I D is. " \
                            "Please tell me your stop I D and route number again, "
        else:
            error = True
            speech_output = "I'm not sure what your stop I D is. " \
                            "Please try again. "
            reprompt_text = "I'm not sure what your stop I D is. " \
                            "Please tell me your stop I D and route number. "
    except:
        error = True
        speech_output = "Sorry I didn't get that. " \
                        "Please try again. " \
                        "You can say my stop I.D. is one four one nine, and route number is sixty nine. "
        reprompt_text = "I'm not sure what your stop I D and Route number is. " \
                        "Please tell me your stop I D and route number, " \
                        "for example, my stop I D is one four one nine. and route number is 69"
    card_text = speech_output
    
    if (error == True):  ## do not close the seesion if there was an error in the request
        should_end_session = False
    else:
        should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, card_text,should_end_session))

def build_speechlet_response(title, output, reprompt_text, card_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Boston T-time',
            'content': card_text
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def seach_mbta(stop_id,route_id):
    API_KEY = "wX9NwuHnZU2ToO7GmGR9uw"
    payload = {'api_key':API_KEY,'route':route_id,'format':'json'}
    url_p_route = "http://realtime.mbta.com/developer/api/v2/predictionsbyroute"
    r = requests.get(url_p_route, params=payload)
    res = r.json() ## josonfy the string
    print (res) ## this is for logging and should not released!!
    #function returns -1 if there is an error
    foundStop = False
    stop_id  = str(stop_id)
    try:
        timeNow = datetime.datetime.now(pytz.utc)
        for direction in res["direction"]:
            for trip in direction["trip"]:
                for stopOutbound in trip["stop"]:
                    outTime = datetime.datetime.fromtimestamp(int(stopOutbound["sch_arr_dt"]),pytz.UTC)
                    if (stopOutbound["stop_id"] == stop_id)and(foundStop == False)and(outTime >= timeNow):
                        foundStop = True
                        tripDirection = trip["trip_headsign"]
                        outTimeFound = datetime.datetime.fromtimestamp(int(stopOutbound["sch_arr_dt"]),pytz.UTC)
        if foundStop == False:
            return -1

        timeNow = datetime.datetime.now(pytz.utc)

        if (outTimeFound >= timeNow):
            time_diff = outTimeFound - timeNow
            minutesForNextBus = (time_diff.seconds//60)%60
        else:
            return -1

        outString = "The next " + route_id +" bus towards "+ tripDirection + " will arrive at stop " +stop_id+ " in "+ str(minutesForNextBus) + " Minutes"

        return outString
    except:
        return -1

def stopSession():
    session_attributes = {}
    card_title = "Boston T-time"
    speech_output = "Good Bye !!"
    card_text = "Good Bye !!"
    reprompt_text = "Good Bye !!"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, card_text, should_end_session))

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }