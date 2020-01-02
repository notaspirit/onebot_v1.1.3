import discord as dc
from discord.ext import commands
import asyncio
import json


with open("config.json", "r") as f:
    jsonconfig = json.load(f)


prefix = jsonconfig["prefix"]
version = jsonconfig["version"]
bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")
red = 0xff0000
yellow = 0xffff00
green = 0x00FF00

def str_to_bool(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise ValueError

def list_to_string(list_, new_line):
    if new_line == False:
        s = ""
        c = 0
        for i in list_:
            c += 1
            if c == len(list_):
                s += i + " "
            else:
                s += i
        return s
    else:
        s = ""
        c = 0
        for i in list_:
            c += 1
            if c == len(list_):
                s += i + "\n"
            else:
                s += i
        return s

@bot.event
async def on_ready():
    await bot.change_presence(activity=dc.Game(name="{}help | v{}".format(prefix, version)))
    print("Logged in!")
    print("Prefix: " + prefix)
    print("Bot Version: " + version)
    print("Libary Version: " + dc.__version__)


def get_user_json(userid, key):
    with open("userdatabase.json", "r") as f:
        userdata = json.load(f)
    return userdata[str(userid)][key]


def change_user_json(userid, key, new_value):
    with open("userdatabase.json", "r") as f:
        userdata = json.load(f)
    userdata[str(userid)][key] = [new_value]

@bot.event
async def on_member_join(member):
    role = dc.utils.get(member.guild.roles, id=581989047753506846)
    user_json_default = {
        str(member.id): {
            "customroleid": None,
            "warns": 0,
            "kicks": 0,
            "admin": False,
            "dev": False,
            "lostperm": False,
            "bday": None,
            "realname": None,
            "premium": False
            }
        }
    await member.add_roles(role)
    with open("userdatabase.json", "r") as f:
        data = json.load(f)
    data.update(user_json_default)
    with open("userdatabase.json", "w") as f:
        json.dump(data, f, indent=2)


async def userinfo(message):
    async def makeembed(user):
        e = dc.Embed(title="Informationen über {}".format(str(user)), color=yellow)
        e.add_field(name="Username", value=str(user), inline=False)
        e.add_field(name="Userid", value=str(user.id), inline=False)
        e.add_field(name="Customroleid", value=str(get_user_json(userid=user.id, key="customroleid")), inline=False)
        e.add_field(name="Administrator", value=str(get_user_json(userid=user.id, key="admin")), inline=False)
        e.add_field(name="Developer", value=str(get_user_json(userid=user.id, key="dev")), inline=False)
        e.add_field(name="LostPermissions", value=str(get_user_json(userid=user.id, key="lostperm")), inline=False)
        e.add_field(name="Geburtstag", value=str(get_user_json(userid=user.id, key="bday")), inline=False)
        e.add_field(name="Echter Name", value=str(get_user_json(userid=user.id, key="realname")), inline=False)
        e.add_field(name="Premium", value=str(get_user_json(userid=user.id, key="premium")), inline=False)
        await message.channel.send(embed=e)

    if message.mentions:
        await makeembed(user=message.mentions[0])
    else:
        await makeembed(user=message.author)

   
async def change_user_perms(message):
    if message.mentions:
        if get_user_json(userid=message.author.id, key="admin") == True:
            user = message.mentions[0]
            if len(message.content.split(" ")) >= 3:
                key = message.content.split(" ")[2]
                new_value_raw = message.content.split(" ")[3]
                with open("userdatabase.json", "r") as f:
                    data = json.load(f)
                perms = ["admin", "dev", "lostperm", "noping", "premium"]
                new_value = str_to_bool(s=new_value_raw)
                if key in perms:
                    if key == "masterperk":
                        data[str(user.id)]["perks"]["masterperk"] = new_value
                    else:
                        data[str(user.id)][key] = new_value
                
                    with open("userdatabase.json", "w") as f:
                        json.dump(data, f, indent=2)
                    e = dc.Embed(title="Erfolg!", description="Die Permission `{}` wurde erfolgreich auf `{}` gesetzt!".format(key, new_value), color=green)
                    await message.channel.send(embed=e)
                else:
                    e = dc.Embed(title="Fehler!", description="Ungültige Permission! Mögliche Permissions `admin, dev, lostperm, noping, premium`", color=red)
                    await message.channel.send(embed=e)
            else:
                e = dc.Embed(title="Fehler!", description="Fehlende Argumente! Die richtige Verwendung ist `o.change_user_perms <user> <perm> <new_value>`", color=red)
                await message.channel.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
            await message.channel.send(embed=e)
    else:
        e = dc.Embed(title="Fehler!", description="Es muss ein User erwähnt werden!", color=red)
        await message.channel.send(embed=e)


async def customrole(message):
    if len(message.content.split(" ")) > 1:
        if message.content.split(" ")[1] == "give":
            if get_user_json(userid=message.author.id, key="admin") == True:
                if message.mentions:
                    userid = message.mentions[0].id
                    username = message.mentions[0].name
                    user = message.guild.get_member(userid)
                    if get_user_json(userid=userid, key="customroleid") == None:
                        new_role = await message.guild.create_role(name="Customrole von `{}`".format(username),  mentionable=True, hoist=True)
                        await user.add_roles(new_role)
                        with open("userdatabase.json", "r") as f:
                            data = json.load(f)
                        
                        data[str(userid)]["customroleid"] = new_role.id

                        with open("userdatabase.json", "w") as f:
                            json.dump(data, f, indent=2)
                        
                        e = dc.Embed(title="Erfolg!", description="Es wurde die Customrole für `{}` erstellt!".format(username), color=green)
                        await message.channel.send(embed=e)
                    else:
                        e = dc.Embed(title="Fehler!", description="`{}` hat bereits eine Customrole!".format(username), color=red)
                        await message.channel.send(embed=e)
                else:
                    e = dc.Embed(title="Fehler!", description="Du musst einen User erwähnen!", color=red)
                    await message.channel.send(embed=e)
            else:
                e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
                await message.channel.send(embed=e)
        elif message.content.split(" ")[1] == "remove":
            if get_user_json(userid=message.author.id, key="admin") == True:
                if message.mentions:
                    userid = message.mentions[0].id
                    username = message.mentions[0].name
                    user = message.guild.get_member(userid)
                    if not get_user_json(userid=userid, key="customroleid") == None:
                        role = dc.utils.get(message.guild.roles, id=get_user_json(userid=userid, key="customroleid"))
                        await role.delete()
                        with open("userdatabase.json", "r") as f:
                            data = json.load(f)
                        
                        data[str(userid)]["customroleid"] = None

                        with open("userdatabase.json", "w") as f:
                            json.dump(data, f, indent=2)
                        e = dc.Embed(title="Erfolg!", description="Die Customrole von `{}` wurde erfolgreich gelöscht!".format(username), color=green)
                        await message.channel.send(embed=e)
                    else:
                        e = dc.Embed(title="Fehler!", description="`{}` hat keine Customrole!".format(username), color=red)
                        await message.channel.send(embed=e)
                else:
                    e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
                    await message.channel.send(embed=e)
            else:
                e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
                await message.channel.send(embed=e)
        elif message.content.split(" ")[1] == "rename":
            if not get_user_json(userid=message.author.id, key="customroleid") == None:
                if len(message.content.split(" ")) > 2:
                    new_name = ""
                    c = 0
                    for a in message.content.split(" "):
                        c += 1
                        if a == "o.customrole":
                            pass
                        elif a == "rename":
                            pass
                        else:
                            if c == len(message.content.split(" ")):
                                new_name += a
                            else:
                                new_name += a + " "

                    role = dc.utils.get(message.guild.roles, id=get_user_json(userid=message.author.id, key="customroleid"))
                    s = False
                    try:
                        await role.edit(name=new_name)
                        s = True
                    except Exception as exc:
                        e = dc.Embed(title="Fehler!", description="Folgender Fehler ist aufgetreten: `{}`".format(str(exc)), color=red)
                        await message.channel.send(embed=e)
                    if s == True:
                        e = dc.Embed(title="Erfolg!", description="Der Name deiner Customrole wurde auf `{}` geändert!".format(new_name), color=green)
                        await message.channel.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="`{}` ist kein gültiges Argument!".format(str(message.content.split(" ")[1])))
            await message.chanenl.send(embed=e)
    else:
        e = dc.Embed(title="Fehler!", description="Es muss mindestens ein Argument angegeben werden!", color=red)
        await message.channel.send(embed=e)


