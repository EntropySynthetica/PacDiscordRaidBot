"""
This bot is built to provide services to the guild Discord of Pacrooti's Hirelings in the MMORPG Elder Scrolls Online.
Currently this Bot has two functions, and more may be added later.

* Provides a welcome message and assigns the citizen rank when people join the server.
* Allows Trial leads to post a roster and let people sign up by reacting to emoji on the roster.
"""

import os
import re
from datetime import datetime
from random import randint
from dotenv import load_dotenv
import discord

load_dotenv()

# Load Vars from .env
TOKEN = os.getenv('DISCORD_TOKEN')
TANK_EMOJI = os.getenv('TANK_EMOJI')
HEAL_EMOJI = os.getenv('HEAL_EMOJI')
RANGED_EMOJI = os.getenv('RANGED_EMOJI')
MELEE_EMOJI = os.getenv('MELEE_EMOJI')
WELCOME_CHANNEL_NAME = os.getenv('WELCOME_CHANNEL_NAME')
WELCOME_ROLE_NAME = os.getenv('WELCOME_ROLE_NAME')
CREATE_EDIT_TRIAL_ROLE = os.getenv('CREATE_EDIT_TRIAL_ROLE')

client = discord.Client()  # pylint: disable=invalid-name

UNSIGNUP_EMOJI = '🛑'

# Help menu to send to people who DM the bot.
PAC_BOT_HELP_PAGE = f"""
Pacrooti Bot Commands

This bot creates a roster for where folks can sign up for guild trial events.

- To sign up for a role in a trial click the emoji on the roster for the role you want to go as.  If you click the same
emoji twice you will be put on the backup roster for that role.
Tank Emoji = {TANK_EMOJI}
Healer Emoji = {HEAL_EMOJI}
Melee DPS Emoji = {MELEE_EMOJI}
Ranged DPS Emoji = {RANGED_EMOJI}
Unsignup from Roster Emoji = {UNSIGNUP_EMOJI}

- To create a new trial (requires perms) type the following in the channel you want to the roster to post in.
!NewTrial <number of tanks> <number of healers> <number of DPS> <Name and description of trial>

Example to create a trial with 1 tank 2 healers and 9 DPS:
**!NewTrial 1 2 9 Friday Night Trial with Pacbot**

- To add someone to a trial roster (requires perms)
!AddtoTrial <TrialID> @Users Discord Name <emoji for role>

Example to add a user named someome to an existing trial as a healer with an ID of 123456
**!AddtoTrial 123456 @Someone {HEAL_EMOJI}**

- You can remove someone from the trial by using the !AddtoTrial command with the {UNSIGNUP_EMOJI} emoji.

Example to remove a user named someone from trial 123456
**!AddtoTrial 123456 @Someone {UNSIGNUP_EMOJI}**

"""


