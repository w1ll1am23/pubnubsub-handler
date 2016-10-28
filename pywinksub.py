"""
Handle the subscriptions responses between PubNub and Home-Assistant.
"""

import json
import threading
import time
import sys
import os

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
        self.update_funcs = []
        self.current_data = {}
        self.sub_key = sub_key
        self.pubnub = Pubnub(
            'N/A', self.sub_key, ssl_on=True)
        #self.pubnub.set_heartbeat(6)

    def add_subscription(self, channel, function, update_function):
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
        self.update_funcs.append(update_function)

    def subscribe(self):
        """
        Start the subscription to the channel list.
        """
        self.pubnub.subscribe(self.channels, self.pub_callback)
        threading.Timer(30, self.manual_resub).start()
        #threading.Timer(120, self.resubscribe).start()

    def resubscribe(self):
        """
        Unsubscribe and resubscribe from the channel list.
        """
        threading.Timer(120, self.resubscribe).start()
        self.unsubscribe()
        sleep_thread = threading.Thread(target=self.sleep_thread)
        sleep_thread.start()

    def sleep_thread(self):
        time.sleep(30)
        self.subscribe()

    def manual_resub(self):
        if os.path.isfile("/home/pi/pubnub.txt"):
            self.resubscribe()
        threading.Timer(30, self.manual_resub).start()

    def unsubscribe(self):
        """
        Stop the subscription to the channel list.
        """
        csv_channels = ",".join(self.channels)
        self.pubnub.unsubscribe(channel=csv_channels)

    def pub_callback(self, message, channel):
        """
        Called when a new message is recevied on one of the subscribed
        to channels.
        Proccess the message and if it is new update the channels current data.
        If the data is new, also call the channels callback function.
        """
        sys.stdout.write("\n\nPubnub callback was called!\n\n")
        if 'data' in message:
            json_data = json.dumps(message.get('data'))
        else:
            json_data = message
        for func in self.subscriptions[channel]:
            if self.current_data[channel] != json_data:
                func(json.loads(json_data))
        self.current_data[channel] = json_data