async def lost(message):
    if message.content.startswith("{}lostcounter".format(prefix)):
        with open("cmdconfig.json", "r") as f:
            data = json.load(f)
        e = dc.Embed(title="Lostcounter", description="Der Lostcounter beträgt `{}`".format(str(data["lost"]["counter"])), color=yellow)
        await message.channel.send(embed=e)
    elif message.content.startswith("{}lostclear".format(prefix)): 
        if get_user_json(userid=message.author.id, key="lostperm")  == True:
            with open("cmdconfig.json", "r") as f:
                data = json.load(f)
            data["lost"]["counter"] = 0
            with open("cmdconfig.json", "w") as f:
                json.dump(data, f, indent=2)

            e = dc.Embed(title="Erfolg!", description="Der Lostcounter wurde auf `0` zurückgesetzt!", color=green)
            await message.channel.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
            await message.channel.send(embed=e)

    elif message.content.startswith("{}lost".format(prefix)): 
        if get_user_json(userid=message.author.id, key="lostperm")  == True:
            with open("cmdconfig.json", "r") as f:
                data = json.load(f)
            data["lost"]["counter"] += 1
            with open("cmdconfig.json", "w") as f:
                json.dump(data, f, indent=2)

            e = dc.Embed(title="Erfolg!", description="Ein Lost wurde erfolgreich hinzugefügt! Der Lostcounter beträgt nun `{}`".format(str(data["lost"]["counter"])) ,color=green)
            await message.channel.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
            await message.channel.send(embed=e)


