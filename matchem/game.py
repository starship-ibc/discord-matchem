import asyncio
from datetime import datetime, timedelta
from random import randint

import discord
from wand.image import Image

from .card import create_cards


class Game(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        self.match_card = None
        self.round_message = None
        self.images_per_card = 4
        self.rounds_left = 0
        self.winners = []
        self.losers = {}
        self.guild = None

    @property
    def game_in_progress(self):
        return self.rounds_left > 0

    @property
    def current_round(self):
        return len(self.winners) + 1

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id or self.game_in_progress:
            return

        if message.content.startswith("sg-games play matchem"):
            rounds = 5
            m_args = message.content.split(" ")
            self.images_per_card = 4
            if len(m_args) > 3:
                rounds = int(m_args[3])
            if len(m_args) > 4:
                self.images_per_card = int(m_args[4])

            await self.start_game(
                message.guild, message.channel, rounds, self.images_per_card
            )

    async def start_game(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel,
        rounds: int,
        images_per_card: int,
    ):
        await channel.send(
            "Starting a game of Match-Em! Be the first person to "
            "react with the icon that appears on both sides of the image."
            "\n\nGame settings:"
            f"\n- Rounds: {rounds}"
            f"\n- Images: {images_per_card}"
        )

        self.guild = guild
        print(guild)
        self.winners = []
        self.rounds_left = rounds
        await self.play_round(channel, images_per_card)

    async def play_round(self, channel: discord.TextChannel, images_per_card: int):
        cards = create_cards(images_per_card)
        img: Image = cards["combined_image"]

        filename = "card.png"
        img.save(filename=filename)
        cards_img = discord.File(filename)
        self.round_message: discord.Message = await channel.send(
            content=f"Round {self.current_round}: Start!", file=cards_img
        )
        self.match_card = cards["card_info"][3]

        emojis = [c["emoji"] for c in cards["card_info"]]
        tasks = []
        while len(emojis) > 0:
            emoji = emojis.pop(randint(0, len(emojis) - 1))
            tasks.append(self.round_message.add_reaction(emoji))
        await asyncio.gather(*tasks)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (
            not self.game_in_progress
            or payload.message_id != self.round_message.id
            or payload.user_id == self.user.id
        ):
            return

        # discord.PartialEmoji()
        correct_emoji = discord.PartialEmoji(name=self.match_card["emoji"])
        if payload.emoji != correct_emoji:
            print(f"{payload.user_id} put in timeout for {payload.emoji}")
            allowed_time = datetime.utcnow() + timedelta(seconds=5)
            self.losers[payload.user_id] = allowed_time
            return

        if (
            payload.user_id in self.losers
            and datetime.utcnow() <= self.losers[payload.user_id]
        ):
            print(f"User {payload.user_id} in timeout")
            return

        print(f"CORRECT GUESS! from {payload.user_id} ({payload.emoji})")
        channel: discord.TextChannel = self.get_channel(payload.channel_id)
        member: discord.Member = await self.guild.fetch_member(payload.user_id)

        message = channel.get_partial_message(payload.message_id)
        await message.delete()

        await channel.send(f"Round {self.current_round} winner: {member.mention}!")
        self.winners.append(member)
        self.rounds_left -= 1
        if self.rounds_left > 0:
            await self.play_round(channel, self.images_per_card)
            return

        winner_count = {}
        for winner in self.winners:
            key = winner.mention
            if key not in winner_count:
                winner_count[key] = 0
            winner_count[key] += 1

        winner_str = "\n".join(
            [f"{w}: {r}" for w, r in reversed(sorted(winner_count.items()))]
        )
        await channel.send("Game finished. Congrats to the winners!\n\n" + winner_str)