# Function to update the trial roster when people react to emoji, or the !AddtoTrial command is called.
def update_trial_roster(trial_message, member_to_signup, role_emote):
    """This function is called when we need to update the trial roster with someone signing up or being removed."""

    # Detect what kind of emoji the user reacted with and assign it to a role.  If we don't recognize the emoji set the role to none.
    if str(role_emote) == TANK_EMOJI:
        chosen_role = "tank"
    elif str(role_emote) == HEAL_EMOJI:
        chosen_role = "healer"
    elif str(role_emote) == RANGED_EMOJI:
        chosen_role = "rangeddps"
    elif str(role_emote) == MELEE_EMOJI:
        chosen_role = "meleedps"
    elif str(role_emote) == UNSIGNUP_EMOJI:
        chosen_role = "unsignup"
    else:
        chosen_role = "None"

    # Parse the title of the trial.
    title_rex = r'has\sposted\s(.*)'
    trial_title = re.findall(title_rex, trial_message.content)

    title_header = "Pac's Raid Signup Bot has posted " + trial_title[0] + "\n"

    instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {TANK_EMOJI}\nHealer = {HEAL_EMOJI}\nRangedDPS = {RANGED_EMOJI}\nMeleeDPS = {MELEE_EMOJI}\nUnSignup = {UNSIGNUP_EMOJI}\n")

    # Parse Roster of folks already signed up.
    tank_rex = r'Tank\d\=(.*)'
    tanks_signedup = re.findall(tank_rex, trial_message.content)

    healer_rex = r'Healer\d\=(.*)'
    healer_signedup = re.findall(healer_rex, trial_message.content)

    dps_rex = r'DPS\d\=(.*)'
    dps_signedup = re.findall(dps_rex, trial_message.content)

    backup_rex = r'Backup\d\=(.*)'
    backup_signedup = re.findall(backup_rex, trial_message.content)

    # Parse the Trial ID
    trialid_rex = r'TrialID\=(\d{6})'
    trialid = re.findall(trialid_rex, trial_message.content)

    # If the trial does not have an ID lets give it one. This enables new features to work with old rosters.
    if not trialid:
        trialid = []
        trialid.append(''.join(["{}".format(randint(0, 9)) for num in range(0, 6)]))

    # Check if user is already signed up, if so and they sign up again lets put them on the backup roster.
    make_backup_tank = False
    make_backup_healer = False
    make_backup_dps = False

    for index, value in enumerate(tanks_signedup):
        if str(member_to_signup) in value:
            tanks_signedup[index] = "Open"
            make_backup_tank = True

    for index, value in enumerate(healer_signedup):
        if str(member_to_signup) in value:
            healer_signedup[index] = "Open"
            make_backup_healer = True

    for index, value in enumerate(dps_signedup):
        if str(member_to_signup) in value:
            dps_signedup[index] = "Open"
            make_backup_dps = True

    for index, value in enumerate(backup_signedup):
        if str(member_to_signup) in value:
            del backup_signedup[index]

    # Check if Rosters are full.
    tank_roster_full = bool("Open" not in tanks_signedup)
    healer_roster_full = bool("Open" not in healer_signedup)
    dps_roster_full = bool("Open" not in dps_signedup)

    # Add user to the Tank roster if they clicked tank emoji.
    tankspotfound = False
    for index, value in enumerate(tanks_signedup):
        if (value == "Open") and ((tankspotfound is False) and (make_backup_tank is False)) and (chosen_role == "tank"):
            usersigned_up = (f'{member_to_signup} {role_emote}')
            tanks_signedup[index] = usersigned_up
            tankspotfound = True

    tank_header = ""
    for index, value in enumerate(tanks_signedup):
        index = index + 1
        tank_header = tank_header + "Tank" + str(index) + "=" + value + "\n"

    # If the roster is full lets add them to the backup list.
    if ((tank_roster_full is True) and (chosen_role == "tank")) or ((make_backup_tank is True) and (chosen_role == "tank")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    # Add user to the healer roster if they clicked healer emoji.
    healerspotfound = False
    for index, value in enumerate(healer_signedup):
        if (value == "Open") and ((healerspotfound is False) and (make_backup_healer is False)) and (chosen_role == "healer"):
            usersigned_up = (f'{member_to_signup} {HEAL_EMOJI}')
            healer_signedup[index] = usersigned_up
            healerspotfound = True

    healer_header = ""
    for index, value in enumerate(healer_signedup):
        index = index + 1
        healer_header = healer_header + "Healer" + str(index) + "=" + value + "\n"

    if ((healer_roster_full is True) and (chosen_role == "healer")) or ((make_backup_healer is True) and (chosen_role == "healer")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    # Add user to the DPS roster if they clicked mele or ranged DPS emoji.
    dps_spot_found = False
    for index, value in enumerate(dps_signedup):
        if (value == "Open") and ((dps_spot_found is False) and (make_backup_dps is False)) and (chosen_role in ("rangeddps", "meleedps")):
            if chosen_role == "rangeddps":
                dps_emoji = RANGED_EMOJI
            elif chosen_role == "meleedps":
                dps_emoji = MELEE_EMOJI

            usersigned_up = (f'{member_to_signup} {dps_emoji}')
            dps_signedup[index] = usersigned_up
            dps_spot_found = True

    dps_header = ""
    for index, value in enumerate(dps_signedup):
        index = index + 1
        dps_header = dps_header + "DPS" + str(index) + "=" + value + "\n"

    if (dps_roster_full is True) and (chosen_role in ("rangeddps", "meleedps")) or (make_backup_dps is True) and (chosen_role in ("rangeddps", "meleedps")):
        backup_signedup.append(f'{member_to_signup} {role_emote}')

    # Add users to Backup Roster if something was full.
    backup_header = ""
    for index, value in enumerate(backup_signedup):
        index = index + 1
        backup_header = backup_header + "Backup" + str(index) + "=" + value + "\n"

    # Add in the TrialID
    trialid_header = ("TrialID=" + str(trialid[0]))

    edited_message = {}
    edited_message['message'] = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + dps_header + "\n" + backup_header + "\n" + trialid_header
    edited_message['trialid'] = str(trialid[0])

    # Pass our edited message out to be sent to disord, unless the users role is none, in which case we pass the unedited message.
    if chosen_role != "None":  # pylint: disable=no-else-return
        return edited_message

    else:
        return trial_message.content

def lock_trial_roster(trial_message):
    """This function is called when we need to lock or unlock a trial.  The signup emoji don't work on a locked trial."""

    # Parse the Trial ID
    trialid_rex = r'TrialID\=(\d{6})'
    trialid = re.findall(trialid_rex, trial_message.content)

    locked_string = "\nTrial_Locked"
    edited_message = {}

    # Trial is already locked, so lets unlock it.
    if locked_string in trial_message.content:
        print(f'{timestamp()}, {trialid} UnLocked.')
        edited_message['message'] = trial_message.content.replace(locked_string, "")
        return edited_message

    # Trial is unlocked, so lets lock it.
    else:
        print(f'{timestamp()}, {trialid} Locked.')
        edited_message['message'] = trial_message.content + locked_string
        return edited_message


def timestamp():
    """Return the current time as a string for log purposes."""
    now = datetime.now()
    time_stamp = now.strftime("%m/%d/%Y, %H:%M:%S %Z")
    return time_stamp


def get_trial_id():
    """Generate a random 6 digit Trial ID"""
    trialid = ''.join(["{}".format(randint(0, 9)) for num in range(0, 6)])
    return trialid

# Connect the Client to Discord and report back.
@client.event
async def on_ready():
    print(f'{timestamp()}, {client.user} has connected to {client.guilds} Discord')

# Watch messages on the Discord server for commands the bot cares about.
@client.event
async def on_message(message):
    # Check if the message author has the Correct Role to Edit and Create Trial rosters Ignore messages that are DMs or from the Bot.
    if message.guild is not None and message.author != client.user:
        user_has_perms = bool(CREATE_EDIT_TRIAL_ROLE in [role.name for role in message.author.roles])

    # Print to log the message if it isn't from the bot.
    if message.author != client.user:
        print(f'{timestamp()}, Channel={message.channel}, Author={message.author}, Message={message.content}')

    # If the message is from the bot lets do nothing.
    if message.author == client.user:
        print(f'{timestamp()}, Message from bot, ignoring.')

    # If the message is not from a discord server (aka guild) then it's a DM to the bot.  Let's respond with the help page for the bot.
    elif message.guild is None and message.author != client.user:

        channel = await message.author.create_dm()

        await channel.send(PAC_BOT_HELP_PAGE)

        print(f'{timestamp()}, Responded to {message.author} with help page.')

    # Someone typed a message starting with !NewTrial, that is probably for us.
    elif message.content.startswith('!NewTrial'):
        if user_has_perms is False:
            error_msg = "You don't have the correct role to create or edit a trial roster"
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} tried to create a new trial but does not have the role {CREATE_EDIT_TRIAL_ROLE}.')
            return

        # Regular expression to parse out the arguments after the command.
        new_trial_rex = r'\!NewTrial\s(?P<tank>\d{1,2})\s(?P<healer>\d{1,2})\s(?P<DPS>\d{1,2})(?:\s|)(?P<Title>(?:.*|))'
        new_trial_vars = re.search(new_trial_rex, message.content)

        if new_trial_vars:
            tank_count = int(new_trial_vars.group('tank'))
            healer_count = int(new_trial_vars.group('healer'))
            dps_count = int(new_trial_vars.group('DPS'))
            trial_title = new_trial_vars.group('Title')

            # Lets limit the max spots for any role to 20 so we don't overrun the max Discord message length.
            if tank_count > 20:
                tank_count = 20

            if healer_count > 20:
                healer_count = 20

            if dps_count > 20:
                dps_count = 20

        else:
            # If the regular expression didn't match they must of typed the incorrect syntax, lets throw an error.
            error_msg = "Syntax Error for command !NewTrial.  DM the bot for a command help page."
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} NewTrial error, Message syntax invalid.')
            return

        # Create the intial trial post
        title_header = "Pac's Raid Signup Bot has posted " + trial_title + "\n"

        instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {TANK_EMOJI}\nHealer = {HEAL_EMOJI}\nRangedDPS = {RANGED_EMOJI}\nMeleeDPS = {MELEE_EMOJI}\nUnSignup = {UNSIGNUP_EMOJI}\n")

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
        # First Get a list of previous trialIDs in channel so we can check for collision.
        trialid_history = []
        async for trial_message in message.channel.history():
            trialid_rex = r'TrialID\=(\d{6})'
            message_trial_id = re.findall(trialid_rex, trial_message.content)

            if message_trial_id:
                trialid_history.append(int(message_trial_id[0]))

        # Pull a Random trial ID from get_trial_id(), then make sure it hasn't been used before.  Loop until we find an unused ID.
        while True:
            trialid = get_trial_id()
            if trialid not in trialid_history:
                break

        trialid_header = ("TrialID=" + str(trialid))

        response = title_header + "\n" + instructions_header + "\n" + tank_header + "\n" + healer_header + "\n" + dps_header + "\n" + trialid_header

        # Post the Message in the same discord channel the command was run from.
        await message.channel.send(response)

        # Grab the last message posted to discord. That should be what our bot just posted. We need it's ID so we can add the reaction emotes.
        async for last_message in message.channel.history(limit=1):

            default_reactions = [TANK_EMOJI, HEAL_EMOJI, MELEE_EMOJI, RANGED_EMOJI, UNSIGNUP_EMOJI]
            for emoji in default_reactions:
                await last_message.add_reaction(emoji)

        print(f'{timestamp()}, Created a trial with {str(tank_count)} Tanks, {str(healer_count)} Healers, and {str(dps_count)} DPS named {trial_title} in channel {message.channel}')

    # Someone typed a message starting with !AddtoTrial, that is probably for us
    elif message.content.startswith('!AddtoTrial'):
        if user_has_perms is False:
            error_msg = "You don't have the correct role to create or edit a trial roster"
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} tried to add/remove someone from trial but does not have the role {CREATE_EDIT_TRIAL_ROLE}.')
            return

        add_to_trial_rex = r'\!AddtoTrial\s(?P<trialid>\d{6})\s*(?P<member_to_signup>\<\@.*?\>)\s*(?P<role_emote>.*)(?:\s|$)'
        add_to_trial_vars = re.search(add_to_trial_rex, message.content)

        if add_to_trial_vars:
            trialid = add_to_trial_vars.group('trialid')
            member_to_signup = add_to_trial_vars.group('member_to_signup')
            role_emote = add_to_trial_vars.group('role_emote')

            member_to_signup = member_to_signup.replace('!', '')

            trialid_found = False
            async for trial_message in message.channel.history():

                # Search the message for a Trial ID.
                trialid_rex = r'TrialID\=(\d{6})'
                trialid_message = re.findall(trialid_rex, trial_message.content)

                if trialid_message:

                    if trialid_message[0] == trialid:
                        edited_message = update_trial_roster(trial_message, member_to_signup, role_emote)
                        await trial_message.edit(content=edited_message['message'])

                        trialid_found = True
                        print(f'{timestamp()}, {message.author} used addtotrial {role_emote} {member_to_signup} to trial {trialid}.')

            if trialid_found is False:
                print(f'{timestamp()}, {message.author} Addtotrial error, {trialid} not found.')

        else:
            # The regular expression failed to parse so lets assume there was a syntax typo and throw an error.
            error_msg = "Syntax Error for command !AddtoTrial.  DM the bot for a command help page."
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} Addtotrial error, Message syntax invalid.')
            return

    elif message.content.startswith('!LockTrial'):
        if user_has_perms is False:
            error_msg = "You don't have the correct role to lock a trial roster"
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} tried to lock a trial but does not have the role {CREATE_EDIT_TRIAL_ROLE}.')
            return

        lock_trial_rex = r'\!LockTrial\s(?P<trialid>\d{6})(?:\s|$)'
        lock_trial_vars = re.search(lock_trial_rex, message.content)

        if lock_trial_vars:
            trialid = lock_trial_vars.group('trialid')

            trialid_found = False
            async for trial_message in message.channel.history():

                # Search the message for a Trial ID.
                trialid_rex = r'TrialID\=(\d{6})'
                trialid_message = re.findall(trialid_rex, trial_message.content)

                if trialid_message:

                    if trialid_message[0] == trialid:
                        edited_message = lock_trial_roster(trial_message)
                        await trial_message.edit(content=edited_message['message'])

                        trialid_found = True
                        print(f'{timestamp()}, {message.author} used LockTrial to trial {trialid}.')

            if trialid_found is False:
                print(f'{timestamp()}, {message.author} LockTrial error, {trialid} not found.')

        else:
            # The regular expression failed to parse so lets assume there was a syntax typo and throw an error.
            error_msg = "Syntax Error for command !LockTrial.  DM the bot for a command help page."
            channel = await message.author.create_dm()
            await channel.send(error_msg)
            print(f'{timestamp()}, {message.author} LockTrial error, Message syntax invalid.')
            return

