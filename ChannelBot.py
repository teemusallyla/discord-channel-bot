import discord

with open("token.txt") as f:
    token = f.read().rstrip()

class ChannelBot(discord.Client):

    async def on_ready(self):
        self.appinfo = await self.application_info()
        print("Bot logged in")

    async def on_message(self, message):
        if message.author == self.appinfo.owner:
            await message.channel.send("You sent a message! " + message.content)

    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if before.channel:
            await self.on_voice_channel_leave(member, before.channel)
        
        if after.channel:
            await self.on_voice_channel_join(member, after.channel)

    async def on_voice_channel_leave(self, member, channel):
        guild = channel.guild
        perms = guild.me.guild_permissions

        before_role = discord.utils.find(
            lambda r: r.name == channel.name,
            guild.roles
        )
        if before_role:
            await member.remove_roles(before_role)
            print("Removed Role")

    async def on_voice_channel_join(self, member, channel):
        guild = channel.guild
        perms = guild.me.guild_permissions

        after_role = discord.utils.find(
            lambda r: r.name == channel.name,
            guild.roles
        )

        if not after_role:
            if perms.manage_roles:
                after_role = await guild.create_role(name=channel.name)
        
        if after_role:
            await member.add_roles(after_role)
            print("Added Role")



bot = ChannelBot()

bot.run(token)