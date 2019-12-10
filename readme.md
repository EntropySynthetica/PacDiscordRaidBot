# Pacrooti's Discord Bot

This bot is built to provide services to the guild Discord of Pacrooti's Hirelings in the MMORPG Elder Scrolls Online. 

Currently this Bot has two functions, and more may be added later.  

1. Provides a welcome message and assigns the citizen rank when people join the server. 

2. Allows Trial leads to post a roster and let people sign up by reacting to emoji on the roster. 

This trial roster features of this bot was inspired by a private bot written by Kyzeragon. 

## Bot Usage

Sending a DM message to the bot will cause it to reply with a help menu.  

To create a new event use the command `!NewTrial` followed by the number of open Tank spots, healer spots, DPS spots, and the Trial title. 

For example, to create a Vet Atherian Archvie trial signup for 2 Tanks, 2 Healers and 8 DPS you would type the following,

`!NewTrial 2 2 8 Vet Atherian Archive Trial signups`

If you type `!NewTrial` with no arguments it will default to a 2 tank, 2 healer, 2 DPS trial with a generic name. 

To sign up for a spot someone simply needs to click the reaction emoji of the role they want.  If they click multiple emoji the system will sign them up for the last role that they clicked.  The stop sign emoji will remove them from the signup.  

To delete a signup just delete the post via discord.  This may require admin perms on the channel. 

Someone can be manually added or removed from a trial with the command ```!AddtoTrial```

To use this type a message that starts with that command followed by the trial ID number, @ message of the person to add or remove, and the appropriate role emoji.  Use the stop sign emoji to remove someone. 

## Running the Bot

The bot requires python 3.7 or newer, and the discord.py python library.  The bot must be running on a system 24/7 to monitor a discord server.  The bot is fairly small, so it can be run on something as simple as a Raspberry Pi.  

The bot requires a Discord API Key to connect properly.  The instructions to obtain the API key can be found in this article. https://realpython.com/how-to-make-a-discord-bot-python/

There is a file included in this repo named .env.example  You need to rename this file to .env and put your key into that file, along with the ID of the emoji you wish to use for each role.  The example file contains the IDs for the Emoji on my test server and will not work on a different server, so make sure to update these. 


I have included a Dockerfile to run the bot within a docker container.  Using this method the bot can easily be ran from any OS.

To build the application into a docker image run the following within the directory of the application. 

```docker build -t discordbot .```

Start a container from the image with the following.

```docker run -d --name discordbot discordbot```

## New Features

12/08/19 - Sending a DM to the bot will cause it to respond with a help message.  Bot commands will only work from someone with the appropriate role in the discord server. A person issuing commands without the correct role will get DM from the bot with an error message.

## Todo
* Bugfix: If someone comments on the discord channel before the bot can add the reaction emoji to a new trial post the emoji could go onto the wrong post. 

* Bugfix: If two people sign up at almost the same time (within a few seconds of each other) it is possible the bot will not add the first person who signed up to the roster. 

* Add the ability for overflow backups to get a spot on the main roster if someone drops from the roster. 
