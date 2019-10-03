import os
import discord
import re
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

tank_emoji = '<:tank:628405354996432936>'
heal_emoji = '<:healer:628405417042509899>'
magdps_emoji = '<:magdps:628405402358251520>'
stamdps_emoji = '<:stamdps:628405386168369153>'

# tank_emoji = '<:tank:628734674402934804>'
# heal_emoji = '<:healer:628734751024480287>'
# magdps_emoji = '<:magdps:628734734637465642>'
# stamdps_emoji = '<:stamdps:628734719831310337>'
unsignup_emoji = '🛑'

#Connect the Client to Discord and report back.
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#Watch for the !NewTrial string at the begining.
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!NewTrial'):


        #Regular expression to parse out the arguments after the command.  If no arguments were passed we create a default trial of 2 2 8. 
        NewTrialRex = r'\!NewTrial\s(?P<tank>\d)\s(?P<healer>\d)\s(?P<DPS>\d)\s(?P<Title>.*)'
        NewTrialVars = re.search(NewTrialRex, message.content)

        if NewTrialVars:
            tank_count = int(NewTrialVars.group('tank'))
            healer_count = int(NewTrialVars.group('healer'))
            dps_count = int(NewTrialVars.group('DPS'))
            trial_title = NewTrialVars.group('Title')
        else:
            tank_count = 2
            healer_count = 2
            dps_count = 8
            trial_title = "New Trial"

        #Debug block to see what vars were passed. 
        print('Tank Count = ' + str(tank_count))
        print('Healer Count = ' + str(healer_count))
        print('DPS Count = ' + str(dps_count))
        print('Trial title = ' + trial_title)

        #Create the intial trial post. 
        title_header = "Pac's Raid Signup Bot has posted " + trial_title + "\n"

        instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {tank_emoji}\nHealer = {heal_emoji}\nMagDPS = {magdps_emoji}\nStamDPS = {stamdps_emoji}\nUnSignup = {unsignup_emoji}\n")
        
        tank_header = ""
        for i in range(tank_count):
            i = i + 1
            tank_header = tank_header + "Tank" + str(i) + "=Open\n"

        healer_header = ""
        for i in range(healer_count):
            i = i + 1
            healer_header = healer_header + "Healer" + str(i) + "=Open\n"

        dps_header = ""
        for i in range(dps_count):
            i = i + 1
            dps_header = dps_header + "DPS" + str(i) + "=Open\n"

        response = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + dps_header

        #Post the Message in the same discord channel the command was run from. 
        await message.channel.send(response)


        #Grab the last message posted to discord. That should be what our bot just posted. We need it's ID so we can add the reaction emotes.
        async for last_message in message.channel.history(limit=1):
            #print(last_message)
            #print(last_message.content)
            #print('Last Message ID = ' + str(last_message.id))

            default_reactions = [tank_emoji,heal_emoji,stamdps_emoji,magdps_emoji,unsignup_emoji]
            for emoji in default_reactions:
                await last_message.add_reaction(emoji)

