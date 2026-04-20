import discord, datetime

def fetch_variables(text:str,member:discord.Member=None,guild:discord.Guild=None):
    if not text:
        return None
    if member:
        text = text.replace("{user}",member.display_name)
        text = text.replace("{user.id}",str(member.id))
        text = text.replace("{user.tag}",member.discriminator)
        text = text.replace("{user.mention}",member.mention)
        text = text.replace("{user.avatar}",member.display_avatar.url)
        text = text.replace("{user.created_at}",f"<t:{int(member.created_at.timestamp())}:R>")
        text = text.replace("{user.joined_at}",f"<t:{int(member.joined_at.timestamp())}:R>")
    if guild:
        text = text.replace("{guild}",guild.name)
        text = text.replace("{server}",guild.name)
        text = text.replace("{server.id}",str(guild.id))
        text = text.replace("{server.icon}",guild.icon.url) if guild.icon else text
        text = text.replace("{guild.id}",str(guild.id))
        text = text.replace("{guild.icon}",guild.icon.url) if guild.icon else text
        text = text.replace("{guild.owner}",guild.owner.display_name)
        text = text.replace("{guild.owner.id}",str(guild.owner.id))
        text = text.replace("{member.count}",str(guild.member_count))
    
    # replace {time} with current time in HH:MM:SS 23:59:59 UTC
    text = text.replace("{time}",f"{datetime.datetime.utcnow().strftime('%H:%M:%S %d-%m-%Y')} UTC")
    # replace \n with new line
    text = text.replace(r"\n","\n")
    return text
