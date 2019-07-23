# -*- coding: utf-8 -*-

import datetime
import random
import configparser
import forecastio
from slack import WebClient

config = configparser.ConfigParser()
config.read("config.ini")
authed_teams = {}


class PlayvoxBot(object):

    def __init__(self):
        super(PlayvoxBot, self).__init__()
        self.name = "playvoxbot"
        self.as_user = True
        self.oauth = {"client_id": config.get("slack", "client_id"),
                      "client_secret": config.get("slack", "client_secret"),
                      "scope": "bot"}
        self.verification = config.get("slack", "verification_token")
        self.client = WebClient(token=config.get("slack", "oauth_secret"))

    def auth(self, code):
        print('client_id: {} ----- client_secret: {} ----- code:{}'.format(self.oauth["client_id"], self.oauth["client_secret"], code))
        auth_response = self.client.oauth_access(
                client_id=self.oauth["client_id"],
                client_secret=self.oauth["client_secret"],
                code=code)

        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}

        self.client = WebClient(authed_teams[team_id]["bot_token"])

        print('user_id: {}'.format(auth_response['user_id']))

    def open_dm(self, user_id):
        new_dm = self.client.im_open(user=user_id)
        dm_id = new_dm["channel"]["id"]
        return dm_id

    def __get_user_info(self, user_id):
        user_info = self.client.users_info(user=user_id)
        return user_info

    def get_username(self, user_id):
        username = self.__get_user_info(user_id)["user"]["real_name"]
        return username

    def is_myself(self, user_id):
        if self.__get_user_info(user_id)["user"]["is_bot"] is True and self.__get_user_info(user_id)["user"]["name"] == self.name:
            return True
        return False

    def is_channel(self, channel_id):
        channel_info = self.client.channels_info(channel=channel_id)
        if channel_info["ok"] is True:
            return True
        return False

    def __weather_message(self):
        forecast = forecastio.load_forecast(key=config.get(
            "forecast.io", "secret_key"), lat="5.070275", lng="-75.513817",
            lang="en", time=datetime.datetime.now())

        text = "{} {} // ↑ {}ºC - ↓ {}ºC".format(
            forecast.daily().data[0].summary,
            datetime.datetime.today().date(),
            int(round(forecast.daily().data[0].temperatureHigh)),
            int(round(forecast.daily().data[0].temperatureLow)),
        )

        return text

    def onboarding_message(self, team_id, user_id):
        self.client.chat_postMessage(
            channel=self.open_dm(user_id),
            text="¡Welcome to Bot!")

    def __random_tips(self):
        list_random_phrases = ["Do more & be faster", "Take action based on real data", "Get better results", "Write great emails", "Get involved in the community", "Clean up your branches"]
        return random.choice(list_random_phrases)

    def command_answer_message(self, event_type):
        payload = None
        if event_type == "/weather":

            payload = {'text': self.__weather_message()}
        elif event_type == "/tips":
            payload = {'text': self.__random_tips()}

        return payload

    def answer_message(self, slack_event):
        event_type = slack_event["event"]["type"]
        user_id = slack_event["event"]["user"]
        channel = slack_event["event"]["channel"]
        incoming_message = slack_event["event"]["text"]

        print('**** properties: event:{}, user_id: {}, channel:{}, incoming_message:{} ****'.format(event_type, user_id, channel, incoming_message))

        if incoming_message.upper() in ['FEO', 'SHIT', 'MALDITO', 'BITCH']:
            self.client.chat_postMessage(
                channel=channel,
                text="Your language is offensive, <@{}> https://media.giphy.com/media/GBIzZdF3AxZ6/giphy.gif".format(user_id))
            return

        elif incoming_message.upper() in ['HOLA', 'HI', 'HELLO']:
            self.client.chat_postMessage(
                channel=channel,
                text="Hello, <@{}> from playvoxbot".format(user_id))
            return

        elif incoming_message.upper() in ['TIEMPO', 'CLIMA', 'TIME', 'WEATHER']:
            text = self.__weather_message()
            self.client.chat_postMessage(
                channel=channel,
                text=text)

        else:
            buttonUrl = 'https://www.google.com/search?q={}'.format(incoming_message.replace(" ", "+"))

            self.client.chat_postMessage(
                channel=channel,
                text="I do not understand you, but Google will have to separate the answer.",
                attachments=[
                    {
                        'fallback': buttonUrl,

                        'actions': [
                            {'type': 'button', 'text': 'Buscar :mag:',
                             'url': buttonUrl, 'style': 'primary'}]
                    }
                ]
            )

        return
