# This is new in the discord.py 2.0 update

# imports
import discord
import discord.ext
from mojang import API
import requests
import json
from dungeons import DungeonsCarry

# setting up the bot
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
dungeonCarry = DungeonsCarry('dungeon_carry_db')

HypApi = 'API KEY HERE'

def carrier(ctx):
    role = ctx.user.guild.roles[[x.name for x in ctx.user.guild.roles].index('Carrier')]
    if role in ctx.user.roles:
        return True
    else:
        return False

def verified(ctx):
    role = ctx.user.guild.roles[[x.name for x in ctx.user.guild.roles].index('Verified')]
    if role in ctx.user.roles:
        return True
    else:
        return False

def verify(ign, discord, uid):
    global HypApi
    try:
        uuid = API().get_uuid(ign)
        if not uuid:
            return False
        res = requests.get(f'https://api.hypixel.net/player?key={HypApi}&uuid={uuid}').json()['player']['socialMedia']['links']
        retdisc=res['DISCORD']
    except Exception:
        return False
    if retdisc == discord:
        with open('verified.json') as f:
            data = json.load(f)
            data['verified'][uid] = uuid
        with open('verified.json', 'w') as outfile:
            json.dump(data, outfile)
        return True

# sync the slash command to your server
@client.event
async def on_ready():
    await tree.sync()
    # print "ready" in the console when the bot is ready to work
    print("ready")

# make the slash command
@tree.command(name="verify", description="verify with Hypixel")
async def command_verify(ctx: discord.Interaction, ign:str):
    names = [x.name for x in ctx.user.roles]
    if not 'Verified' in names:
        res = verify(ign=ign, discord=ctx.user.name, uid=ctx.user.id)
        print(res)
        if res:
            role = ctx.user.guild.roles[[x.name for x in ctx.user.guild.roles].index('Verified')]

            await ctx.user.add_roles(role, reason='User Verified')
            await ctx.response.send_message(f"Successfully Verified: {ign}!", ephemeral=True)
        else:
            await ctx.response.send_message(f"Couldn't Verify: {ign}\nEither:\n> Username Doesnt Exist\n> Username isn't linked to discord om Hypixel (log on to hypixel -> social menu -> link discord)\n> Discord linked to hypixel is outdatd (relink discord)", ephemeral=True)
    else:
        await ctx.response.send_message(f"Can't Verify IGN: {ign}\n>  IGN already verified", ephemeral=True)

#--------------------------------dungeons----------------------------------

@tree.command(name="dgn_request_carry", description="Request a dungeon carry!")
async def command_dungeon_request_carry(ctx: discord.Interaction, floor:str):
    if not verified(ctx):
        await ctx.response.send_message('Please verify with /verify', ephemeral=True)
        return True
    if floor.upper() in dungeonCarry.codes:
        if not dungeonCarry.check_active_carry(str(ctx.user.id)):
            dungeonCarry.request_carry(floor, str(ctx.user.id))
            await ctx.response.send_message(f'You have successfully applied an {floor.upper()} carry!\n You will get a DM with details of your carry once a Verified carrier has accepted your request!', ephemeral=True)
        else:
            await ctx.response.send_message(f'You already have an active carry!\nPlease cancel it if you wish to do another carry!', ephemeral=True)
    else:
        f=''
        for x in dungeonCarry.codes:
            f=f+f'\n> {x}'
        await ctx.response.send_message(f'Invalid Floor Code!\nCodes:{f}',ephemeral=True)

@tree.command(name="dgn_cancelcarry", description="Cancel a carry!")
async def command_dungeon_cancel_carry(ctx: discord.Interaction):
    if not verified(ctx):
        await ctx.response.send_message('Please verify with /verify', ephemeral=True)
        return True
    if dungeonCarry.check_active_carry(str(ctx.user.id)):
        dungeonCarry.cancel_carry(str(ctx.user.id))
        await ctx.response.send_message(f'Successfully Canceled Your Dungeon Carry!',ephemeral=True)
    else:
        await ctx.response.send_message('You dont have an active carry!\n**/dgn_request_carry** to start a carry!', ephemeral=True)

@tree.command(name="dgn_viewrequests", description="View everyone who wants a carry and in what floor")
async def command_dungeon_view_carry(ctx: discord.Interaction):
    if not verified(ctx) or not carrier(ctx):
        await ctx.response.send_message('You need to be verified with /verify or be a carrier to use this command', ephemeral=True)
        return True
    embed = discord.Embed(title='Carry Viewer', description='This shows the whole database:')
    db = dungeonCarry.database_get()
    for x in db:
        usrs = []
        for i in db[x]:
            usrs.append(client.get_user(int(i)).name)
        embed.add_field(name=x, value=f'{usrs}\n', inline=True)
    await ctx.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="dgn_startcarry", description="Start carry for certain floor")
async def command_dungeon_start_carry(ctx: discord.Interaction, floor:str, ppl:int):
    if not verified(ctx) or not carrier(ctx):
        await ctx.response.send_message('You need to be verified with /verify or be a carrier to use this command', ephemeral=True)
        return True
    if floor.upper() in dungeonCarry.codes:
        dids = dungeonCarry.start_carry(ppl=ppl, floor=floor)
        igns = []
        api = API()
        with open('verified.json') as f:
            data = json.load(f)
            for x in range(len(dids)):
                igns.append(api.get_username(data['verified'][str(dids[x])]))
            message = f'**---**\nYour **{floor.upper()}** carry has been accepted by **"@{ctx.user.name}"**\nYou will be getting an invite from **{api.get_username(data["verified"][str(ctx.user.id)])}** shortly!\n**---**'
            for x in dids:
                usr = client.get_user(int(x))
                await usr.send(content=message)
                final = ''
                for x in igns:
                    final = final+f'> {x}\n'
                await ctx.response.send_message(f'**{floor.upper()} carry**\nAdd to Party: \n{final}')

    else:
        f=''
        for x in dungeonCarry.codes:
            f=f+f'\n> {x}'
        await ctx.response.send_message(f'Invalid Floor Code!\nCodes:{f}',ephemeral=True)

# run the bot
client.run('DISCORD API KEY')