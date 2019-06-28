<img src="https://cdn.discordapp.com/attachments/593508805812420649/594278579273990145/hack_wump_ship.png">

Channel bot is a quick and dirty bot made for Discord Hack Week 2019.

## Description

Channel bot creates text channels only visible to people in the corresponding voice channels. This way the people in voice chat can share stuff with each other, and those without mics can talk using text. However, if you are not in the voice channel, you won't be pinged about stuff you have no context for.  
**Note:** if you have the `Manage Channels` permission, you will be able to see the channels even though they are "hidden".

## Commands

`!cb help` -- lists these possible commands. You get more details about the commands by running them without the parameter.  
`!cb delete [min]` -- sets the minutes after which an empty voice-text channel is deleted.  
`!cb clear [min]` -- sets the minutes after which an empty voice-text channel is cleared (good if you want to manually set a category or position for the channel).  
`!cb minimum [num]` -- sets the minimum number of members needed in a voice chat for a text channel to be created.  
 **Note:** You will need the `Manage Channels` permission in order to use commands.

## Permissions required

`Manage Roles` -- managing for whom a text channel is visible is handled with roles.  
`Manage Channels` -- bot needs this in order to create and delete channels.  
`Send Messages` -- for sending help messages.  
`Manage Messages` -- required in order for the bot to clear a channel.  
`Read Message History` -- required for clearing a channel.  
`Add Reactions` -- bot uses reactions to show successful commands.  

## Invite

<a href="https://discordapp.com/api/oauth2/authorize?client_id=593505426956615701&permissions=268511312&scope=bot"> Invite the bot to your server. </a>