async def todo(message):
    if get_user_json(userid=message.author.id, key="admin") == True or get_user_json(userid=message.author.id, key="dev") == True:
        if len(message.content.split(" ")) == 1:
            with open("cmdconfig.json", "r") as f:
                data = json.load(f)
            e = dc.Embed(title="Todo Liste", description="Die Todoliste beinhaltet `{}`".format(list_to_string(list_=data["todo"], new_line=True)), color=yellow)
            await message.channel.send(embed=e)
        elif message.content.split(" ")[1] == "add":
            if len(message.content.split(" ")) >= 3:
                with open("cmdconfig.json", "r") as f:
                    data = json.load(f)
                todo_new = ""
                c = 0
                for i in message.content.split(" "):
                    c += 1
                    if c == 1 or c == 2:
                        pass
                    else:
                        if c == len(message.content.split(" ")):
                            todo_new += i
                        else:
                            todo_new += i + " "
                data["todo"].append(todo_new)
                with open("cmdconfig.json", "w") as f:
                    json.dump(data, f, indent=2)
                e = dc.Embed(title="Erfolg!", description="`{}` wurde hinzugefügt!".format(todo_new), color=green)
                await message.channel.send(embed=e)
            else:
                e = dc.Embed(title="Fehler!", description="Du musst ein Todo Namen angeben!", color=red)
                await message.channel.send(embed=e)
        elif message.content.split(" ")[1] == "remove":
            if len(message.content.split(" ")) >= 3:
                with open("cmdconfig.json", "r") as f:
                    data = json.load(f)
                rtodo = ""
                c = 0
                for i in message.content.split(" "):
                    c += 1
                    if c == 1 or c == 2:
                        pass
                    else:
                        if c == len(message.content.split(" ")):
                            rtodo += i
                        else:
                            rtodo += i + " "
                s = False
                try:
                    data["todo"].remove(rtodo)
                    s = True
                except Exception as exc:
                    e = dc.Embed(title="Fehler!", description="Folgender Fehler ist aufgetretten `{}`".format(str(exc)), color=red)
                    await message.channel.send(embed=e)
                if s == True:
                    with open("cmdconfig.json", "w") as f:
                        json.dump(data, f, indent=2)
                    e = dc.Embed(title="Erfolg!", description="`{}` wurde entfernt!".format(rtodo), color=green)
                    await message.channel.send(embed=e)
            else:
                e = dc.Embed(title="Fehler!", description="Du musst ein Todo Namen angeben!", color=red)
                await message.channel.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="`{}` ist kein gültiges Argument!".format(str(message.content.split(" ")[1])))
            await message.chanenl.send(embed=e)

    else:
        e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
        await message.channel.send(embed=e)

