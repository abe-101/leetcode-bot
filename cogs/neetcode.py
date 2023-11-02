import pathlib
from typing import List
import datetime
from zoneinfo import ZoneInfo

import discord
import git
from discord import app_commands
from discord.ext import commands, tasks
from git.repo.base import Repo



class Neetcode(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = self.bot.logger
        self.pull_repo.start()
        self.daily_report.start()  # Start the daily report loop
        self.bot_spam_channels = [
            1053845551315173397,  # bot-spam -> abes-server
            1053874909014675576,  # bot-playground -> neetcode

        ]
        
        self.command_usage_stats = {
            "pulls": 0,
            "leetcode_invoked": 0,
        }

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("America/New_York")))
    async def daily_report(self):
        # Log the daily report
        self.logger.info("Daily Report:")
        self.logger.info(f"Number of repo pulls: {self.command_usage_stats['pulls']}")
        self.logger.info(f"Number of leetcode command invocations: {self.command_usage_stats['leetcode_invoked']}")

    @tasks.loop(time=datetime.time(hour=22, minute=54, tzinfo=ZoneInfo("America/New_York")))
    async def pull_repo(self):
            o = self.repo.remotes.origin
            o.pull()
            self.logger.info("pulled repo on timer")
            self.command_usage_stats["pulls"] += 1  # Increment pull count


    async def cog_load(self) -> None:
        self.neetcode = pathlib.Path("leetcode")
        self.neetcode.mkdir(exist_ok=True)
        try:
            self.repo = Repo.clone_from(
                "https://github.com/neetcode-gh/leetcode.git", self.neetcode
            )
            self.logger.info("cloned repo")
            self.repo = Repo(self.neetcode)
        except git.exc.GitCommandError:
            self.repo = Repo(self.neetcode)
            o = self.repo.remotes.origin
            o.pull()
            self.logger.info("pulled repo")

        self.languages = [
            x.name
            for x in self.neetcode.iterdir()
            if x.is_dir() and not x.name.startswith(".")
        ]

    @app_commands.command()
    @app_commands.describe(
        number="the number leetcode problem you want a soluiton for",
        language="the coding language",
    )
    async def leetcode(
        self, interaction: discord.Interaction, number: int, language: str
    ):
        self.command_usage_stats["leetcode_invoked"] += 1
        # add leading zeros to match file names
        number = "{:04d}".format(number)
        """Returns the leetcode solution"""
        files = list(self.neetcode.glob(language + "/" + str(number) + "-*"))
        if language not in self.languages or len(files) == 0:
            await interaction.response.send_message(
                f"there are no solutions for leetcode problem #{number} in {language}",
                ephemeral=True
            )
            self.logger.info(f"{interaction.user} asked for problom #{number} in {language} but none exist")
            return

        self.logger.info(f"{interaction.user} asked for problom #{number} in {language}")
        with open(files[0]) as f:
            code = f.read()
        if interaction.channel_id in self.bot_spam_channels or interaction.channel.name.lower() == "leetcode":
            problem_name = pathlib.Path(files[0].stem).name.replace('-', ' ')
            await interaction.response.send_message(f"Problem #{problem_name} ({language})\n```{language}\n{code}\n```")
        else:
            await interaction.response.send_message(f"```{language}\n{code}\n```", ephemeral=True)

    @leetcode.autocomplete("language")
    async def leetcode_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=language, value=language)
            for language in self.languages
            if current.lower() in language.lower()
        ]

    @commands.command(hidden=True)
    @commands.is_owner()
    async def stats(self, ctx):
        """Reports the usage stats of the bot."""
        stats_message = "Command Usage Stats:\n"
        stats_message += f"Number of repo pulls: {self.command_usage_stats['pulls']}\n"
        stats_message += f"Number of leetcode command invocations: {self.command_usage_stats['leetcode_invoked']}\n"
        
        await ctx.send(stats_message)



async def setup(bot: commands.Bot):
    await bot.add_cog(Neetcode(bot))
