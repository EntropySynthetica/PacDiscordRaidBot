import os
import discord
import re
from discord.ext import commands
from dotenv import load_dotenv
from random import randint

load_dotenv()

#Load Vars from .env
token = os.getenv('DISCORD_TOKEN')
tank_emoji = os.getenv('TANK_EMOJI')
heal_emoji = os.getenv('HEAL_EMOJI')
magdps_emoji = os.getenv('MAGDPS_EMOJI')
stamdps_emoji = os.getenv('STAMDPS_EMOJI')
welcome_channel_name = os.getenv('WELCOME_CHANNEL_NAME')
welcome_role_name = os.getenv('WELCOME_ROLE_NAME')

client = discord.Client()

unsignup_emoji = '🛑'


def updateTrialRoster(trial_message, member_to_signup, role_emote):

    #This function is called when we need to update the trial roster with someone signing up or being removed. 

    if str(role_emote) == tank_emoji:
        chosen_role = "tank"
    elif str(role_emote) == heal_emoji:
        chosen_role = "healer"
    elif str(role_emote) == magdps_emoji:
        chosen_role = "magdps"
    elif str(role_emote) == stamdps_emoji:
        chosen_role = "stamdps"
    elif str(role_emote) == unsignup_emoji:
        chosen_role = "unsignup"
    else:
        print('Emoji = ' + str(role_emote))
        chosen_role = "None"
        return

    #Parse the title of the trial. 
    title_rex = r'has\sposted\s(.*)'
    trial_title = re.findall(title_rex, trial_message.content)

    title_header = "Pac's Raid Signup Bot has posted " + trial_title[0] + "\n"

    instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {tank_emoji}\nHealer = {heal_emoji}\nMagDPS = {magdps_emoji}\nStamDPS = {stamdps_emoji}\nUnSignup = {unsignup_emoji}\n")

    #Parse Roster of folks already signed up. 
    tank_rex = r'Tank\d\=(.*)'
    tanks_signedup = re.findall(tank_rex, trial_message.content)

    healer_rex = r'Healer\d\=(.*)'
    healer_signedup = re.findall(healer_rex, trial_message.content)

    DPS_rex = r'DPS\d\=(.*)'
    DPS_signedup = re.findall(DPS_rex, trial_message.content)

    backup_rex = r'Backup\d\=(.*)'
    backup_signedup = re.findall(backup_rex, trial_message.content)

    #Parse the Trial ID
    trialid_rex = r'TrialID\=(\d{6})'
    trialid = re.findall(trialid_rex, trial_message.content)

    #If the trial does not have an ID lets give it one. This enables new features to work with old rosters 
    if not trialid:
        trialid = []
        trialid.append(''.join(["{}".format(randint(0, 9)) for num in range(0, 6)]))

    #Check if user is already signed up, if so lets remove their old entry to prevent multiple signups. 
    for index, value in enumerate(tanks_signedup):
        if str(member_to_signup) in value:
            tanks_signedup[index] = "Open"

    for index, value in enumerate(healer_signedup):
        if str(member_to_signup) in value:
            healer_signedup[index] = "Open"

    for index, value in enumerate(DPS_signedup):
        if str(member_to_signup) in value:
            DPS_signedup[index] = "Open"

    for index, value in enumerate(backup_signedup):
        if str(member_to_signup) in value:
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
            usersigned_up = (f'{member_to_signup} {role_emote}')
            tanks_signedup[index] = usersigned_up
            tankspotfound = True

    tank_header = ""
    for index, value in enumerate(tanks_signedup):
        index = index + 1
        tank_header = tank_header + "Tank" + str(index) + "=" + value +"\n"
    
    #If the roster is full lets add them to the backup list.
    if (tankrosterfull == True) and (chosen_role == "tank"):
        backup_signedup.append(f'{member_to_signup} {role_emote}')


    #Add user to the healer roster if they clicked healer emoji
    healerspotfound = False
    for index, value in enumerate(healer_signedup):
        if (value == "Open") and (healerspotfound == False) and (chosen_role == "healer"):
            usersigned_up = (f'{member_to_signup} {heal_emoji}')
            healer_signedup[index] = usersigned_up
            healerspotfound = True

    healer_header = ""
    for index, value in enumerate(healer_signedup):
        index = index + 1
        healer_header = healer_header + "Healer" + str(index) + "=" + value +"\n"

    if (healerrosterfull == True) and (chosen_role == "healer"):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    #Add user to the DPS roster if they clicked stam or mag DPS emoji
    DPSspotfound = False
    for index, value in enumerate(DPS_signedup):
        if (value == "Open") and (DPSspotfound == False) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
            if chosen_role == "magdps":
                dps_emoji = magdps_emoji
            elif chosen_role == "stamdps":
                dps_emoji = stamdps_emoji

            usersigned_up = (f'{member_to_signup} {dps_emoji}')
            DPS_signedup[index] = usersigned_up
            DPSspotfound = True

    DPS_header = ""
    for index, value in enumerate(DPS_signedup):
        index = index + 1
        DPS_header = DPS_header + "DPS" + str(index) + "=" + value +"\n"

    if (DPSrosterfull == True) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    #Add users to Backup Roster if something was full.
    backup_header = ""
    for index, value in enumerate(backup_signedup):
        index = index + 1
        backup_header = backup_header + "Backup" + str(index) + "=" + value +"\n"

    #Add in the TrialID
    trialid_header = ("TrialID=" + str(trialid[0])) 


    edited_message = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + DPS_header + "\n" + backup_header + "\n" + trialid_header
    
    return edited_message
    #Update our post with the new roster
    #await trial_message.edit(content=edited_message)


