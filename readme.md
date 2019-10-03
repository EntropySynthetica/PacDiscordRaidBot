# Pac's Discord Raid Signup Bot

Pac's Discord Raid Signup Bot is intended to create and allow people to signup for Elder Scrolls Online Raids from a Discord Channel. I created this for the Guild Pacrooti's Hirelings in ESO.

## Bot Usage
To create a new event use the command `!NewTrial` followed by the number of open Tank spots, healer spots, DPS spots, and the Raid title. 

For example, to create a Vet Atherian Archvie trial signup for 2 Tanks, 2 Healers and 8 DPS you would type the following,

`!NewTrial 2 2 8 Vet Atherian Archive Trial signups`

If you type `!NewTrial` with no arguments it will default to a 2 tank, 2 healer, 2 DPS trial with a generic name. 

To sign up for a spot someone simply needs to click the reaction emoji of the role they want.  If they click multiple emoji the system will sign them up for the last role that they clicked.  The stop sign emoji will remove them from the signup.  

To delete a signup just delete the post via discord.  This may require admin perms on the channel. 

## Running the Bot

The bot requires python 3.7 or newer, and the discord.py python library.  The bot must be running on a system 24/7 to monitor a discord server.  The bot is fairly small, so it can be run on something as simple as a Raspberry Pi.  

The bot requires a Discord API Key to connect properly.  The instructions to obtain the API key can be found in this article. https://realpython.com/how-to-make-a-discord-bot-python/

There is a file included in this repo named .env.example  You need to rename this file to .env and put your key into that file, along with the ID of the emoji you wish to use for each role.  The example file contains the IDs for the Emoji on my test server and will not work on a different server, so make sure to update these. 


I have included a Dockerfile to run the bot within a docker container.  Using this method the bot can easily be ran from any OS.

To build the application into a docker image run the following within the directory of the application. 

```docker build -t discordbot .```

Start a container from the image with the following.

```docker run -d --name discordbot discordbot```

## Todo
* Add commands so a raid lead can manually add, remove, and move around people. 

* Add the ability for overflow backups to get a spot on the main roster if someone drops from the roster. 
