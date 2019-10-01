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

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!NewTrial'):

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

        print('Tank Count = ' + str(tank_count))
        print('Healer Count = ' + str(healer_count))
        print('DPS Count = ' + str(dps_count))
        print('Trial title = ' + trial_title)

        title_header = "Pac's Raid Signup Bot has posted " + trial_title + "\n"

        instructions_header = (f"To sign up click the reaction emoji below for your role.\nTank = {tank_emoji}\nHealer = {heal_emoji}\nMagDPS = {magdps_emoji}\nStamDPS = {stamdps_emoji}\n")
        
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


        await message.channel.send(response)

        print(f'{message.channel} is Message Channel')
        print(f'{message.author} is Message Author')

        async for last_message in message.channel.history(limit=1):
            #print(last_message)
            print(last_message.content)
            print('Last Message ID = ' + str(last_message.id))

            default_reactions = [tank_emoji,heal_emoji,stamdps_emoji,magdps_emoji]
            for emoji in default_reactions:
                await last_message.add_reaction(emoji)


@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    else:
        print('Emoji = ' + str(reaction.emoji))
        print('Emoji Channel ID = ' + str(reaction.message.channel.id))
        print('Emoji Message ID = ' + str(reaction.message.id))
        print('Emoji User = ' + str(user))
        print('Emoji User Nick = ' + str(user.nick))
        print('Emoji User ID = ' + str(user.id))

        if str(reaction.emoji) == tank_emoji:
            chosen_role = "tank"
        elif str(reaction.emoji) == heal_emoji:
            chosen_role = "healer"
        elif str(reaction.emoji) == magdps_emoji:
            chosen_role = "magdps"
        elif str(reaction.emoji) == stamdps_emoji:
            chosen_role = "stamdps"
        else:
            chosen_role = "None"

        print("Chosen Role = " + chosen_role)

        message = await client.get_channel(reaction.message.channel.id).fetch_message(reaction.message.id)

        print(message)
        edited_message = (f'Message edited by <@{user.id}>')
        #await message.edit(content=edited_message)





# bot = commands.Bot(command_prefix='!')

# @bot.command(name='ping', help='Replies with Pong')
# async def ping(ctx):

#     response = "Pong #1234"
#     await ctx.send(response)


#bot.run(token)

client.run(token)