#Watch for a reaction on our trial post. 
@client.event
async def on_raw_reaction_add(reaction):
    if reaction.user_id == client.user.id:
        return

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)


        #Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):
            if str(reaction.emoji) == tank_emoji:
                chosen_role = "tank"
            elif str(reaction.emoji) == heal_emoji:
                chosen_role = "healer"
            elif str(reaction.emoji) == magdps_emoji:
                chosen_role = "magdps"
            elif str(reaction.emoji) == stamdps_emoji:
                chosen_role = "stamdps"
            elif str(reaction.emoji) == unsignup_emoji:
                chosen_role = "unsignup"
            else:
                print('Emoji = ' + str(reaction.emoji))
                chosen_role = "None"
                return

            #Debuging Print statements
            print('Emoji = ' + str(reaction.emoji))
            print('Emoji Channel ID = ' + str(reaction.channel_id))
            print('Emoji Message ID = ' + str(reaction.message_id))
            print('Emoji User ID = ' + str(reaction.user_id))
            print('Client User = ' + str(client.user.id))
            print("Chosen Role = " + chosen_role)

            #Parse the title of the trial. 
            title_rex = r'has\sposted\s(.*)'
            trial_title = re.findall(title_rex, message.content)

            title_header = "Pac's Raid Signup Bot has posted " + trial_title[0] + "\n"

            instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {tank_emoji}\nHealer = {heal_emoji}\nMagDPS = {magdps_emoji}\nStamDPS = {stamdps_emoji}\nUnSignup = {unsignup_emoji}\n")
  
            #Parse Roster of folks already signed up. 
            tank_rex = r'Tank\d\=(.*)'
            tanks_signedup = re.findall(tank_rex, message.content)

            healer_rex = r'Healer\d\=(.*)'
            healer_signedup = re.findall(healer_rex, message.content)

            DPS_rex = r'DPS\d\=(.*)'
            DPS_signedup = re.findall(DPS_rex, message.content)

            backup_rex = r'Backup\d\=(.*)'
            backup_signedup = re.findall(backup_rex, message.content)

            #Check if user is already signed up, if so lets remove their old entry to prevent multiple signups. 
            for index, value in enumerate(tanks_signedup):
                if str(reaction.user_id) in value:
                    tanks_signedup[index] = "Open"

            for index, value in enumerate(healer_signedup):
                if str(reaction.user_id) in value:
                    healer_signedup[index] = "Open"

            for index, value in enumerate(DPS_signedup):
                if str(reaction.user_id) in value:
                    DPS_signedup[index] = "Open"

            for index, value in enumerate(backup_signedup):
                if str(reaction.user_id) in value:
                    del backup_signedup[index]

            #Check if Rosters are full
            if "Open" not in tanks_signedup:
                tankrosterfull = True
            else:
                tankrosterfull = False

            if "Open" not in healer_signedup:
                healerrosterfull = True
            else:
                healerrosterfull = False

            if "Open" not in DPS_signedup:
                DPSrosterfull = True
            else: 
                DPSrosterfull = False

            #Add user to the Tank roster if they clicked tank emoji
            tankspotfound = False
            for index, value in enumerate(tanks_signedup):
                if (value == "Open") and (tankspotfound == False) and (chosen_role == "tank"):
                    usersigned_up = (f'<@{reaction.user_id}> {tank_emoji}')
                    tanks_signedup[index] = usersigned_up
                    tankspotfound = True

            tank_header = ""
            for index, value in enumerate(tanks_signedup):
                index = index + 1
                tank_header = tank_header + "Tank" + str(index) + "=" + value +"\n"
            
            #If the roster is full lets add them to the backup list.
            if (tankrosterfull == True) and (chosen_role == "tank"):
                backup_signedup.append(f'<@{reaction.user_id}> {reaction.emoji}')


            #Add user to the healer roster if they clicked healer emoji
            healerspotfound = False
            for index, value in enumerate(healer_signedup):
                if (value == "Open") and (healerspotfound == False) and (chosen_role == "healer"):
                    usersigned_up = (f'<@{reaction.user_id}> {heal_emoji}')
                    healer_signedup[index] = usersigned_up
                    healerspotfound = True

            healer_header = ""
            for index, value in enumerate(healer_signedup):
                index = index + 1
                healer_header = healer_header + "Healer" + str(index) + "=" + value +"\n"

            if (healerrosterfull == True) and (chosen_role == "healer"):
                backup_signedup.append(f'<@{reaction.user_id}> {reaction.emoji}')

            #Add user to the DPS roster if they clicked stam or mag DPS emoji
            DPSspotfound = False
            for index, value in enumerate(DPS_signedup):
                if (value == "Open") and (DPSspotfound == False) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
                    if chosen_role == "magdps":
                        dps_emoji = magdps_emoji
                    elif chosen_role == "stamdps":
                        dps_emoji = stamdps_emoji

                    usersigned_up = (f'<@{reaction.user_id}> {dps_emoji}')
                    DPS_signedup[index] = usersigned_up
                    DPSspotfound = True

            DPS_header = ""
            for index, value in enumerate(DPS_signedup):
                index = index + 1
                DPS_header = DPS_header + "DPS" + str(index) + "=" + value +"\n"

            if (DPSrosterfull == True) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
                backup_signedup.append(f'<@{reaction.user_id}> {reaction.emoji}')

            #Add users to Backup Roster if something was full.
            backup_header = ""
            for index, value in enumerate(backup_signedup):
                index = index + 1
                backup_header = backup_header + "Backup" + str(index) + "=" + value +"\n"


            edited_message = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + DPS_header + "\n" + backup_header
            #Update our post with the new roster
            await message.edit(content=edited_message)

        else:
            return    


client.run(token)