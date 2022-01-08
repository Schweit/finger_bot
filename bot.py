import asyncio
import discord
import os
import youtube_dl
import json
import playlist
from discord.ext import commands

helpText = """Here are my commands you piece of shit..

**.join** - Joins Voice Chat
**.leave** - Leaves Voice Chat
**.mike** - Plays a Mike Dean song that will take you to ANOTHER! PLANET!!!!
**.stream [YouTube Url]** - Plays YouTube Audio

If I need to explain these next commands, you should just leave the server... 
**.play**
**.pause**
**.stop**
**.rickroll**

OHHHhh.. and Fuck Luke...
"""

youtube_dl.utils.bug_reports_message = lambda: '' 

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    voiceClient = None
    users = open("users.json", "r+") 
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        # if (ctx.author.voice):
        #     channel = ctx.author.voice.channel
        #     await channel.connect()
        # else:
        #     await ctx.send("Fuck you.. You're not even in a channel.")
        channel = ctx.author.voice.channel
        self.voiceClient = await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if self._checkPermissions(str(ctx.author), "stop"):
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Fuck you " + str(ctx.author).split("#")[0] + ", You're not my mom....")

    @commands.command()
    async def mike(self, ctx):
        async with ctx.typing():
            player = await YTDLSource.from_url("https://youtu.be/g0YRgWo6zdc?t=6", loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command()
    async def stream(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command
    async def pause(ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client                
        voice_channel.pause()

    @commands.command
    async def play(ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client                
        voice_channel.play()

    @commands.command()
    async def stop(self, ctx):
        if self._checkPermissions(str(ctx.author), "stop"):
            ctx.voice_client.stop()
        else:
            await ctx.send("Fuck you " + str(ctx.author).split("#")[0] + ", I'm not stopping this shit..")

    @commands.command()
    async def rickroll(self, ctx):
        if self._checkPermissions(str(ctx.author), "rick"):
            async with ctx.typing():
                player = await YTDLSource.from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley", loop=self.bot.loop, stream=True)
                print(player)
                # ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        else: 
            await ctx.send("Fuck you " + str(ctx.author).split("#")[0])
        
    @commands.command()
    async def getsong(self, ctx, *, url):
        await ctx.send("Bruh!!  That's " + self._getSongTitleByUrl(url)[0])

    @commands.command()
    async def playlist(self, ctx, playlistName, song = None, delete = None):
        if self._validateInputs(playlistName, song, delete) and await self._getSongTitleByUrl(song)[1]:
            playlist_engine.playlist(ctx.author, playlistName, song, delete)

    @commands.command()
    async def deleteplaylist(self, ctx, playlistName):
        if self._validateInputs(playlistName):
            playlist_engine.playlist(ctx.author, playlistName, None, True)

    @commands.command()
    async def showPlaylists(self, ctx):
        print("Something")
        print(ctx.author)

    @commands.command()
    async def playRandomPlaylist(self, ctx, *, user = None):
        print("Something")
        print(ctx.author)

    @commands.command()
    async def playPlaylist(self, ctx, *, playlistName):
        print("Something")
        print(ctx.author)

    @commands.command()
    async def help(self, ctx):
        await ctx.send(helpText)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == None:
            channels = await after.channel.guild.fetch_channels()
            for channel in channels:
                if str(channel.category) == "Text Channels":
                    print("idk..")
        if str(member) == "TopFord#7988":
            if before.channel == None:
                await asyncio.sleep(2)
                voice_state = member.guild.voice_client
                player = await YTDLSource.from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley", loop=self.bot.loop, stream=True)
                voice_state.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    def _checkPermissions(self, user, cmd):
        if (cmd == "rick"):
            if user == "HayBale#5783" or user == "FoXRuN402#6734":
                return False
        elif (cmd == "stop"):
            if user == "HayBale#5783" or user == "FoXRuN402#6734":
                return False
        return True

    def _validateInputs(self, *, playlistName = None, song = None, delete = None):
        if playlistName or song or delete:
            if playlistName and type(playlistName != str): return False
            if delete and str(delete) == "Delete": return False
        else:
            # No Params Sent
            return False
        return True

    async def _getSongTitleByUrl(self, url):
        try:
            song = await ytdl.extract_info(url)
            print(song)
            return [song['title'], True]
        except: 
            return ["Cant Find Song", False]



client = commands.Bot(command_prefix = '.', help_command=None)
count = 0
emoji = None
music = Music(client)

@client.event
async def on_ready():
    print("bot is ready")

@client.event
async def on_message(msg):
    global emoji
    global count
    if msg.author.bot or count == 0: return
    print(msg)
    await msg.add_reaction(emoji)
    if "Jake" in msg.content:
        channel = client.get_channel(msg.channel.id)
        await channel.send('Fuck Jake...')
    await client.process_commands(msg)

@client.event
async def on_raw_reaction_add(payload):
    global emoji
    global count
    if count == 0:
        print("Emoji Set!")
        emoji = payload.emoji
        count+=1

client.add_cog(music)
client.run('ODkwMzMwNjQ3NjE1NDAxOTk3.YUuPBw.raPHv6U0MqUJIQ-zan8Sgp1Qh1w')