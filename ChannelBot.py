import discord
import json
import os
import time
import asyncio


def load_token():
    if not "token.txt" in os.listdir():
        return
    with open("token.txt") as f:
        return f.read().rstrip()

def load_configs():
    if not "config.json" in os.listdir():
        with open("base_config.json") as f:
            configs = json.load(f)
        with open("config.json", "w+") as f:
            json.dump(configs, f, indent=4)
    else:
        with open("config.json") as f:
            configs = json.load(f)

    return configs

def load_responses():
    with open("responses.json") as f:
        return json.load(f)

def save_configs(configs):
    with open("config.json", "w+") as f:
        json.dump(configs, f, indent=4)

class ChannelBot(discord.Client):

    async def on_ready(self):
        self.appinfo = await self.application_info()
        self.configs = load_configs()
        self.responses = load_responses()
        try:
            self.handler
        except AttributeError:
            self.handler = asyncio.ensure_future(self.delay_handler())

        for guild in self.guilds:
            if not str(guild.id) in self.configs:
                self.configs[str(guild.id)] = self.configs["base"].copy()
                self.configs[str(guild.id)]["channels"] = {}
                save_configs(self.configs)
        print("Bot logged in")

    async def on_message(self, message):
        if not message.author.guild_permissions.manage_channels:
            return
        if not message.content.startswith("!cb"):
            return
        
        split = message.content.split()
        if len(split) == 2:
            if split[1].lower() == "help":
                await message.channel.send(self.responses["help"])
            elif split[1].lower() == "delete":
                resp = self.responses["delete_help"]
                resp += " Current: " + str(self.configs[str(message.guild.id)]["delete_after"])
                await message.channel.send(resp)
            elif split[1].lower() == "clear":
                resp = self.responses["clear_help"]
                resp += " Current: " + str(self.configs[str(message.guild.id)]["clear_after"])
                await message.channel.send(resp)
            elif split[1].lower() in ["min", "minimum"]:
                resp = self.responses["minimum_help"]
                resp += " Current: " + str(self.configs[str(message.guild.id)]["minimum_members"])
                await message.channel.send(resp)
        elif len(split) == 3:
            if split[1].lower() == "delete":
                mins = split[2]
                if mins.isdigit():
                    mins = int(mins)
                    if mins < 0 or mins > 10000:
                        await message.channel.send("Minutes is too high or too low")
                        return
                else:
                    mins = "never"
                self.configs[str(message.guild.id)]["delete_after"] = mins
                save_configs(self.configs)
                await message.add_reaction("👍")
            elif split[1].lower() == "clear":
                mins = split[2]
                if mins.isdigit():
                    mins = int(mins)
                    if mins < 0 or mins > 10000:
                        await message.channel.send("Minutes is too high or too low")
                        return
                else:
                    mins = "never"
                self.configs[str(message.guild.id)]["clear_after"] = mins
                save_configs(self.configs)
                await message.add_reaction("👍")
            elif split[1].lower() in ["min", "minimum"]:
                num = split[2]
                if not num.isdigit() or int(num) < 0:
                    await message.channel.send("Not a proper number of members")
                    return
                else:
                    num = int(num)
                    self.configs[str(message.guild.id)]["minimum_members"] = num
                    save_configs(self.configs)
                    await message.add_reaction("👍")

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

        if not perms.manage_roles:
            print("I do not have the permissions to manage roles")
            return

        before_role = discord.utils.find(
            lambda r: r.name == channel.name,
            guild.roles
        )
        if before_role:
            await member.remove_roles(before_role)
            print("Removed Role")

        text_channel = discord.utils.find(
            lambda c: c.name == channel.name.lower() + "_text",
            guild.text_channels
        )

        if text_channel and len(channel.members) == 0:
            if perms.manage_channels:
                da = self.configs[str(guild.id)]["delete_after"]
                ca = self.configs[str(guild.id)]["clear_after"]
                if da == 0:
                    await text_channel.delete()
                elif ca == 0:
                    await text_channel.purge(limit=9999, after=text_channel.created_at)
                elif type(da) == int or type(ca) == int:
                    self.configs[str(guild.id)]["channels"][str(text_channel.id)] = int(time.time())
                    save_configs(self.configs)


    async def on_voice_channel_join(self, member, channel):
        guild = channel.guild
        perms = guild.me.guild_permissions

        if not perms.manage_roles:
            print("I do not have the permissions to manage roles")
            return

        after_role = discord.utils.find(
            lambda r: r.name == channel.name,
            guild.roles
        )

        text_channel = discord.utils.find(
            lambda c: c.name == channel.name.lower() + "_text",
            guild.text_channels
        )

        if not after_role:
            after_role = await guild.create_role(name=channel.name)
        
        if after_role:
            create_channel = len(channel.members) >= self.configs[str(guild.id)]["minimum_members"]
            if not text_channel and perms.manage_channels and create_channel:
                ow = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    after_role: discord.PermissionOverwrite(read_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                text_channel = await guild.create_text_channel(
                    channel.name + "_text",
                    overwrites=ow,
                    position=channel.position,
                    category=channel.category
                )
            elif text_channel:
                if str(text_channel.id) in self.configs[str(guild.id)]["channels"]:
                    del self.configs[str(guild.id)]["channels"][str(text_channel.id)]
                    save_configs(self.configs)
            await member.add_roles(after_role)
            print("Added Role")
    
    async def on_guild_join(self, guild):
        self.configs[str(guild.id)] = self.configs["base"].copy()
        self.configs[str(guild.id)]["channels"] = {}
        save_configs(self.configs)

    async def on_guild_remove(self, guild):
        if str(guild.id) in self.configs:
            del self.configs[str(guild.id)]
            save_configs(self.configs)


    async def delay_handler(self):
        while True:
            print("Handler going through stuff")
            for gid in self.configs:
                if gid == "base":
                    continue
                chid_to_delete = []
                da = self.configs[gid]["delete_after"]
                ca = self.configs[gid]["clear_after"]
                for chid in self.configs[gid]["channels"]:
                    last_visit = self.configs[gid]["channels"][chid]
                    if type(da) != int and type(ca) != int:
                        chid_to_delete.append(chid)
                        continue

                    elif type(da) == int and time.time() > last_visit + 60 * da:
                        print("handler deleting stuff")
                        channel = self.get_channel(int(chid))
                        if channel:
                            await channel.delete()
                            print("Deleted Channel")
                        else:
                            print("Couldn't find channel")
                        chid_to_delete.append(chid)

                    elif type(ca) == int and time.time() > last_visit + 60 * ca:
                        print("handler clearing stuff")
                        channel = self.get_channel(int(chid))
                        if channel:
                            await channel.purge(limit=9999, after=channel.created_at)
                            print("Cleared channel")
                        else:
                            print("Couldn't find channel")
                        if type(da) != int:
                            chid_to_delete.append(chid)

                for chid in chid_to_delete:
                    del self.configs[gid]["channels"][chid]
                if len(chid_to_delete) > 0:
                    save_configs(self.configs)
            print("Handler still working")
            await asyncio.sleep(30)



if __name__ == "__main__":
    token = load_token()
    bot = ChannelBot()
    bot.run(token)