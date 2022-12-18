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
        self.pull_repo.start()
        self.bot_spam_channels = [
            1053845551315173397,  # bot-spam -> abes-server
            1053874909014675576,  # bot-playground -> neetcode

        ]

    @tasks.loop(time=datetime.time(hour=22, minute=54, tzinfo=ZoneInfo("America/New_York")))
    async def pull_repo(self):
            o = self.repo.remotes.origin
            o.pull()
            print("pulled repo on timer")


    async def cog_load(self) -> None:
        self.neetcode = pathlib.Path("leetcode")
        self.neetcode.mkdir(exist_ok=True)
        try:
            self.repo = Repo.clone_from(
                "https://github.com/neetcode-gh/leetcode.git", self.neetcode
            )
            print("cloned repo")
            self.repo = Repo(self.neetcode)
        except git.exc.GitCommandError:
            self.repo = Repo(self.neetcode)
            o = self.repo.remotes.origin
            o.pull()
            print("pulled repo")

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
        """Returns the leetcode solution"""
        files = list(self.neetcode.glob(language + "/" + str(number) + "-*"))
        print(f"{interaction.user} asked for problom #{number} in {language}")
        if language not in self.languages or len(files) == 0:
            await interaction.response.send_message(
                f"there are no solutions for leetcode problem #{number} in {language}",
                ephemeral=True
            )
            return

        with open(files[0]) as f:
            code = f.read()
        if interaction.channel_id in self.bot_spam_channels:
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Neetcode(bot))
