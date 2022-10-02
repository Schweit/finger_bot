import asyncio
import discord
import youtube_dl
import playlist
from discord.ext import commands

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

async def main():
    async with bot:
        await bot.load_extension(extensions)


class MyBot(commands.Bot):
    count = 0
    emoji = None

    def __init__(self):
        super().__init__(command_prefix='$', intents = discord.Intents.all())
        self.initial_extensions = [
            'cogs.music',
        ]

    async def on_message(self, msg):
        if msg.author.bot or self.count == 0: return
        print(msg)
        await msg.add_reaction(self.emoji)
        if "Jake" in msg.content:
            channel = bot.get_channel(msg.channel.id)
            await channel.send('Fuck Jake...')
        await bot.process_commands(msg)
    
    async def on_raw_reaction_add(self, payload):
        if self.count == 0:
            print("Emoji Set!")
            self.emoji = payload.emoji
            self.count+=1

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print('Ready!')


bot = MyBot()
bot.run('')