#Connect the Client to Discord and report back.
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#Watch for the !NewTrial string at the begining.
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('!NewTrial'):
        #Regular expression to parse out the arguments after the command.  If no arguments were passed we create a default trial of 2 2 8. Trial title is optional
        NewTrialRex = r'\!NewTrial\s(?P<tank>\d{1,2})\s(?P<healer>\d{1,2})\s(?P<DPS>\d{1,2})(?:\s|)(?P<Title>(?:.*|))'
        NewTrialVars = re.search(NewTrialRex, message.content)

        if NewTrialVars:
            tank_count = int(NewTrialVars.group('tank'))
            healer_count = int(NewTrialVars.group('healer'))
            dps_count = int(NewTrialVars.group('DPS'))
            trial_title = NewTrialVars.group('Title')

            #Lets limit the max spots for any role to 20 so we don't overrun the max Discord message length
            if tank_count > 20:
                tank_count = 20

            if healer_count > 20:
                healer_count = 20

            if dps_count > 20:
                dps_count = 20

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

        # Assign the Trial an ID number so we can reference it later. 
        trialid = ''.join(["{}".format(randint(0, 9)) for num in range(0, 6)])

        trialid_header = ("TrialID=" + str(trialid)) 

        response = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + dps_header + "\n" + trialid_header

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

    elif message.content.startswith('!AddtoTrial'):

        print(str(message.content))

        AddtoTrial_rex = r'\!AddtoTrial\s(?P<trialid>\d{6})\s*(?P<member_to_signup>\<\@.*?\>)\s*(?P<role_emote>.*)(?:\s|$)'
        AddtoTrialVars = re.search(AddtoTrial_rex, message.content)

        if AddtoTrialVars:
            trialid = AddtoTrialVars.group('trialid')
            member_to_signup = AddtoTrialVars.group('member_to_signup')
            role_emote = AddtoTrialVars.group('role_emote')
            
            member_to_signup = member_to_signup.replace('!', '')

            print(trialid)
            print(member_to_signup)
            print(role_emote)

            async for trial_message in message.channel.history():
                
                #Search the message for a Trial ID
                trialid_rex = r'TrialID\=(\d{6})'
                trialid_message = re.findall(trialid_rex, trial_message.content)

                if trialid_message:

                    if trialid_message[0] == trialid:
                        print(str(trial_message.id))

                        edited_message = updateTrialRoster(trial_message, member_to_signup, role_emote)

                        await trial_message.edit(content=edited_message)

        else:
            return



#Watch for a emoji reaction on our trial post. 
@client.event
async def on_raw_reaction_add(reaction):
    if reaction.user_id == client.user.id:
        return

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)


        #Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):

            member_to_signup = (f'<@{reaction.user_id}>')

            #print(message)
            print(member_to_signup)
            print(reaction.emoji)

            edited_message = updateTrialRoster(message, member_to_signup, reaction.emoji)

            await message.edit(content=edited_message)

        else:
            return    

#Print Welcome Message and Assign a Role when someone joins the discord. 
@client.event
async def on_member_join(member):
    print(member.name + " has joined " + str(member.guild))

    role = discord.utils.get(member.guild.roles, name=welcome_role_name)
    channel = discord.utils.get(client.get_all_channels(), name=welcome_channel_name)

    welcome_member = f'<@{member.id}>'

    welcome_message = "This one welcomes " + welcome_member + " to " + str(member.guild) + ".  Please change your discord nickname to match your ESO @ name."

    await member.add_roles(role)
    await channel.send(welcome_message)


client.run(token)