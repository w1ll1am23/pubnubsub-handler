"""
Handle the subscriptions responses between PubNub and Home-Assistant.
"""

import json
import sys

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeCallback, PNOperationType, \
                          PNStatusCategory

SUBSCRIPTIONS = {}
CHANNELS = []
CURRENT_DATA = {}

class PubNubWinkHandler():
    """
    Connection handler for PubNub.
    """

    def __init__(self, sub_key):
        """
        Create the PubNub connection object
        """
        self.pnconfig = PNConfiguration()
        self.pnconfig.subscribe_key = sub_key
        self.pnconfig.ssl = True
        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(PubNubWinkCallback())

    def add_subscription(self, channel, function):
        """
        Add a channel to subscribe to and a callback function to
        run when the channel receives an update.
        """
        if channel not in CHANNELS:
            CHANNELS.append(channel)
            SUBSCRIPTIONS[channel] = [function]
        else:
            SUBSCRIPTIONS[channel].append(function)
        CURRENT_DATA[channel] = ''

    def subscribe(self):
        """
        Start the subscription to the channel list.
        """
        for channel in CHANNELS:
            sys.stdout.write("Channel: " + channel + "\n")
        for key, value in SUBSCRIPTIONS.items():
            sys.stdout.write("Key: " + key + "\n")
        sys.stdout.flush()
        self.pubnub.subscribe().channels(CHANNELS).execute()

    def unsubscribe(self):
        """
        Stop the subscription to the channel list.
        """
        self.pubnub.unsubscribe_all()

class PubNubWinkCallback(SubscribeCallback):
    """
    PubNub Callback handler.
    """

    def status(self, pubnub, status):
        """
        Things to do on different status updates.
        """
        if status.operation == PNOperationType.PNSubscribeOperation \
                and status.category == PNStatusCategory.PNConnectedCategory:
            print("connected")

    def presence(self, pubnub, presence):
        """
        Not sure what to do here.
        """
        pass

    def message(self, pubnub, message):
        """
        Called when a new message is recevied on one of the subscribed
        to channels.
        Proccess the message and if it is new update the channels current data.
        If the data is new, also call the channels callback function.
        """
        if 'data' in message.message:
            json_data = json.dumps(message.message.get('data'))
        else:
            json_data = message.message
        for func in SUBSCRIPTIONS[message.subscribed_channel]:
            if CURRENT_DATA[message.subscribed_channel] != json_data:
                func(json.loads(json_data))
        CURRENT_DATA[message.subscribed_channel] = json_data
