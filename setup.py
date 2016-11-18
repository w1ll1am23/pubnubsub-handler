from setuptools import setup, find_packages

setup(
    name='pubnubsub-handler',
    version='0.0.2',
    description='Handles the PubNub subscriptions between PubNub and Home-Assistant',
    author='William Scanlon',
    py_modules=['pubnubsubhandler'],
    license='MIT',
    classifiers=(
        'Programming Language :: Python',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    install_requires=[
        'pycryptodomex>=3.3',
        'requests>=2.4',
        'pubnub==4.0.1'
    ],
    zip_safe=False,
)
