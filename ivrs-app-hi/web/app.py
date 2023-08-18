
from threading import Thread
import sys
import requests
import json

from flask import (
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)

import flask
from flask import Flask
from twilio.twiml.voice_response import Gather, VoiceResponse, Say, Redirect#,Hangup 

app = Flask(__name__)

shared_dict = None
req_counter = 0
CARD_NUM = None
INTENT = ""
ENTITY = ""
VALUE = ""
ONLY_VALUE = False

@app.route('/')
def hello():
    return('welcome to twilio ivr bot, please dial a twilio number to talk to the bot')

@app.route('/home', methods=['GET', 'POST'])
def home():
    response = VoiceResponse()
    with response.gather(action=url_for('intent'), method="POST", input='speech', language='hi-IN', timeout=3) as g:
#         g.say(message="please mention your problem", language="en-IN", voice='man')
        g.play('https://ivrs-demo-2239.twil.io/welcome.mp3') #twilio assets
#         g.play('https://res.cloudinary.com/cloud08/video/upload/v1655456878/welcome_bc7rxz.mp3') #cloudinary
    return twiml(response)

@app.route('/intent', methods=['POST'])
def intent():
    #url = 'https://rasa_nlu:5005/model/parse'
    url = 'http://rasa_nlu:5005/model/parse'
    message = str(request.form['SpeechResult'])
    data = {"text": message}
    rasa_response = requests.post(url, json=data)
    shared_dict = rasa_response.json()
#     global req_counter
#     url = 'https://demo-rasa.herokuapp.com/model/parse'
#     data = {"text": str(request.form['SpeechResult'])}
    
#     if req_counter == 0:
#         t=Thread(target=send_post_req, args=(url, data))
#         t.setDaemon(True)
#         t.start()
#         req_counter = 1
        
