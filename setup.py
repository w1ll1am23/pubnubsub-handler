from setuptools import setup, find_packages

setup(
    name='pubnubsub-handler',
    version='1.0.1',
    description='Handles the PubNub subscriptions between PubNub and Home-Assistant for Wink',
    url='https://github.com/w1ll1am23/pubnubsub-handler',
    author='William Scanlon',
    py_modules=['pubnubsubhandler'],
    license='MIT',
    install_requires=[
        'pycryptodomex>=3.3',
        'requests>=2.4',
        'pubnub==4.0.5'
    ],
    zip_safe=True
)
