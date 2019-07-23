# -*- coding: utf-8 -*-
import json
import bot
from flask import Flask, request, make_response, render_template, jsonify

playvox_bot = bot.PlayvoxBot()
slack = playvox_bot.client

app = Flask(__name__)


def event_handler(event_type, slack_event):

    team_id = slack_event.get("team_id")

    print('***** event_type: {}----- info: {}'.format(event_type, slack_event))

    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        playvox_bot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200)

    if event_type == "message" or event_type == "app_mention":
        try:
            user_id = slack_event["event"]["user"]
            if playvox_bot.is_myself(user_id):
                return make_response("Message by myself", 200, {"X-Slack-No-Retry": 1})

            playvox_bot.answer_message(slack_event)

            return make_response("Answer Sent", 200)

        except Exception:
            return make_response("Unhandled message", 200, {"X-Slack-No-Retry": 1})

    return make_response("You have not added an event handler for the %s" % event_type, 200, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def root():
    client_id = playvox_bot.oauth["client_id"]
    scope = playvox_bot.oauth["scope"]
    return render_template("index.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    playvox_bot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/slash", methods=["POST"])
def slash_commands():
    slack_event = request.form

    if playvox_bot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \nPlayvoxBot has: \
                   % s\n\n" % (slack_event["token"], playvox_bot.verification)

        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "command" in slack_event:
        event_type = slack_event.get('command')
        payload = playvox_bot.command_answer_message(event_type)
        return jsonify(payload)

    return make_response("Unhandled event", 404, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    if playvox_bot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \nPlayvoxBot has: \
                   % s\n\n" % (slack_event["token"], playvox_bot.verification)

        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return event_handler(event_type, slack_event)

    return make_response("Unhandled event", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
