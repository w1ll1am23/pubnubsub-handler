from setuptools import setup, find_packages

setup(
    name='pywinksub',
    version='0.0.1',
    description='Handles the PubNub subscription between PubNub and Home-Assistant',
    author='William Scanlon',
    py_modules=['pubnub'],
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
        'pubnub==4.0.0'
    ],
    zip_safe=False,
)