#     if shared_dict:
        
    global INTENT
    global ENTITY
    global VALUE
    global ONLY_VALUE

    if ONLY_VALUE == False:
        INTENT = shared_dict['intent']['name']
        entities = shared_dict['entities']
        if entities:
            ENTITY = entities[0]['entity']
            VALUE = entities[0]['value']
        else:
            ENTITY = ''
            VALUE = ''
    else:
        entities = shared_dict['entities']
        if entities:
            VALUE = entities[0]['value']
        else:
            VALUE = ''
            
    response=VoiceResponse()        

    
    if INTENT == "loss_report" or INTENT == "unblock_report":
        response.redirect('/loss/card_num')
        return twiml(response)
    elif INTENT == "fraud_report":
        if ("करेंट" in VALUE)  or ("करंट" in VALUE) or ("करेंट" in message) or ("करंट" in message):
            response.redirect('/loss/card_num')
        
        elif (("एन आर आई" in VALUE) or ("एन आर आई" in message) or ("एनआरआई" in VALUE) or ("एनआरआई" in message)):
            response.redirect('/loss/card_num')
            
        elif (("डेबिट" in VALUE) or ("क्रेडिट" in VALUE ) or ("प्रीपेड" in VALUE ) or ("सेविंग्स" in VALUE ) or ("सेविंग" in VALUE ) or ("एटीएम" in VALUE )):
            response.redirect('/fraud/card_num')
        
        else:
            ONLY_VALUE = True
            with response.gather(action='/intent', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#                 g.say(message="Please mention one among savings account, credit/prepaid card, current account, NRI account", language="en-IN", voice='man')
                g.play('https://ivrs-demo-2239.twil.io/cardname.mp3')
        
        return twiml(response)
        
    else:
        response.say("please mention intent", language="en-IN", voice='man')
        response.redirect("/home")
    
    return twiml(response)

##################################################################################################################
# LOSS REPORT AND UNBLOCK REPORT FLOW

@app.route('/loss/card_num', methods=['POST'])
def loss_card_num():
    response = VoiceResponse()
    with response.gather(action='/loss/card_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#         g.say(message="Enter your 16 digit card number", language="en-IN", voice='man')
#         g.play('https://res.cloudinary.com/cloud08/video/upload/v1655456832/cardnum_onejdl.mp3') #cloudinary
        if INTENT == 'loss_report':
            g.play('https://ivrs-demo-2239.twil.io/losscardnum.mp3') #twilio assets
        elif INTENT == 'unblock_report':
            g.play('https://ivrs-demo-2239.twil.io/unblockcardnum.mp3') #twilio assets
        elif INTENT == 'fraud_report':
            g.play('https://ivrs-demo-2239.twil.io/fraudcardnum.mp3') #twilio assets
        else:
            g.say('incorrect intent')
    
    return twiml(response)

@app.route('/loss/card_confirm', methods=['POST'])
def loss_card_confirm(): 
    global CARD_NUM 
    cardNumString = request.form['SpeechResult']
    CARD_NUM  = validateCardNum(cardNumString)
    
    response = VoiceResponse()
    if CARD_NUM :
        with response.gather(action='/loss/connect_call', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say(f'Card number you entered is {CARD_NUM }. To confirm say "sahi". To cancel and re-enter say "vapas".', language="en-IN", voice='man')
#             g.play('https://ivrs-demo-2239.twil.io/cardnumconfirm1.mp3')
            g.say(f'{CARD_NUM }', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/cardnumoptions2.mp3') #twilio assets
#             g.play('https://res.cloudinary.com/cloud08/video/upload/v1655456878/cardnumoptions2_s8psyq.mp3') #cloudinary
    
    else:
        with response.gather(action='/loss/card_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say('Please mention correct 16 digit card number', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/againcardnum.mp3')

    return twiml(response)

@app.route('/loss/connect_call', methods=['POST'])
def loss_connect_call():
    option = request.form['SpeechResult']
    response = VoiceResponse()
    if option == "सही!":
#         response.say('Connecting call to our agent. Please wait')
        response.play('https://ivrs-demo-2239.twil.io/connectcall.mp3') #twillio assets
#         response.play('https://res.cloudinary.com/cloud08/video/upload/v1655456832/connectcall_k6oepu.mp3') #cloudinary
        response.hangup()
    elif option == "वापस!" or option == 'वापिस!':
        response.redirect('/loss/card_num')
    else:
        with response.gather(action='/loss/connect_call', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say(f'incorrect response, Card number you entered is {CARD_NUM }. To confirm say "sahi". To cancel and re-enter say "vapas".', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/incorrectans.mp3')
#             g.play('https://ivrs-demo-2239.twil.io/cardnumconfirm1.mp3')
            g.say(f'{CARD_NUM }', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/cardnumoptions2.mp3')
 
    return twiml(response)

###########################################################################################################################
# FRAUD REPORT FLOW

@app.route('/fraud/card_num', methods=['POST'])
def fraud_card_num():
    response = VoiceResponse()
    with response.gather(action='/fraud/card_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#         g.say(message="Enter your 16 digit card number or 12 digit bank account number.", language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/fraudcardnum.mp3')

    return twiml(response)

@app.route('/fraud/card_confirm', methods=['POST'])
def fraud_card_confirm():
    global CARD_NUM
    cardNumString = request.form['SpeechResult']
    CARD_NUM = validateCardNum(cardNumString)
    
    response = VoiceResponse()
    if CARD_NUM:
        with response.gather(action='/fraud/otp_response', method="POST", input='speech', language='hi-IN', timeout=4) as g:
#             g.say(f'Card number you entered is {CARD_NUM}. To receive OTP say "bhhejo". To enter OTP say "OTP". To cancel and re-enter say "vaapas".', language="en-IN", voice='man')
#             g.play('https://ivrs-demo-2239.twil.io/cardnumconfirm1.mp3')
            g.say(f'{CARD_NUM }', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/otpoptions2.mp3')

    else:
        with response.gather(action='/fraud/card_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say('Please mention correct 16 digit card number or 12 digit bank account number', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/againcardnum.mp3')

    return twiml(response)


@app.route('/fraud/otp_response', methods=['POST'])
def otp_reponse():
    otpResponse = request.form['SpeechResult']
    response = VoiceResponse()
    
    if otpResponse=='भेजो!':
#         response.say('OTP has been sent to your registered mobile number. Please check')
        response.play('https://ivrs-demo-2239.twil.io/otpsent.mp3')
        
        response.hangup()
    elif otpResponse == 'ओटीपी!':
        with response.gather(action='/fraud/otp_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say('Please enter the OTP you recived', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/enterotp.mp3')
    elif otpResponse == 'वापस!' or otpResponse == 'वापिस!':
        response.redirect('/fraud/card_num')
    else:
        with response.gather(action='/fraud/otp_response', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say(f'incorrect response, Card number you entered is {CARD_NUM}. To receive OTP say "bhhejo". To enter OTP say "OTP". To cancel and re-enter say "vaapas".', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/incorrectans.mp3')
#             g.play('https://ivrs-demo-2239.twil.io/cardnumconfirm1.mp3')
            g.say(f'{CARD_NUM }', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/otpoptions2.mp3')

    return twiml(response)

@app.route('/fraud/otp_confirm', methods=['POST'])
def otp_confirm():
    otpString = request.form['SpeechResult']
    OTP = validateOtp(otpString)
    response = VoiceResponse()
    if OTP:
#         response.say('Connecting call to our agent. Please wait')
        response.play('https://ivrs-demo-2239.twil.io/connectcall.mp3')
        response.hangup()
    else:
        with response.gather(action='/fraud/otp_confirm', method="POST", input='speech', language='hi-IN', timeout=3) as g:
#             g.say(f'Incorrect OTP, Enter again.', language="en-IN", voice='man')
            g.play('https://ivrs-demo-2239.twil.io/incorrectans.mp3')
            
    return twiml(response)

###################################################################
def send_post_req(url, data):
    global shared_dict
    rasa_response = requests.post(url, json=data)
    shared_dict = rasa_response.json()
    
def twiml(resp):
    resp = flask.Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

#####################################################################

# helper functions
def validateCardNum(cardNumString):
    cardNum = ""
    Length = 0
    for num in cardNumString:
        if num.isdigit():
            cardNum += num
            Length += 1
            
    if Length == 6:
        return cardNum
    else:
        return None
    
def validateOtp(otpString):
    OTP = ""
    for num in otpString:
        if num.isdigit():
            OTP += num
            
    if OTP == "1234" or OTP == "1234!":
        return OTP
    else:
        return None
            
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)
