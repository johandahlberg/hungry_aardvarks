Hungry Aardvarks - A podcast annotation app prototype
=====================================================

A prototype for a podcast annotation app built for the [Hackup](http://hackup.se/) Hackaton in Uppsala in November 2015. The goal of the hackaton was to try out the IBM Watson API's and it was a tons of fun. And with the prototype we made it in to the finals - even if we didn't win.

This app was built by the Hungry Aardvarks team: [@ambarrio](https://github.com/ambarrio), [@hussius](https://github.com/hussius), and [@johandahlberg](https://github.com/johandahlberg).

Trying it out
-------------

To get this running you need to have a username and api-keys for the Watson Speech-to-text and Alchemy API's. You can get those by registering for IBM BlueMix at https://console.eu-gb.bluemix.net/catalog/.

Insert your own values at the top of the the app.py file:

    S2T_USERNAME="<YOUR SPEECH2TEXT USER>"
    S2T_PASSWD="<YOUR SPEECH2TEXT PASSWORD>"
    ALCHEMY_KEY = "<YOUR ALCHEMY API KEY>"
        
You also need to have tornado and mutagen installed as well as some commandline utils, use this to get them:

    pip install mutagen
    pip install tornado
    sudo apt-get install quelcom soundconverter

You then start the App by running:

  python app.py

You'll now have a web server running and listening on port 8888. And you can go to `localhost:8888/static/index.html` in your browser to see a very rudimentary UI, or start using the `/insight` end-point directly.

Licence
-------
MIT
