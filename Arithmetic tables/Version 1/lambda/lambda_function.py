from __future__ import print_function
import random

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Arithmetic Tables - " + title,
            'content': "Alexa - " + output
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
    card_title = "Choose operation"
    speech_output = "Welcome to arithmetic tables. Which operation would you like to choose from: addition, subtraction, times, division"
    reprompt_text = "Sorry, I did not understand the operation. Please, tell me which operation would you like to choose from: addition, subtraction, times and division."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def choose_operation_response(intent, session):
    session_attributes = {}
    card_title = "Choose operation"
    reprompt_text = "Sorry, I did not understand the number. Please, choose a number from one to ten."
    should_end_session = False
    
    if not session.get('attributes'): 
        operation = intent['slots']['operation']['value']
        session_attributes = {
            "operation": operation
        }
        speech_output = "Please, choose a number from one to ten."
    
    else:
        session_attributes = session['attributes']
        operation = session_attributes['operation']
        speech_output = "Oops. I didn't understand your number. Please, choose a number from one to ten.".format(operation)
    
    
    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    

def choose_number_response(intent, session):
    card_title = "Choose number"
    speech_output = ""
    reprompt_text = "Oops. I didn't understand your number. Please, repeat for me."
    should_end_session = False
    
    session_attributes = {}
    
    if not session.get('attributes'):
        speech_output = "Sorry, wrong operation. Choose an operation between addition, subtraction, times and division."    
        
        
    else:
        session_attributes = session['attributes']
        number = intent['slots']['number']['value']
        
        
        if not session['attributes'].get('number'):
            if int(number) > 10:
                speech_output = "Looks like your number is too high. Please choose a number from one to ten"
                return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            else: 
                session_attributes['number'] = int(number)
                #array of numbers that are gonna be randonly selected
                session_attributes['disponible_numbers'] = list(range(1, 11))  
                # User grade 
                session_attributes['grade'] = 0
                # We'll have a total of 10 calculations
                session_attributes['iterations'] = 10
        
        else:
            #The number entered by the user is a result of an operation
            result = int(number)
            
            if result == session_attributes['expected_result']:
                session_attributes['grade'] += 1
            
            session_attributes['iterations'] -= 1
            
            if session_attributes['iterations'] == 0:
                grade = session_attributes['grade']
                speech_output = "Your grade was {} of 10! Thank you for playing arithmetic tables.".format(grade)
                should_end_session = True
                return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
        
        #Making random operations
        disponible_numbers = session_attributes['disponible_numbers']
        random_number = random.choice(disponible_numbers)
        #removing number from the list
        disponible_numbers.pop(disponible_numbers.index(random_number))
        speech_output = "{} {} {}".format(session_attributes['number'], session_attributes['operation'], random_number)
        
        expected_result = 0
        if session_attributes['operation'] == 'addition':
            expected_result = int(session_attributes['number']) + int(random_number)
        
        elif session_attributes['operation'] == 'subtraction':
            expected_result = int(session_attributes['number']) - int(random_number)
        
        elif session_attributes['operation'] == 'times':
            expected_result = int(session_attributes['number']) * int(random_number)    
            
        else:
            expected_result = int(session_attributes['number']) / int(random_number)
        
        session_attributes['expected_result'] = int(expected_result)

    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    
    
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

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
    if intent_name == "ChooseOperation":
        return choose_operation_response(intent, session)
    elif intent_name == "ChooseNumber":
        return choose_number_response(intent, session)
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
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

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