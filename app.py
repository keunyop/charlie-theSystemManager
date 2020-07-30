# -*- coding: utf-8 -*-

# pip install flask request make_response jsonify
import json
#from slacker import Slacker
import logging
from slack import WebClient
from slack.errors import SlackApiError
from flask import Flask, request, make_response, jsonify
import datetime
import sys
sys.path.insert(0, './lib')
import sys
sys.path.insert(0, '../charlie-theSystemManager')
import system_info as si

# token은 charlie 봇에 대한 OAuth & Permissions 입니다.
# https://api.slack.com/apps/A015W9HG7FV/oauth?
#token = 'xoxb-621965038067-1193406469174-ZWa1VfOBB1q7juZomteYk8Fy'
token = 'xoxb-621965038067-1193406469174-hLjdpCEQ5pj6OKoeO3QTaCtR'
client = WebClient(token=token)
#slack = Slacker(token)

app = Flask(__name__)

def printlog(log_type=INFO, message=''):
    #print(message)
    if log_type == INFO :
        logging.info(message)
    elif log_type == WARNING:
        logging.warning(message)
    elif log_type == ERROR:
        logging.error(message)
    else :
        logging.debug(message)

def get_users(user_type="name"):
    response = client.users_list()
    #users = response["members"]
    #print(users)
    user_list = dict([(x['name'], x['id']) for x in response['members']])
    print(user_list)
    '''
    if user_type == "name":
        user_list = list(map(lambda u: u["deleted"], users))
    elif user_type == "id":
        user_list = list(map(lambda u: u["id"], users))
    print(user_list)
    '''

def get_answer(slack_event):
    return si.system_info(user_text, intent)


# 이벤트 핸들하는 함수
def event_handler(event_type, slack_event):
    user_message = slack_event["event"]["text"]

    ###############################################
    # 사용자(User)가 @Charlie로 메시지 전송하는경우
    ###############################################
    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        #text = get_answer()
        #response = client.chat_postMessage(channel, text)
        user = slack_event["event"]["user"]
        text = get_answer(slack_event)
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=text,
                user=user)
            assert response["message"]["text"] == text
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            #print(f"Got an error: {e.response['error']}")

        return make_response(slack_event["event"], 200, {"content_type": "application/json"})


    ###############################################
    # 사용자(User)와 Charlie의 1:1대화 하는 경우.
    ###############################################
    if event_type == "message":
        channel = slack_event["event"]["channel"]
        user = slack_event["event"]["user"]
        user_text = slack_event["event"]["text"]

        #get_users('name')
        print(">> [{}][{}]".format(user, user_text))
        text = get_answer(slack_event)

        try:
            print(text)
            response = client.chat_postMessage(
                channel=channel,
                text=text,
                user=user)
            #print(">> response[{}], text[{}]".format(response["message"]["text"], text))
            #assert response["message"]["text"] == text
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            #print(f"Got an error: {e.response['error']}")

        return make_response(slack_event["event"], 200, {"content_type": "application/json"})

    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    print(">> message [{}]".format(message))
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

# default route
#@app.route("/slack", methods=["GET", "POST"])
@app.route('/')
def index():
    #return 'python slackclient flask App(/)'
    return make_response("Charlie App(/)", 200, {"Content-type": "text/plain"})

@app.route('/intent', methods=[ 'POST'])
def validate_intent():
    req_data = json.loads(request.data)
    
    #print(">> rawdata : {}".format(rawdata))
    #print(">> mtx : {}".format(mtx))
    print(">> vectorizer : {}".format(vectorizer))
    print(">> message : {}".format(req_data['message']))

    _dict = iv.validate_intent(rawdata, mtx, vectorizer, req_data['message'])
    print(">> _dict : {}".format(_dict))
    #print("intent_dict = score [{}], intent [{}]".format(_dict['score'],_dict['intent']))

    return make_response(_dict, 200, {"content_type": "application/json"})

@app.route("/slack", methods=["GET", "POST"])
def slack_event():
    #print("\nrequest data [{}]".format(request.data))
    if len(request.data) == 0:
        return make_response("Charlie App(/slack)", 200, {"Content-type": "text/plain"})

    slack_event = json.loads(request.data)
    #print("\n>> slack_event [{}]".format(slack_event))
    ###############################################
    # Event Subscriptions 에서 Request test용
    ###############################################
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    ###############################################
    # User 이벤트인지, Charlie의 이벤트인지 구분
    ###############################################
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        #print(">> event_type [{}]".format(event_type))

        if "bot_profile" in slack_event["event"]:
            bot_name = slack_event["event"]["bot_profile"]["name"]
            #print("\n>> [{}] event from bot [{}]".format(event_type, bot_name))
            #print("> slack_event [{}]".format(slack_event))
            #return make_response("Response OK", 200, {"X-Slack-No-Retry": 1})
            return make_response("봇 리턴으로 입력된 이벤트 입니다.", 200, {"Content-type": "text/plain"})

        if "blocks" in slack_event["event"]:
            user_name = slack_event["event"]["user"]
            print("\n>> [{}] event from user [{}]".format(event_type, user_name))
            #print(">> slack_event [{}]".format(slack_event))
            print("request data [{}]".format(request.data))
            printlog(DEBUG, '>> slack_event {}'.format(slack_event))
            return event_handler(event_type, slack_event)

    return make_response("슬랙 요청에 이벤트가 없습니다.", 404, {"X-Slack-No-Retry": 1})

if __name__ == '__main__':
    
    ###############################################
    # 테스트/개발 환경에 대해 이야기하는 경우 디버그 옵션을 사용. 
    # 코드 변경이 발생하면 flask 앱을 자동으로 다시로드
    ###############################################
    #app.run('0.0.0.0', port=5000)
    app.run('0.0.0.0', port=5000, debug=True)

    # conda activate <ENV Name>
    # python app.py
    # ./ngrok http 5000
    # http://<랜덤값>.ngrok.io/slack
