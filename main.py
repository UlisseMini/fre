import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

client.run('NjY2NzE2MTYzNDQ2OTMxNTI0.Xh4Ovw.7tXaovJVA8f2_JESnCRt3jFFWno')
