from __future__ import print_function
import random
import logging


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome Response"
    speech_output = "Welcome to arithmetic tables. Say stop at anytime to stop playing. Say play again to restart it. Let's get started with the first question."
    reprompt_text = "Sorry, I did not understand the number. Please, choose a number from one to ten."
    should_end_session = False
    
    number = random.choice(list(range(1, 11)))
    
    #Choose random number from 1 to ten
    session_attributes['number'] = int(number)
    #choose random operation. 0 for addition, 1 for subtraction, 2 for multiply, 3 for division
    session_attributes['operation'] = random.choice(list(range(1, 5)))  

    #array of numbers that are gonna be randonly selected
    session_attributes['disponible_numbers'] = list(range(1, 11))  
    # User grade 
    session_attributes['grade'] = 0
    # We'll have a total of 10 calculations
    session_attributes['iterations'] = 10
    
    expected_result, speech_operation_output = get_random_operation(session_attributes)
    
    session_attributes['expected_result'] = int(expected_result)
    
    speech_output += ("          " + speech_operation_output)
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_random_operation(session_attributes):
    #Making random operations
    #Choosing random number
    disponible_numbers = session_attributes['disponible_numbers']
    next_number = disponible_numbers[0]
    
    #Choosing random operator
    operations = ['plus', 'minus', 'times', 'divided by']
    operation = session_attributes['operation']
    #removing number from the list
    disponible_numbers = disponible_numbers.pop(0)
    speech_output = "{} {} {}".format(session_attributes['number'], operations[operation], next_number)
    
    expected_result = 0
    if operation == 0:
        expected_result = int(session_attributes['number']) + int(next_number)
    
    elif operation == 1:
        expected_result = int(session_attributes['number']) - int(next_number)
    
    elif operation == 2:
        expected_result = int(session_attributes['number']) * int(next_number)    
        
    else:
        expected_result = int(session_attributes['number']) / int(next_number)
        
    return expected_result, speech_output

def answer_operation_response(intent, session):
    card_title = "Choose number"
    speech_output = ""
    reprompt_text = "Oops. That is an invalid number. Please, choose a number from one to ten."
    should_end_session = False
    
    session_attributes = session['attributes']
    
    response = int(intent['slots']['number']['value'])
    
    #The number entered by the user is a result of an operation
    if response == session_attributes['expected_result']:
        session_attributes['grade'] += 1
    
    session_attributes['iterations'] -= 1
    
    if session_attributes['iterations'] == 0:
        grade = session_attributes['grade']
        speech_output = "Your grade was {} of 10! Would you like to play again?.".format(grade)
        should_end_session = True
        
        return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))
    
    expected_result, speech_output = get_random_operation(session_attributes)
    session_attributes['expected_result'] = int(expected_result)
    
    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing arithmetic tables. Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def play_again_response():
    return get_welcome_response()

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific 
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlayAgainIntent":
        return play_again_response()
    elif intent_name == "AnswerNumberIntent":
        return answer_operation_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
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
