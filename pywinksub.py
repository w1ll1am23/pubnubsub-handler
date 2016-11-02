"""
Handle the subscriptions responses between PubNub and Home-Assistant.
"""

import json
import threading
import time
import sys
import os
import datetime

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.pubnub import SubscribeCallback, PNOperationType, \
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
        self.sub_key = sub_key
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
        self.pubnub.subscribe().channels(CHANNELS).execute()
        threading.Timer(3600, self.resubscribe).start()

    def resubscribe(self):
        """
        Unsubscribe and resubscribe from the channel list.
        """
        threading.Timer(3600, self.resubscribe).start()
        self.pubnub.unsubscribe_all()
        sleep_thread = threading.Thread(target=self.sleep_thread)
        sleep_thread.start()

    def sleep_thread(self):
        time.sleep(120)
        self.pubnub.stop()
        self.pubnub = None
        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(PubNubWinkCallback())
        self.pubnub.subscribe().channels(CHANNELS).execute()


class PubNubWinkCallback(SubscribeCallback):
    """
    PubNub Callback handler.
    """

    def status(self, pubnub, status):
        """
        Things to do on different status updates.
        """
        with open('/home/pi/pubnub.log', 'a') as pub_log:
            pub_log.write("\n\n\n")
            pub_log.write(str(datetime.datetime.now()) + "\n")
            pub_log.write("\nStatus:\n")
            if status.operation == PNOperationType.PNSubscribeOperation \
                or status.operation == PNOperationType.PNUnsubscribeOperation:
                if status.category == PNStatusCategory.PNConnectedCategory:
                    pub_log.write("Connected\n")
                    # This is expected for a subscribe, this means there is no error or issue whatsoever
                elif status.category == PNStatusCategory.PNReconnectedCategory:
                    pub_log.write("Reconnected\n")
                    # This usually occurs if subscribe temporarily fails but reconnects. This means
                    # there was an error but there is no longer any issue
                elif status.category == PNStatusCategory.PNDisconnectedCategory:
                    pub_log.write("Unsubscribe success\n")
                    # This is the expected category for an unsubscribe. This means there
                    # was no error in unsubscribing from everything
                elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                    pub_log.write("Internet went down?\n")
                    # This is usually an issue with the internet connection, this is an error, handle appropriately
                    # retry will be called automatically
                else:
                    pub_log.write("Internet went down?\n")
                    # This is usually an issue with the internet connection, this is an error, handle appropriately
                    # retry will be called automatically
            elif status.operation == PNOperationType.PNHeartbeatOperation:
                # Heartbeat operations can in fact have errors, so it is important to check first for an error.
                # For more information on how to configure heartbeat notifications through the status
                # PNObjectEventListener callback, consult <link to the PNCONFIGURATION heartbeart config>
                if status.is_error():
                    # There was an error with the heartbeat operation, handle here
                    pub_log.write("Failed heartbeat\n")
                else:
                    pass
                    # Heartbeat operation was successful
            else:
                pass

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
        with open('/home/pi/pubnub.log', 'a') as pub_log:
            pub_log.write("\n\n\n")
            pub_log.write(str(datetime.datetime.now()) + "\n")
            if 'last_reading' not in json_data:
                pub_log.write("\nLast reading not in json\n")
            pub_log.write(json_data)
        for func in SUBSCRIPTIONS[message.subscribed_channel]:
            if CURRENT_DATA[message.subscribed_channel] != json_data:
                func(json.loads(json_data))
        CURRENT_DATA[message.subscribed_channel] = json_data
