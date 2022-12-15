import pathlib
from typing import List

import discord
import git
from discord import app_commands
from discord.ext import commands
from git.repo.base import Repo


class Neetcode(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        self.neetcode = pathlib.Path("leetcode")
        self.neetcode.mkdir(exist_ok=True)
        try:
            Repo.clone_from(
                "https://github.com/self.neetcode-gh/leetcode.git", self.neetcode
            )
            print("cloned repo")
        except git.exc.GitCommandError:
            repo = Repo(self.neetcode)
            o = repo.remotes.origin
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
        if language not in self.languages or len(files) == 0:
            await interaction.response.send_message(
                f"there are no solutions for leetcode problem #{number} in {language}"
            )
            return

        with open(files[0]) as f:
            code = f.read()

        await interaction.response.send_message(f"```{language}\n{code}\n```")

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
