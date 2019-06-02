"""
Handle the subscriptions responses between PubNub and another program.
"""

import json
import threading
import logging

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.enums import PNOperationType, PNStatusCategory, \
                         PNReconnectionPolicy
from pubnub.callbacks import SubscribeCallback


SUBSCRIPTIONS = {}
CHANNELS = []
CHANNEL_LISTS = []

_LOGGER = logging.getLogger(__name__)

class PubNubSubscriptionHandler():
    """
    Connection handler for PubNub Subscriptions.
    """

    def __init__(self, sub_key, keep_alive_function=None, keep_alive=3600,
                 sub_delay=60, origin=None):
        """
        Create the PubNub connection object.

        Args:
            sub_key (str): The PubNub Subscription key to use.
            keep_alive_function (func, optional): If provided will be run
                every keep_alive seconds. Use if something needs run to
                keep your PubNub updates flowing. Defaults to None.
                Example: For Wink subscriptions the Wink API needs polled
                occasionally to keep updates flowing from PubNub.
            keep_alive (int, optional): How often to run the keep_alive_function
                in seconds. Defaults to 3600 (1 hour)
            sub_delay (int, optional): How long to delay the call to subscribe.
                Defaults to 1 second. (No delay)
        """
        logging.getLogger('pubnub').setLevel(logging.CRITICAL)
        self._sub_key = sub_key
        self._pnconfig = PNConfiguration()
        if origin is not None:
            self._pnconfig.origin = origin
        self._pnconfig.non_subscribe_request_timeout = 30
        self._pnconfig.reconnect_policy = PNReconnectionPolicy.EXPONENTIAL
        self._pnconfig.subscribe_key = sub_key
        self._pnconfig.ssl = True
        self._pubnubs = []
        self._listener = PubNubSubCallback()
        self._keep_alive_function = keep_alive_function
        self._keep_alive = keep_alive
        self._subscribed = False
        self._subscription_delay = sub_delay

    def add_subscription(self, channel, callback_function):
        """
        Add a channel to subscribe to and a callback function to
        run when the channel receives an update.
        If channel already exists, create a new "subscription"
        and append another callback function.

        Args:
            channel (str): The channel to add a subscription too.
            callback_function (func): The function to run on an
                update to the passed in channel.
        """
        if channel not in CHANNELS:
            CHANNELS.append(channel)
            SUBSCRIPTIONS[channel] = [callback_function]
        else:
            SUBSCRIPTIONS[channel].append(callback_function)
        # If a channel gets added after subscription has already been called
        # call subscribe on the individual channel, here.
        if self._subscribed:
            _LOGGER.info("New channel added after main subscribe call.")
            self._pubnubs[0].subscribe().channels(channel).execute()

    def subscribe(self):
        """
        Call the real subscribe method in self._subscription_delay seconds.
        This give the calling program more time to add devices to keep the
        TCP connections to a minimum.
        """
        threading.Timer(self._subscription_delay, self._subscribe).start()

    def _run_keep_alive(self):
        """
        Start a new thread timer to keep the keep_alive_function running
        every keep_alive seconds.
        """
        threading.Timer(self._keep_alive, self._run_keep_alive).start()
        _LOGGER.info("Polling the API")
        # This may or may not return something
        self._keep_alive_function()

    def unsubscribe(self):
        """
        Completly stop all pubnub operations.
        """
        _LOGGER.info("PubNub unsubscribing")
        for pubnub in self.pubnubs:
            pubnub.unsubscribe_all()
            pubnub.stop()
            pubnub = None
        self.pubnubs.clear()

    def _subscribe(self):
        """
        Start the subscription to the channel list.
        If self._keep_alive_function isn't None start timer thread to
        run self._keep_alive_function every self._keep_alive amount of seconds.
        """
        _LOGGER.info("PubNub subscribing")
        CHANNEL_LISTS = [CHANNELS[x:x+50] for x in range(0, len(CHANNELS), 50)]
        for channel_list in CHANNEL_LISTS:
            self._pubnubs.append(PubNub(self._pnconfig))
            self._pubnubs[-1].add_listener(self._listener)
            self._pubnubs[-1].subscribe().channels(channel_list).execute()
        if len(self_pubnubs) == 0:
            self._pubnubs.append(PubNub(self._pnconfig))
            self._pubnubs[-1].add_listener(self._listener)
        if self._keep_alive_function is not None:
            threading.Timer(self._keep_alive, self._run_keep_alive).start()
        self._subscribed = True


class PubNubSubCallback(SubscribeCallback):
    """
    PubNub Callback handler.
    """

    def status(self, pubnub, status):
        """
        Things to do on different status updates.
        """
        if status.operation == PNOperationType.PNSubscribeOperation \
            or status.operation == PNOperationType.PNUnsubscribeOperation:
            if status.category == PNStatusCategory.PNConnectedCategory:
                # This is expected for a subscribe, this means there is no error or issue whatsoever
                _LOGGER.debug("PubNub connected")
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                # This usually occurs if subscribe temporarily fails but reconnects. This means
                # there was an error but there is no longer any issue
                _LOGGER.debug("PubNub reconnected")
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                # This is the expected category for an unsubscribe. This means there
                # was no error in unsubscribing from everything
                _LOGGER.debug("PubNub unsubscribed")
            elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                # This is usually an issue with the internet connection, this is an error, handle appropriately
                # retry will be called automatically
                _LOGGER.debug("PubNub disconnected (lost internet?)")
            else:
                # This is usually an issue with the internet connection, this is an error, handle appropriately
                # retry will be called automatically
                _LOGGER.debug("PubNub disconnected (lost internet?)")
        elif status.operation == PNOperationType.PNHeartbeatOperation:
            # Heartbeat operations can in fact have errors, so it is important to check first for an error.
            # For more information on how to configure heartbeat notifications through the status
            # PNObjectEventListener callback, consult <link to the PNCONFIGURATION heartbeart config>
            if status.is_error():
                # There was an error with the heartbeat operation, handle here
                _LOGGER.debug("PubNub failed heartbeat")
            else:
                # Heartbeat operation was successful
                _LOGGER.debug("PubNub heartbeat")
        else:
            pass

    def presence(self, pubnub, presence):
        """
        Don't currently support anything presence operations
        """
        return

    def message(self, pubnub, message):
        """
        Called when a new message is recevied on one of the subscribed
        to channels.
        Proccess the message and call the channels callback function(s).
        """
        try:
            json_data = json.dumps(message.message.get('data'))
        except AttributeError:
            json_data = message.message
        for func in SUBSCRIPTIONS[message.channel]:
            # This means pubnub couldn't get the current state of the channel
            # The pull_url is the location to pull the current state from.
            # Returning None here to have the calling program handle this.
            if 'pull_url' in json_data:
                func(None)
            else:
                func(json.loads(json_data))
