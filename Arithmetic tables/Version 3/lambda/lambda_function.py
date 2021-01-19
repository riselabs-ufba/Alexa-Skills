from __future__ import print_function
import logging
import random, json
from DatabaseController import DatabaseController

#Variable that indicates if a name is chosen. If it is, it won't fall into the answer_name_intent
name_exists = False

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

# --------------- Functions to make initial configurations ------------------

def set_session_initial_attributes(session_attributes, difficult):
    number = random.choice(list(range(1, 11)))
    
    #Choose random number from 1 to ten
    #choose random operation. 0 for addition, 1 for subtraction, 2 for multiply, 3 for division
    operation = random.choice(['plus', 'minus', 'times', 'divided by'])
    session_attributes['operation'] = operation
    
    #Choosing number based on the operator and by the difficulty level
    with open('./operations/operations_difficulty.json', 'r') as ops:
        operations = json.load(ops)
    number = int(random.choice(operations[operation][difficult]))
    session_attributes['number'] = int(number)

    #array of numbers that are gonna be randonly selected
    session_attributes['disponible_numbers'] = list(range(1, 11))  
    # User grade 
    session_attributes['grade'] = 0
    # We'll have a total of 10 calculations
    session_attributes['iterations'] = 10
    
    return session_attributes

# --------------- Functions to return datas ------------------

def get_random_operation(session_attributes):
    #Making random operations
    #Choosing random number
    disponible_numbers = session_attributes['disponible_numbers']
    next_number = disponible_numbers[0]
    
    #Choosing random operator
    operation = session_attributes['operation']
    #removing number from the list
    disponible_numbers = disponible_numbers.pop(0)
    speech_output = "{} {} {}".format(session_attributes['number'], operation, next_number)
    
    expected_result = 0
    if operation == 'plus':
        expected_result = int(session_attributes['number']) + int(next_number)
    
    elif operation == 'minus':
        expected_result = int(session_attributes['number']) - int(next_number)
    
    elif operation == 'times':
        expected_result = int(session_attributes['number']) * int(next_number)    
        
    else:
        expected_result = int(session_attributes['number']) / int(next_number)
        
    return expected_result, speech_output
    

# --------------- Functions that control the intents ------------------

def get_welcome_response(new_session=False):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    
    ''' Starting the database '''
    databaseController = DatabaseController()
    #databaseController.create_table_users()

    card_title = "Welcome Response"
    if new_session:
        speech_output = "Hello! Please, tell me your name"
    else:
        speech_output = "Ok! Let's play one more time. Tell me your name"

    reprompt_text = "Sorry, I did not understand your name. Please, repeat it."
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def answer_name_response(intent, session):
    card_title = "Confirm name"
    reprompt_text = "Sorry, I did not understand your answer. Please, repeat it."
    should_end_session = False
    session_attributes = {}
    if session.get('attributes'):
        session_attributes = session['attributes']
        if session['attributes'].get('user'):
            speech_output = "Oops. That is an invalid number. Please, choose a number from one to ten."
            return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    
    username = intent['slots']['username']['value']
    userId = session['user']['userId']
    ''' Checking name into the database '''
    databaseController = DatabaseController()
    dbUser = databaseController.find_user(userId, username)
    
    if not dbUser:    
        databaseController.insert_user(userId, username)
        speech_output = "Ok. Welcome to arithmetic tables, {}. Which difficult would you like to choose? Easy, medium or hard?".format(username)
        dbUser = databaseController.find_user(userId, username)

    else:
        speech_output = "It's good to have you back, {}!. In which difficult would you like to play? Easy, medium or hard?".format(username)

    #setting the user's propertys
    username = dbUser['name']
    user_total_score = dbUser['total_score']
    session_attributes['user'] = {"name": username, "total_score": user_total_score}
    #Setting the user
    name_exists = True
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    

def choose_difficult_response(intent, session):
    card_title = "Choose Difficult"
    reprompt_text = "Sorry. I did not understand the difficult you want."
    session_attributes = session['attributes']
    should_end_session = False
    
    #difficultId is 0 if the user chooses easy, 1 for medium and 2 for hard
    difficultId = intent['slots']['difficult']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
    difficultId = int(difficultId)
    if difficultId == 0:
        difficult = 'easy'
    elif difficultId == 1:
        difficult = 'medium'
    else:
        difficult = 'hard'
    
    #Setting the initial session attributes for the user
    session_attributes = set_session_initial_attributes(session_attributes, difficult)
    
    #Choosing the operation that the user will answer after giving his/her name
    expected_result, speech_operation_output = get_random_operation(session_attributes)
    session_attributes['expected_result'] = int(expected_result)
    speech_output = ("Ok, I got it. Ready for your first question? Then answer:          " + speech_operation_output)
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
    
def change_player_response():
    card_title = "Change Player"
    speech_output = "Ok! Let's change the player. New player, please tell me your name!"
    reprompt_text = "Sorry, I did not understand what you've sad"
    # Setting this to true ends the session and exits the skill.
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def answer_operation_response(intent, session):
    card_title = "Choose number"
    speech_output = ""
    reprompt_text = "Oops. That is an invalid number. Please, choose a number from one to ten."
    should_end_session = False
    
    print(session)
    session_attributes = session['attributes']
    
    response = int(intent['slots']['number']['value'])
    
    #The number entered by the user is a result of an operation
    if response == session_attributes['expected_result']:
        session_attributes['grade'] += 1
    
    session_attributes['iterations'] -= 1
    
    
    if session_attributes['iterations'] == 0:
        #If the number of questions are over, finish it
        grade = session_attributes['grade']
        username = session_attributes['user']['name']
        userId = session['user']['userId']

        '''Update the user's general score in the database'''
        databaseController = DatabaseController()
        databaseController.update_score(userId, username, grade)
        '''Get the new user's score'''
        new_score = int(session_attributes['user']['total_score'] + grade)
        
        speech_output = """I hope you enjoyed playing with me, {}. Your grade was {} of 10! 
                           Your general score is {}. Say play again to start over or exit to quit.""".format(username, grade, new_score)
        should_end_session = False
        
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

def help_response():
    card_title = "Help User"
    speech_output = """This is a litle game called arithmetic tables. I'm gonna ask you some mathematic questions and I wanna know if you can answer it. 
                        Your final score will be stored by the end of the game. You may say play again or start over to restart the game at anytime. 
                        If you want to change the name of the player, just say change name or change player.
                        You can say exit or close to exit the application."""
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def play_again_response():
    return get_welcome_response()

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    '''Starting the database'''
    
    pass

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    return get_welcome_response(True)

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlayAgainIntent":
        return play_again_response()
    elif intent_name == "AnswerNameIntent":
        if not name_exists:
            return answer_name_response(intent, session)
        else:
            return answer_operation_response(intent, session)
    elif intent_name == "ChooseDifficultIntent":
        return choose_difficult_response(intent, session)
    elif intent_name == "AnswerNumberIntent":
        return answer_operation_response(intent, session)
    elif intent_name == "ChangePlayerIntent":
        return change_player_response()
    elif intent_name == "AMAZON.HelpIntent":
        return help_response()
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
          
    return handle_session_end_request()

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