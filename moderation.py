from discord.ext import commands
import discord
from utils import form, get_prefix
import json
from time import time


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError) and str(error.original):
            await ctx.send('Ошибка:\n' + str(error.original))

    @commands.command(name='purge', help='Команда для удаления последних сообщений',
                      usage='{}purge <кол-во>')
    @commands.has_permissions(manage_messages=True)
    async def purge_(self, ctx, amt: int = 0):
        if amt == 0:
            pref = await get_prefix(self.bot, ctx.message)
            return await ctx.send(f'Использование: {pref}purge <кол-во>')
        channel = ctx.message.channel
        deleted = await channel.purge(limit=amt + 1, check=lambda msg: True)
        amt = len(deleted) - 1
        return await ctx.send('Удалено {} {}'.format(amt, form(amt, ['сообщение', 'сообщения', 'сообщений'])))

    @commands.command(usage='{}move <название канала>',
                      help='Команда для перемещения всех из одного канала в другой')
    @commands.has_permissions(move_members=True)
    async def move(self, ctx, *, channel: str):
        if ctx.author.voice.channel.name.lower() == channel.lower():
            return await ctx.send('Уже подключен к голосовому каналу')
        channels = await ctx.guild.fetch_channels()
        for ch in channels:
            if (ch.__class__ == discord.channel.VoiceChannel) and (ch.name.lower() == channel.lower()):
                members = ctx.author.voice.channel.members
                for member in members:
                    await member.move_to(ch)
                return await ctx.send('*⃣ | Перемещен в {}'.format(ch.name))
        return await ctx.send('Канал с таким именем не найден')

    @commands.command(name='prefix', pass_context=True, help='Команда для установки префикса бота',
                      usage='{}prefix [префикс]')
    @commands.has_permissions(administrator=True)
    async def pref_(self, ctx, pref=None):
        if not pref:
            prefixes = await self.bot.get_prefix(ctx.message)
            sid = str(self.bot.user.id)
            for pr in prefixes:
                if sid not in pr:
                    return await ctx.send('Текущий префикс: {}'.format(pr))
        pfxs = json.load(open('resources/prefixes.json', 'r'))
        pfxs[str(ctx.guild.id)] = pref
        json.dump(pfxs, open('resources/prefixes.json', 'w'))
        return await ctx.send('Префикс установлен на {}'.format(pref))

    @commands.command(name='ping', pass_context=True, help='Команда для проверки жизнеспособности бота',
                      usage='{}ping')
    async def ping_(self, ctx):
        embed = discord.Embed(description='Pong')
        ts = time()
        msg = await ctx.send(embed=embed)
        tm = (time() - ts) * 1000
        embed.description = '{:.2f}ms'.format(tm)
        return await msg.edit(embed=embed)


def mod_setup(bot):
    bot.add_cog(Moderation(bot))