# Watch for a emoji reaction.
@client.event
async def on_raw_reaction_add(reaction):
    if reaction.user_id == client.user.id:
        pass

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

        # Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):

            member_to_signup = (f'<@{reaction.user_id}>')
            member_to_signup_name = client.get_user(reaction.user_id)
            locked_string = "\nTrial_Locked"

            if locked_string in message.content:
                pass

            else:
                edited_message = update_trial_roster(message, member_to_signup, reaction.emoji)

                await message.edit(content=edited_message['message'])

                edited_trialid = edited_message['trialid']

                print(f'{timestamp()}, {member_to_signup_name} clicked the {reaction.emoji} emoji.')
                print(f'{timestamp()}, TrialID {edited_trialid} was edited.')

        else:
            pass

# Watch for removing an emoji reaction.
@client.event
async def on_raw_reaction_remove(reaction):
    if reaction.user_id == client.user.id:
        pass

    else:
        message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

        # Figure out what role emoje was clicked
        if message.content.startswith('Pac\'s Raid Signup Bot has posted'):

            member_to_signup = (f'<@{reaction.user_id}>')
            member_to_signup_name = client.get_user(reaction.user_id)
            locked_string = "\nTrial_Locked"

            if locked_string in message.content:
                pass

            else:
                edited_message = update_trial_roster(message, member_to_signup, reaction.emoji)

                await message.edit(content=edited_message['message'])

                edited_trialid = edited_message['trialid']

                print(f'{timestamp()}, {member_to_signup_name} un-clicked the {reaction.emoji} emoji.')
                print(f'{timestamp()}, TrialID {edited_trialid} was edited.')

        else:
            pass

# Print Welcome Message and Assign a Role when someone joins the discord.
@client.event
async def on_member_join(member):
    print(member.name + " has joined " + str(member.guild))

    role = discord.utils.get(member.guild.roles, name=WELCOME_ROLE_NAME)
    channel = discord.utils.get(client.get_all_channels(), name=WELCOME_CHANNEL_NAME)

    welcome_member = f'<@{member.id}>'

    welcome_message = "This one welcomes " + welcome_member + " to " + str(member.guild) + ".  Please change your discord nickname to match your ESO @ name."

    await member.add_roles(role)
    await channel.send(welcome_message)

    print(f'{timestamp()}, The bot welcomed {welcome_member} to the guild.')

if __name__ == '__main__':
    client.run(TOKEN)
