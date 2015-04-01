#Permit Bot

Permit Bot is a twitter bot for tweeting about Chicago building permits, using public data from the city data portal. You can see the [source data here](https://data.cityofchicago.org/Buildings/Building-Permits/ydr8-5enu) and [follow Permit Bot here](https://twitter.com/permitbot).

##What's happening here
Permit bot is basically a set of python functions, some Fabric and then a cron job that calls the fabfile. There is also some Duct Tape.

##How to setup Permit Bot
Twitter bots can be a number of things. Some tweet about earthquakes, home runs, or even do complicated things like tell you what public radio station is nearest to you.

Permit Bot is a very simple implementation that looks for permits at the city of Chicago data portal at scheduled times and then tweets if the permits meet certain requirements.

###Start a Twitter account
Go to [twitter.com](https://twitter.com) and open a new account. You'll need an email address that isn't attached to another account and a cell number (for later). You have to remove this number from any accounts it's already attached to, but you can add it back after this process.

###Create a twitter API key
Go to [apps.twitter.com](https://apps.twitter.com/) and start a new app. Once that's created, go to the permissions tab and make sure it's set to Read and Write.

The other thing you'll need from this screen is your API keys, available in the Keys and Access Tokens tab. We don't need them just yet, but keep them handy for the next step.

###Clone this repository
This is the part where you actually get this code.

From the main repository, use the Clone in Desktop or Download buttons to get the files to your computer. If you're familiar with git and github, you can [clone the repo like you would anything else](https://help.github.com/articles/importing-a-git-repository-using-the-command-line/) (and you probably know how to do this better than I do, so please submit some pull requests to improve this). Once you have everything, run `pip install -r requirements.txt` to install the needed packages, mainly Python-Twitter and Fabric.

The main thing you'll need to change is a file called config_template.py. This is the file that has all of the Twitter keys that will be used to call the API.

Rename the file to config.py and then add your information from the twitter Keys and Access Tokens tab where prompted:

```python
config = {
    'consumer_key':'YOUR_CONSUMER_KEY_HERE',
	'consumer_secret':'YOUR_CONSUMER_SECRET_HERE',
	'access_token_key':'YOUR_ACCESS_TOKEN_HERE',
	'access_token_secret':'YOUR_ACCESS_TOKEN_SECRET_HERE'
}
```

###Running the bot
There are a few ways to do this. 

You can run the project off your own machine. This isn't a problem if you only want to send our tweets occasionally or have a computer that's always on.

More likely you'll want to set this up on a server. I used space I have avaialble for personal projects. [Lauren Orsini wrote a similar piece using Heroku](http://readwrite.com/2014/06/20/random-non-sequitur-twitter-bot-instructions), which could be a better fit for your project.

All the code that interacts with the data portal and twitter lives in permitbot.py. Here are the functions and what they do:
- post_status(text): Takes text and posts it to twitter
- test_api(): Tests your connection to the twitter api
- get_data(limit=1000,offset=0, days=1): Gets data from the city of Chicago data portal.
- find_high(days=1): Parses building permit data to find any with an estimated cost greater than $500,000.
- get_summary(days=30): Parses building permit data to get a summary of permit costs for a given number of days.
- find_demo(days=1): Parses building permit data to find demolition permits
- add_id_to_file(id,file): Add a permit ID to a text file.
- duplicate_check(id,file): Check a text file to see if a given ID is in there.

The basic workflow is this:
* Call get_data to collect permits from a given time frame. The data portal api only returns 1,000 results at a time, so for anything more than that it iterates until all the permits are saved.
* Perform whatever function we're intersted in, such as looking for large permits or demolitions.
* If a permit matches our filters, check if its ID is in a text file we've started to track what permits we've tweeted about. If it is, we pass. If not, we tweet.

I used a python package called Fabric to help manage the actual sending of tweets. In fabfile.py you'll find a few simple functions that can be called from the command line and trigger Permit Bot.

To actually send tweets you'll need to schedule a cron job that calls the fabfile and the functions in permitbot.py. [Here's a good primer on how to do that](http://v1.corenominal.org/howto-setup-a-crontab-file/). 

This is what my crontab file looks like:

```
SHELL=/bin/bash
23 13-23 * * * cd /home/permitbot/ && source bin/activate && fab large_permits
47 16 * * * cd /home/permitbot/ && source bin/activate && fab demos:days=1
```

You can [read more about crons here](http://en.wikipedia.org/wiki/Cron). The command takes five time entries (minutes, hours, days, week, day of the week) from left to right. For example, I have jobs running on the 23rd and 47th minute every day. The first runs during specified hours (13-23, in GMT) and the other only once.

At the specified time the cron changes the directory to where Permit Bot code lives, start my virtual environment and calls a fabric command. That runs through the Permit Bot code, and tweets if any new permits are found. While it runs every hour, in practice tweets are only sent in the morning as the data is most often updated once a day.