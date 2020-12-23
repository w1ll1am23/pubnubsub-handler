# Change Log

## 1.0.9
- Fixed reference to _pubnub

## 1.0.8
- Fixed a typo :(

## 1.0.7
- Change the subscription delay to 60 seconds

## 1.0.6
- Change the channel splitting from 3 to 50 

## 1.0.5
- Create a new pubnub instance for every 50 channels, delay subscirption for 60 seconds, and set pubnub logging to critical by default

## 1.0.4
- Allow subscription URL to be passed in

## 1.0.2
- Update to pubnub 4.0.10

## 1.0.1
- Check for "'data':" not "data"

## 1.0.0
- Code reviewed by pubnub team, corrected reconnect policy.

## 0.0.7
- Updated to pubnub 4.0.5

## 0.0.6
- Updated to pubnub 4.0.4 and added automatic reconnects

## 0.0.5
- Made sleep before subscription optional.

## 0.0.4
- Updated pubnub version.

## 0.0.3
- Delayed subscribe call with support for adding channels after main subscribe call is made.

## 0.0.2
- Add support for running a keep alive function.

## 0.0.1
- Initial support for handling PubNub Wink subscriptions.