@bot.event
async def on_message(message):
    if message.content.startswith("{}userinfo".format(prefix)):
        await userinfo(message=message)
    elif message.content.startswith("{}change_user_perms".format(prefix)):
        await change_user_perms(message=message)    
    elif message.content.startswith("{}customrole".format(prefix)):
        await customrole(message=message)
    elif message.content.startswith("{}lost".format(prefix)) or message.content.startswith("{}lostcounter".format(prefix)):
        await lost(message=message)
    elif message.content.startswith("{}todo".format(prefix)):
        await todo(message=message)
    
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    reaction = payload.emoji
    n_msg_id = 661728874769678408
    p_msg_id = 661728941689536522
    if payload.message_id == n_msg_id:
        await user.add_roles(dc.utils.get(user.guild.roles, name=reaction.name))
        e = dc.Embed(title="Erfolg!", description="Deine Farbe wurde aktualisiert! Falls deine neue Farbe nicht angezeigt wird überprüfe ob dies die einzigste Reaktion ist oder wende dich an den Support!", color=green)
        await user.send(embed=e)
    elif payload.message_id == p_msg_id:
        if get_user_json(userid=user.id, key="premium") == True:
            await user.add_roles(dc.utils.get(user.guild.roles, name=reaction.name))
            e = dc.Embed(title="Erfolg!", description="Deine Farbe wurde aktualisiert! Falls deine neue Farbe nicht angezeigt wird überprüfe ob dies die einzigste Reaktion ist oder wende dich an den Support!", color=green)
            await user.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="Du benötigst Premium um diese Farbe zuverwenden!", color=red)
            await user.send(embed=e)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    reaction = payload.emoji
    n_msg_id = 661728874769678408
    p_msg_id = 661728941689536522
    if payload.message_id == n_msg_id or payload.message_id == p_msg_id:
        role = dc.utils.get(guild.roles, name=reaction.name)
        if role in user.roles:
            await user.remove_roles(role)
            e = dc.Embed(title="Erfolg!", description="Deine Farbrolle wurde erfolgreich entfernt!", color=green)
            await user.send(embed=e)
        else:
            e = dc.Embed(title="Fehler!", description="Du hattest diese Farbrolle nicht!", color=red)
            await user.send(embed=e)


