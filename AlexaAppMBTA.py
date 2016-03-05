"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
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
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


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
    card_title = "Welcome to MBTA next bus app"
    speech_output = "Welcome to the Alexa MBTA next bus app " \
                    "Please tell me your stop eye d, and route number." \
                    "For example my stop eye D is one four one nine and route number is sixty nine"
    card_text = "Welcome to the Alexa MBTA next bus app " \
                "Please tell me your stop ID, and route number." \
                "For example my stop ID is 1419 and route number is 69"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your stop I D, and route number." \
                    "my stop eye D is one four one nine. and router number is 69"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, card_text, should_end_session))

def find_next_bus(intent, session):
    """ sets stop id into session"""

    card_title = intent['name']
    session_attributes = {}

    if 'StopId' in intent['slots']:
        myStopID = intent['slots']['StopId']['value']
        if 'routeId' in intent['slots']:
            myRouteId = intent['slots']['routeId']['value']
            
            speech_output = seach_mbta(myStopID,myRouteId)
            reprompt_text = None
        else:
            speech_output = "I'm not sure what your route number is. " \
                        "Please try again."
            reprompt_text = "I'm not sure what your route eye D is. " \
                        "You can tell me your stop eye D and route number, " \
                        "my stop eye D is one four one nine. and route number is 69"
    else:
        speech_output = "I'm not sure what your stop I D is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your stop eye D is. " \
                        "You can tell me your stop eye D and route number. " \
                        "my stop eye D is one four one nine. and route number is 69"
    card_text = speech_output
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
            'title': title,
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

    #print res
    foundStop = False
    try:
        for direction in res["direction"]:
            for trip in direction["trip"]:
                for stopOutbound in trip["stop"]:
                    if (stopOutbound["stop_id"] == stop_id)and(foundStop == False):
                        foundStop = True
                        tripDirection = trip["trip_headsign"]
                        outTime = datetime.datetime.fromtimestamp(int(stopOutbound["sch_arr_dt"]),pytz.UTC)
        if foundStop == False:
            return "Sorry please try another stop"

        timeNow = datetime.datetime.now(pytz.utc)

        if (outTime > timeNow):
            time_diff = outTime - timeNow
            minutesForNextBus = (time_diff.seconds//60)%60
        else:
            return "Sorry please try later"

        outString = "The next " + route_id +" bus towards "+ tripDirection + " will arrive at stop " +stop_id+ " in "+ str(minutesForNextBus) + " Minutes"

        return outString
    except:
        print 
        return "sorry please try another stop I D and route"
    

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }