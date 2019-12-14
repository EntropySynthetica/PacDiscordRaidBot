import os
import discord
import re
from datetime import datetime
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
create_edit_trial_role = os.getenv('CREATE_EDIT_TRIAL_ROLE')

client = discord.Client()

unsignup_emoji = '🛑'

#Help menu to send to people who DM the bot. 
pacBotHelpPage = f"""
Pacrooti Bot Commands

This bot creates a roster for where folks can sign up for guild trial events.  

- To sign up for a role in a trial click the emoji on the roster for the role you want to go as.  If you click the same
emoji twice you will be put on the backup roster for that role. 
Tank Emoji = {tank_emoji}
Healer Emoji = {heal_emoji}
Stam DPS Emoji = {stamdps_emoji}
Mag DPS Emoji = {magdps_emoji}
Unsignup from Roster Emoji = {unsignup_emoji}

- To create a new trial (requires perms) type the following in the channel you want to the roster to post in. 
!NewTrial <number of tanks> <number of healers> <number of DPS> <Name and description of trial>

Example to create a trial with 1 tank 2 healers and 9 DPS: 
**!NewTrial 1 2 9 Friday Night Trial with Pacbot**

- To add someone to a trial roster (requires perms)
!AddtoTrial <TrialID> @Users Discord Name <emoji for role>

Example to add a user named someome to an existing trial as a healer with an ID of 123456
**!AddtoTrial 123456 @Someone {heal_emoji}**

- You can remove someone from the trial by using the !AddtoTrial command with the {unsignup_emoji} emoji.

Example to remove a user named someone from trial 123456
**!AddtoTrial 123456 @Someone {unsignup_emoji}**

"""
#Function to update the trial roster when people react to emoji, or the !AddtoTrial command is called
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

    #Check if user is already signed up, if so and they sign up again lets put them on the backup roster. 
    makeBackupTank = False
    makeBackupHealer = False
    makeBackupDPS = False

    for index, value in enumerate(tanks_signedup):
        if str(member_to_signup) in value:
            tanks_signedup[index] = "Open"
            makeBackupTank = True

    for index, value in enumerate(healer_signedup):
        if str(member_to_signup) in value:
            healer_signedup[index] = "Open"
            makeBackupHealer = True

    for index, value in enumerate(DPS_signedup):
        if str(member_to_signup) in value:
            DPS_signedup[index] = "Open"
            makeBackupDPS = True

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
        if (value == "Open") and ((tankspotfound == False) and (makeBackupTank == False)) and (chosen_role == "tank"):
            usersigned_up = (f'{member_to_signup} {role_emote}')
            tanks_signedup[index] = usersigned_up
            tankspotfound = True

    tank_header = ""
    for index, value in enumerate(tanks_signedup):
        index = index + 1
        tank_header = tank_header + "Tank" + str(index) + "=" + value +"\n"
    
    #If the roster is full lets add them to the backup list.
    if ((tankrosterfull == True) and (chosen_role == "tank")) or ((makeBackupTank == True) and (chosen_role == "tank")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')


    #Add user to the healer roster if they clicked healer emoji
    healerspotfound = False
    for index, value in enumerate(healer_signedup):
        if (value == "Open") and ((healerspotfound == False) and (makeBackupHealer == False)) and (chosen_role == "healer"):
            usersigned_up = (f'{member_to_signup} {heal_emoji}')
            healer_signedup[index] = usersigned_up
            healerspotfound = True

    healer_header = ""
    for index, value in enumerate(healer_signedup):
        index = index + 1
        healer_header = healer_header + "Healer" + str(index) + "=" + value +"\n"

    if ((healerrosterfull == True) and (chosen_role == "healer")) or ((makeBackupHealer == True) and (chosen_role == "healer")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    #Add user to the DPS roster if they clicked stam or mag DPS emoji
    DPSspotfound = False
    for index, value in enumerate(DPS_signedup):
        if (value == "Open") and ((DPSspotfound == False) and (makeBackupDPS == False)) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
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

    if (DPSrosterfull == True) and ((chosen_role == "magdps") or (chosen_role == "stamdps")) or (makeBackupDPS == True) and ((chosen_role == "magdps") or (chosen_role == "stamdps")):
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

def timestamp():
    now = datetime.now()
    timestamp = now.strftime("%m/%d/%Y, %H:%M:%S")
    return timestamp

#Connect the Client to Discord and report back.
@client.event
async def on_ready():
    print(f'{timestamp()}, {client.user} has connected to {client.guilds} Discord')

#Watch messages on the Discord server for commands the bot cares about. 
@client.event
async def on_message(message):
    #Check if the message author has the Correct Role to Edit and Create Trial rosters Ignore messages that are DMs or from the Bot
    if message.guild != None and message.author != client.user:
        if create_edit_trial_role in [role.name for role in message.author.roles]:
            userHasPerms = True
        else:
            userHasPerms = False

    #Print to log the message if it isn't from the bot. 
    if message.author != client.user:
        print(f'{timestamp()}, Channel={message.channel}, Author={message.author}, Message={message.content}')

    #If the message is from the bot lets do nothing. 
    if message.author == client.user:
        print(f'{timestamp()}, Message from bot, ignoring.')
        return

    #If the message is not from a discord server (aka guild) then it's a DM to the bot.  Let's respond with the help page for the bot. 
    elif message.guild is None and message.author != client.user:

        channel = await message.author.create_dm()

        await channel.send(pacBotHelpPage)

        print(f'{timestamp()}, Responded to {message.author} with help page.')

    #If someone typed the command !NewTrial If no arguments were passed we create a default trial of 2 2 8. Trial title is optional
    elif message.content.startswith('!NewTrial'):
        if userHasPerms == False:
            errorMSG = "You don't have the correct role to create or edit a trial roster"
            channel = await message.author.create_dm()
            await channel.send(errorMSG)
            print(f'{timestamp()}, {message.author} tried to create a new trial but does not have the role {create_edit_trial_role}.')
            return

        #Regular expression to parse out the arguments after the command.  
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

        print(f'{timestamp()}, Created a trial with {str(tank_count)} Tanks, {str(healer_count)} Healers, and {str(dps_count)} DPS named {trial_title} in channel {message.channel}')

    elif message.content.startswith('!AddtoTrial'):
        if userHasPerms == False:
            errorMSG = "You don't have the correct role to create or edit a trial roster"
            channel = await message.author.create_dm()
            await channel.send(errorMSG)
            print(f'{timestamp()}, {message.author} tried to add/remove someone from trial but does not have the role {create_edit_trial_role}.')
            return
        
        AddtoTrial_rex = r'\!AddtoTrial\s(?P<trialid>\d{6})\s*(?P<member_to_signup>\<\@.*?\>)\s*(?P<role_emote>.*)(?:\s|$)'
        AddtoTrialVars = re.search(AddtoTrial_rex, message.content)

        if AddtoTrialVars:
            trialid = AddtoTrialVars.group('trialid')
            member_to_signup = AddtoTrialVars.group('member_to_signup')
            role_emote = AddtoTrialVars.group('role_emote')
            
            member_to_signup = member_to_signup.replace('!', '')

            trialid_found = False
            async for trial_message in message.channel.history():
                
                #Search the message for a Trial ID
                trialid_rex = r'TrialID\=(\d{6})'
                trialid_message = re.findall(trialid_rex, trial_message.content)

                if trialid_message:

                    if trialid_message[0] == trialid:
                        edited_message = updateTrialRoster(trial_message, member_to_signup, role_emote)
                        await trial_message.edit(content=edited_message)

                        trialid_found = True
                        print(f'{timestamp()}, {message.author} used addtotrial {role_emote} {member_to_signup} to trial {trialid}.')

            if trialid_found == False:
                print(f'{timestamp()}, {message.author} Addtotrial error, {trialid} not found.')


        else:
            print(f'{timestamp()}, {message.author} Addtotrial error, Message syntax invalid.')
            return

    #Todo: Bot Help message to be DMed to person who types the command. 
    elif message.content.startswith('!PacBotHelp'):
        return

#Watch for a emoji reaction on our trial roster post. 
@client.event
async def on_raw_reaction_add(reaction):
    if reaction.user_id == client.user.id:
        return

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)


        #Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):

            member_to_signup = (f'<@{reaction.user_id}>')

            edited_message = updateTrialRoster(message, member_to_signup, reaction.emoji)

            await message.edit(content=edited_message)

            print(f'{timestamp()}, {member_to_signup} clicked the {reaction.emoji} emoji.')

        else:
            return    

@client.event
async def on_raw_reaction_remove(reaction):
    if reaction.user_id == client.user.id:
        return

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)


        #Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):

            member_to_signup = (f'<@{reaction.user_id}>')

            edited_message = updateTrialRoster(message, member_to_signup, reaction.emoji)

            await message.edit(content=edited_message)

            print(f'{timestamp()}, {member_to_signup} un-clicked the {reaction.emoji} emoji.')

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

    print(f'{timestamp()}, The bot welcomed {welcome_member} to the guild.')


client.run(token)