@bot.command()
async def comingsoon(ctx):
    msg = ctx.message
    with open("cmdconfig.json", "r") as f:
        cmdconfig = json.load(f)
    def perm_check():
        userid = ctx.message.author.id
        if get_user_json(userid=userid, key="admin") == True:
            return True
        elif get_user_json(userid=userid, key="dev") == True:
            return True
        else:
            return False
    if len(msg.content.split(" ")) > 1:
        if perm_check() == True:
            if msg.content.split(" ")[1] == "add":
                if len(msg.content.split(" ")) > 2:
                    if msg.content.find("|"):
                        s = False
                        try:
                            name = msg.content.split("|")[0].replace(prefix + "comingsoon add", "")
                            progress = int(msg.content.split("|")[1])
                            print("true")
                            s = True
                        except:
                            embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon add <Name> | <Value>`".format(prefix), color=red) 
                            await ctx.send(embed=embed)

                        if s == True:
                            if progress > 100:
                                embed = dc.Embed(title="Fehler!", description="Der Progess muss kleiner als 100 sein!", color=red)
                                await ctx.send(embed=embed)
                            else:
                                embed = dc.Embed(title="Erfolg!", description="`{}` wurde erfolgreich mit dem Wert `{}` erstellt!".format(name, progress), color=green)
                                await ctx.send(embed=embed)

                                with open("cmdconfig.json", "r") as f:
                                    data = json.load(f)
                                
                                data["comingsoon"][name.replace(" ", "")] = progress
                                with open("cmdconfig.json", "w") as f:
                                    json.dump(data, f, indent=2)
                    else:
                        embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon add <Name> | <Value>`".format(prefix), color=red) 
                        await ctx.send(embed=embed)
                else:
                    embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon add <Name> | <Value>`".format(prefix), color=red) 
                    await ctx.send(embed=embed)                  
            elif  msg.content.split(" ")[1] == "remove":
                if perm_check() == True:
                    if len(msg.content.split(" ")) > 2:
                        key = ""
                        c = 0
                        
                        for arg in msg.content.split(" "):
                            if arg == "o.comingsoon":
                                pass
                            elif arg == "remove":
                                pass
                            else:
                                c += 1
                                if c == len(msg.content.split(" "))-2:
                                    key += "{}".format(arg)
                                else:
                                    key += "{} ".format(arg)

                        embed = dc.Embed(title="Erfolg!", description="Folgenes Comingsoon Event wurde entfernt: `{}`".format(key), color=green)              
                        with open("cmdconfig.json", "r") as f:
                            data = json.load(f)
                        try:
                            data["comingsoon"].pop(key)    
                        except:
                            embed = dc.Embed(title="Fehler!", description="`{}` konnte nicht gefunden werden!".format(key), color=red)        
                        with open("cmdconfig.json", "w") as f:
                            json.dump(data, f, indent=2)
                        
                        await ctx.send(embed=embed)

            elif  msg.content.split(" ")[1] == "update":
                if perm_check() == True:
                    if len(msg.content.split(" ")) > 2:
                        if msg.content.find("|"):
                            s = False
                            try:
                                name = msg.content.split("|")[0].replace(prefix + "comingsoon update", "")
                                progress = int(msg.content.split("|")[1])
                                s = True
                            except:
                                embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon add <Name> | <Value>`".format(prefix), color=red) 
                                await ctx.send(embed=embed)
                            if s == True:
                                if progress > 100:
                                    embed = dc.Embed(title="Fehler!", description="Der Progess muss kleiner als 100 sein!", color=red)
                                    await ctx.send(embed=embed)
                                else:
                                    embed = dc.Embed(title="Erfolg!", description="`{}` wurde erfolgreich mit dem Wert `{}` gesetzt!".format(name, progress), color=green)
                                    await ctx.send(embed=embed)

                                    with open("cmdconfig.json", "r") as f:
                                        data = json.load(f)
                                    
                                    data["comingsoon"][name.replace(" ", "")] = progress
                                    print(data)
                                    with open("cmdconfig.json", "w") as f:
                                        json.dump(data, f, indent=2)
                        else:
                            embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon add <Name> | <Value>`".format(prefix), color=red) 
                            await ctx.send(embed=embed)
                    else:
                        embed = dc.Embed(title="Fehler!", description="Die Richtige verwendung ist `{}comingsoon update <Name> | <Value>`".format(prefix), color=red) 
                        await ctx.send(embed=embed)
        else:
            embed = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
            await ctx.send(embed=embed)
    else:
        embed = dc.Embed(title="Comingsoon", description="Folgende Features sind derzeit geplant:", color=yellow)
        for key in cmdconfig["comingsoon"]:
            value = int(int(cmdconfig["comingsoon"][key])/10)
            progress = ""
            for _ in range(value):
                progress += "█"
            for _ in range(10-value):
                progress += "░"
            embed.add_field(name=key, value="[{} | {}%]".format(progress, cmdconfig["comingsoon"][key]))
        await ctx.send(embed=embed)
    
@bot.command()
async def say(ctx):
    if len(ctx.message.content.split(" ")) < 3:
        embed = dc.Embed(title="Fehler!", description="Die richtige Verwendung ist `{}say <title> | <value> OPTIONAL: $ <title2> | <value2> ...`!".format(prefix), color=red)
        await ctx.send(embed=embed)
    else:
        if ctx.message.content.find("|"):
            if ctx.message.content.find("$"):
                title = ctx.message.content.split("|")[0].replace("o.say", "")
                sp = ctx.message.content.split("$")
                value = sp[0].split("|")[1]
                embed = dc.Embed(title=title, description=value, color=ctx.author.color)
                first = True
                for l in sp:
                    if first == True:
                        first = False
                    else:
                        embed.add_field(name=l.split("|")[0], value=l.split("|")[1], inline=False)
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)
            else:
                title = ctx.message.content.split("|")[0].replace("o.say", "")
                value = ctx.message.content.split("|")[1]
                embed = dc.Embed(title=title, description=value, color=ctx.author.color)
                await ctx.channel.purge(limit=1)
                botmsg = await ctx.send(embed=embed)
                with open("embeds.json", "r") as f:
                    data = json.load(f)
                data.update({botmsg.id:ctx.author.id})
                with open("embeds.json", "w") as f:
                    json.dump(data, f, indent=2)     
        else:
            embed = dc.Embed(title="Fehler!", description="Die richtige Verwendung ist `{}say <title> | <value> OPTIONAL: $ <title2> | <value2> ...`!".format(prefix), color=red)
            await ctx.send(embed=embed)


@bot.command()
async def birthday(ctx):
    with open("userdatabase.json", "r") as f:
        data = json.load(f)
    if len(ctx.message.content.split(" ")) > 1:
        data[str(ctx.message.author.id)]["bday"] = ctx.message.content.split(" ")[1]
        e = dc.Embed(title="Erfolg!", description="Dein Geburtstag wurde erfolgreich auf {} aktualisiert!".format(ctx.message.content.split(" ")[1]), color=green)
        await ctx.send(embed=e)
    else:
        e = dc.Embed(title="Fehler!", description="Du musst deinen Geburtstag angeben!", color=red)
        await ctx.send(embed=e)
    with open("userdatabase.json", "w") as f:
        json.dump(data, f, indent=2)


@bot.command()
async def realname(ctx):
    with open("userdatabase.json", "r") as f:
        data = json.load(f)
    if len(ctx.message.content.split(" ")) > 1:
        data[str(ctx.message.author.id)]["realname"] = ctx.message.content.split(" ")[1]
        e = dc.Embed(title="Erfolg!", description="Dein echter Name wurde erfolgreich auf {} aktualisiert!".format(ctx.message.content.split(" ")[1]), color=green)
        await ctx.send(embed=e)
    else:
        e = dc.Embed(title="Fehler!", description="Du musst deinen echten Namen angeben!", color=red)
        await ctx.send(embed=e)
    with open("userdatabase.json", "w") as f:
        json.dump(data, f, indent=2)

@bot.command()
async def help(ctx):
    with open("help.json", "r") as f:
        data = json.load(f)
    e = dc.Embed(title="Help", color=yellow)
    for key in data["help"]:
        e.add_field(name=key, value=data["help"][key], inline=False)
    await ctx.send(embed=e)

@bot.command()
async def restart(ctx):
    if get_user_json(userid=ctx.author.id, key="admin") == True or get_user_json(userid=ctx.author.id, key="dev") == True:
        import sys
        e = dc.Embed(title="Erfolg!", description="Der Bot wird neu gestartet!", color=green)
        await ctx.send(embed=e)
        import os
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        e = dc.Embed(title="Fehler!", description="Du hast keine Berechtigung für diesen Befehl!", color=red)
        await ctx.send(embed=e)

@bot.command()
async def info(ctx):
    e = dc.Embed(title="Informationen über diesen Bot", color=yellow)
    e.add_field(name="Version", value=version, inline=False)
    await ctx.send(embed=e)

bot.run(jsonconfig["token"])



