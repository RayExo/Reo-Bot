import discord


from discord.ext import commands


from reo.src.checks import checks


from reo.console.logging import logger


from reo.style import color


from reo.utils import pings


from reo.workflows import gif


from reo.engine.Bot import AutoShardedBot


from reo.workflows import ui


import random


import traceback


import asyncio


class Fun(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Fun"

            category = "Extra"

            description = "Fun commands"

            hidden = False

            emoji = self.bot.emoji.FUN or "🎉"

        self.cog_info = cog_info

    @commands.command(name="slap", help="👋 Slap a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def slap(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get slap gif

        image_url = gif.get_gif("slapping")

        embed = discord.Embed(
            title=f"{ctx.author.name} slapped {(user.name) if user.id != ctx.author.id else 'Himself/Herself'}",
            color=color.random_color(),
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="hug", help="🤗 Hug a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def hug(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get hug gif

        image_url = gif.get_gif("hugging")

        embed = discord.Embed(
            title=f"{ctx.author.name} hugged {(user.name) if user.id != ctx.author.id else 'Himself/Herself'}",
            color=color.random_color(),
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="kiss", help="💋 Kiss a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def kiss(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get kiss gif

        image_url = gif.get_gif("kissing")

        embed = discord.Embed(
            title=f"{ctx.author.name} kissed {(user.name) if user.id != ctx.author.id else 'Himself/Herself'}",
            color=color.random_color(),
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="pat", help="ðŸ¾ Pat a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def pat(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get pat gif

        image_url = gif.get_gif("patting")

        embed = discord.Embed(
            title=f"{ctx.author.name} patted {(user.name) if user.id != ctx.author.id else 'Himself/Herself'}",
            color=color.random_color(),
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="cry", help="😢 Cry", emoji="😢")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def cry(self, ctx: commands.Context):

        # get cry gif

        image_url = gif.get_gif("crying")

        embed = discord.Embed(
            title=f"{ctx.author.name} is crying", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="dance", help="💃 Dance")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def dance(self, ctx: commands.Context):

        # get dance gif

        image_url = gif.get_gif("dancing")

        embed = discord.Embed(
            title=f"{ctx.author.name} is dancing", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="laugh", help="😂 Laugh")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def laugh(self, ctx: commands.Context):

        # get laugh gif

        image_url = gif.get_gif("laughing")

        embed = discord.Embed(
            title=f"{ctx.author.name} is laughing", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="smile", help="😊 Smile")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def smile(self, ctx: commands.Context):

        # get smile gif

        image_url = gif.get_gif("smiling")

        embed = discord.Embed(
            title=f"{ctx.author.name} is smiling", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="angry", help="😡 Angry")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def angry(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get angry gif

        image_url = gif.get_gif("angry")

        embed = discord.Embed(
            title=f"{ctx.author.name} is angry at {(user.name) if user.id != ctx.author.id else 'Himself/Herself'}",
            color=color.random_color(),
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="confused", help="🤔 Confused")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def confused(self, ctx: commands.Context):

        # get confused gif

        image_url = gif.get_gif("confused")

        embed = discord.Embed(
            title=f"{ctx.author.name} is confused", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="sleep", help="😴 Sleep")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def sleep(self, ctx: commands.Context):

        # get sleep gif

        image_url = gif.get_gif("sleeping cartoon")

        embed = discord.Embed(
            title=f"{ctx.author.name} is sleeping", color=color.random_color()
        )

        embed.set_image(url=image_url)

        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="gay", help="Predict a persons gayness level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def gay_command(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            gayness = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                gayness = 0

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                gayness = 100

            embed = discord.Embed(
                description=f"{user.name} is {gayness}% Gay", color=color.random_color()
            )

            embed.set_author(
                name=f"{user.name} Gay Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="lesbian", help="Predict a persons lesbian level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def lesbian(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            lasbian = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                lasbian = 0

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                lasbian = 100

            embed = discord.Embed(
                description=f"{user.name} is {lasbian}% Lesbian",
                color=color.random_color(),
            )

            embed.set_author(
                name=f"{user.name} Lesbian Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="horny", help="Predict a persons horny level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def horny(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            horny = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                horny = 0

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                horny = 100

            embed = discord.Embed(
                description=f"{user.name} is {horny}% Horny", color=color.random_color()
            )

            embed.set_author(
                name=f"{user.name} Horny Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="simp", help="Predict a persons simp level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def simp(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            simp = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                simp = 0

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                simp = 100

            embed = discord.Embed(
                description=f"{user.mention} is {simp}% Simp",
                color=color.random_color(),
            )

            embed.set_author(
                name=f"{user.name} Simp Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="iq", help="Predict a persons IQ level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def iq(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            iq = random.randint(0, 200)

            if any(user.id == dev.id for dev in self.bot.developers):

                iq = 200

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                iq = 0

            embed = discord.Embed(
                description=f"{user.mention} has an IQ of `{iq}`",
                color=color.random_color(),
            )

            embed.set_author(
                name=f"{user.name} IQ Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="cute", help="Predict a persons cuteness level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def cute(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            cute = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                cute = 100

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                cute = 0

            embed = discord.Embed(
                description=f"{user.mention} is {cute}% Cute",
                color=color.random_color(),
            )

            embed.set_author(
                name=f"{user.name} Cute Level", icon_url=user.display_avatar.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="fakeban", help="Fake ban a user", aliases=["fban"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    async def fakeban(
        self, ctx: commands.Context, user: discord.Member, *, reason: str = None
    ):

        try:

            if user.id == self.bot.user.id:

                return await ctx.send("I can't ban myself")

            embed = discord.Embed(
                description=f"{self.bot.emoji.BAN} | Successfully Banned {user.mention} !\nReason: `{reason}`",
                color=color.green,
            )

            embed.set_footer(
                text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url
            )

            embed.set_author(name=f"User Banned", icon_url=user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="fakekick", help="Fake kick a user", aliases=["fkick"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    async def fakekick(
        self, ctx: commands.Context, user: discord.Member, *, reason: str = None
    ):

        try:

            if user.id == self.bot.user.id:

                return await ctx.send("I can't kick myself")

            embed = discord.Embed(
                description=f"{self.bot.emoji.KICK} | Successfully Kicked {user.mention} !\nReason: `{reason}`",
                color=color.green,
            )

            embed.set_footer(
                text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url
            )

            embed.set_author(name=f"User Kicked", icon_url=user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="nukeall", help="Nuke all channels in the server ")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def nukeall(self, ctx: commands.Context):

        try:

            # fake nuke all channels

            embed = discord.Embed(
                description=f"{self.bot.emoji.LOADING} | Nuking Server...",
                color=color.random_color(),
            )

            message = await ctx.send(embed=embed)

            await asyncio.sleep(5)

            embed.description = f"{self.bot.emoji.SUCCESS} | LOL, Just Kidding 😂"

            embed.set_image(
                url="https://cdn.discordapp.com/attachments/1286969360224882688/1287446868623888497/bully-surprise.gif?ex=66f193d5&is=66f04255&hm=5e6d5fc4491927bcec940dab85d68df735b4d22db5d62d71a96377c2e49cdff8&"
            )

            await message.edit(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="ship",
        help="Predict a relationship between two persons",
        aliases=["compatibility", "romance"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=4, per=60, type=commands.BucketType.user)
    async def relation(
        self, ctx: commands.Context, user1: discord.Member, user2: discord.Member = None
    ):

        try:

            if not user2:

                user1, user2 = ctx.author, user1

            # fake relationship percentage

            percentage = random.randint(0, 100)

            if any(
                u.id == dev.id for u in [user1, user2] for dev in self.bot.developers
            ):

                percentage = 0

            embed = discord.Embed(
                description=f"{user1.mention} and {user2.mention} are `{percentage}%` Compatible",
                color=color.random_color(),
            )

            embed.set_author(
                name=f"Relationship Percentage", icon_url=ctx.guild.icon.url
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            try:

                image = ui.create_relation_percentage_banner(
                    user1.display_avatar.url, user2.display_avatar.url, percentage
                )

                file = discord.File(image, filename="relationship.png")

                embed.set_image(url="attachment://relationship.png")

            except Exception as e:

                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

                file = None

            await ctx.send(embed=embed, file=file)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
