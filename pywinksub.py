"""
Handle the subscriptions responses between PubNub and Home-Assistant.
"""

import json

from pubnub import Pubnub

class PubNubWinkHandler():
    """
    Connection handler for PubNub.
    """

    def __init__(self, sub_key):
        """
        Create the PubNub connection object
        """
        self.subscriptions = {}
        self.channels = []
        self.current_data = {}
        self.pubnub = Pubnub(
            'N/A', sub_key, ssl_on=True)
        self.pubnub.set_heartbeat(120)

    def add_subscription(self, channel, function):
        """
        Add a channel to subscribe to and a callback function to
        run when the channel receives an update.
        """
        if channel not in self.channels:
            self.channels.append(channel)
            self.subscriptions[channel] = [function]
        else:
            self.subscriptions[channel].append(function)
        self.current_data[channel] = ''

    def subscribe(self):
        """
        Start the subscription to the channel list.
        """
        self.pubnub.subscribe(self.channels, self.pub_callback)

    def unsubscribe(self):
        """
        Stop the subscription to the channel list.
        """
        for channel in self.channels:
            self.pubnub.unsubscribe(channel)

    def pub_callback(self, message, channel):
        """
        Called when a new message is recevied on one of the subscribed
        to channels.
        Proccess the message and if it is new update the channels current data.
        If the data is new, also call the channels callback function.
        """
        if 'data' in message:
            json_data = json.dumps(message.get('data'))
        else:
            json_data = message
        for func in self.subscriptions[channel]:
            if self.current_data[channel] != json_data:
                func(json.loads(json_data))
        self.current_data[channel] = json_data
