from discord.ext.commands import Cog
from discord.ext import commands
import pyttsx3
import discord


class Tts(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice',
                           r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0")
        self.engine.setProperty('volume', 1)

    @commands.command()
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined voice channel: {channel.name}")

    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def speak(self, ctx, *text):
        # ctx.voice_client.source.volume = 100 / 100
        msg = " ".join(text)
        self.engine.save_to_file(msg, 'test.mp3')
        self.engine.runAndWait()
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=r"D:\Program Files\ffmpeg\bin\ffmpeg.exe", source="test.mp3"))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        # await ctx.send(msg)