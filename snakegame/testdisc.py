import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get
from discord.ext.commands import has_permissions
from itertools import cycle
import datetime
import random
import os
from dotenv import load_dotenv
import asyncio
import time
import json
from os.path import dirname, realpath, isfile


class json_gerenciar():
    def __init__(self):
        self.path = dirname(realpath(__file__)) + '/'
    
    def criar_json(self, file):
        data = {"ids": []}
        path_data = self.path + file
        if not isfile(path_data):
            with open(path_data, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        else:
            return False
        
    def ler_json(self, file):
        if isfile(self.path + file):
            with open(self.path + file, "r") as b:
                data = json.load(b)
            return data
        else:
            return False
    def adicionar_json(self, file, nome='ids', append=0):
        if isfile(self.path + file):
            with open(self.path + file, "r") as b:
                data = json.load(b)
            data[nome].append(append)
            print(data)
            with open(self.path + file, "w") as o:
                json.dump(data, o, indent=4)

jfile = json_gerenciar()
jfile.criar_json('messageid.json')
#prefixo de comando.
client = commands.Bot(command_prefix = '>')
#remover o comando help padrão do bot.
client.remove_command('help')
#criar um ciclo de status para o que o bot esta jogando.
status = cycle(['Para obter ajuda: >ajuda', 'Coe rapazeada', 'Me convide para seus servidores!'])

@client.event
async def on_ready():
    mudar_status.start()
    print('bot online!')



#envia o error para o chat.
@client.event
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
       await ctx.send('```Comando não existe```')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('```Você não pode executar esse comando devido a falta de permissão neste servidor```')
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send('```O bot não pode executar esse comando devido a falta de permissão neste servidor```')

#quando a mensage cujo o id esta no arquivo que ira ser criado a o iniciar o codigo sera adicionado um cargo com nome da reação, emoji.
@client.event
async def on_raw_reaction_add(payload):
    message = payload.message_id
    for msgid in jfile.ler_json('messageid.json')['ids']:
        if int(msgid) == int(message):
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
            role = discord.utils.get(guild.roles, name=payload.emoji.name)
        
            if role is not None:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.add_roles(role)
                else:
                    print('error')
            else:
                print('error2')

#quando a mensage cujo o id esta no arquivo que ira ser criado a o iniciar o codigo sera remover um cargo com nome da reação, emoji.
@client.event
async def on_raw_reaction_remove(payload):
    message = payload.message_id
    for msgid in jfile.ler_json('messageid.json')['ids']:
        if int(msgid) == int(message):
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
            role = discord.utils.get(guild.roles, name=payload.emoji.name)
        
            if role is not None:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role)
                else:
                    print('error')
            else:
                print('error2')


#loop de 10 segundos para trocar o que o bot esta jogando.
@tasks.loop(seconds=10)
async def mudar_status():
    await client.change_presence(activity=discord.Game(next(status)))

#comando de ajuda com comandos, caso trocar o prefixo mude aqui pros usuarios saberem usar.
@client.command(aliases=['help'])
async def ajuda(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title="Ajuda",
    colour=discord.Colour(0xb185),
    description="""Comandos:
```\n Comandos usuário:

- >ajuda, Exibe a ajuda com comandos.

- >ping, Exibe a velocidade de sua conexão em Ms.

- >userinfo @usuário, Exibe algumas irformações sobre o usuario marcado.

 Comandos moderacão:

- >limpar quantidade, ira limpar as mensagens anteriores de acordo com o definido, quantidade padrão (5), necessita que o author tenha de permissão de Gerenciar mensagens.

- >expulsar @membro razão, expulsara o membro marcado pela razão escrita, necessita que o author tenha de permissão de Expulsar membros.

- >banir @membro razão, ira banir o membro marcado pela razão escrita, necessita que o author tenha de permissão de Banir membros.

- >desbanir nome#0000, ira desbanir a pessoa que for colocado o nome e o # dela, necessita que o author tenha de permissão de Banir membros.

- >renomear nome, ira renomear o nome do canal atual para o nome que você escrever, necessita que o author tenha de permissão de Gerenciar canais.

- >topico topico, ira por o topico que escrever, necessita que o author tenha de permissão de Gerenciar canais.

- >lento 0 a 21600, ira por o modo chat lento no canal com o tempod de escrita sendo o valor em segundos que você inserir, necessita que o author tenha de permissão de Gerenciar canais.

- >diga mensagem, comando apenas para donos o BOT fala o que você quiser```""")



    embed.set_thumbnail(url=f"{ctx.guild.icon_url}")

    await ctx.send(embed=embed)


#Exibe a velocidade de sua conexão em Ms.
@client.command()
async def ping(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.send(f'```Seu ping é de: {round(client.latency * 1000)}ms```')

#userinfo @usuário, Exibe algumas irformações sobre o usuario marcado.
@client.command(aliases=['userinfo', 'user-info'])
async def user_info(ctx, user: discord.Member):
    await ctx.channel.purge(limit=1)
    boost = user.premium_since
    perm = discord.Permissions(permissions=user.guild_permissions.value) #pega o valor das permissions
    permissoes = ''
    ustatus = ''
    moderador = False
    administrador = False
    if ctx.guild.owner.id == user.id:
        ustatus += 'dono do servidor\n'
    if perm.administrator:
        permissoes += 'administrador'
        administrador = True #permite o status de administrador
        moderador = True #permite o status de moderador
    else:
        if perm.create_instant_invite:
            permissoes += 'criar convites\n'
        if perm.kick_members:
            permissoes += 'expulsar\n'
            moderador = True
        if perm.ban_members:
            permissoes += 'banir\n'
            moderador = True
        if perm.manage_channels:
            permissoes += 'gerenciar canais\n'
            moderador = True
        if perm.manage_messages:
            permissoes += 'gerenciar mensagens\n'
            moderador = True
        if perm.manage_guild:
            permissoes += 'gerenciar servidor\n'
            moderador = True
            administrador = True
        if perm.add_reactions:
            permissoes += 'adicionar reações\n'
        if perm.view_audit_log:
            permissoes += 'visualizar log de auditoria\n'
        if perm.attach_files:
            permissoes += 'adicionar arquivos\n'
        if perm.view_guild_insights:
            permissoes += 'ver informações da guilda\n'
        if perm.mute_members:
            permissoes += 'mutar membros\n'
            moderador = True
        if perm.deafen_members:
            permissoes += 'ensurdecer membros\n'
            moderador = True
        if perm.move_members:
            permissoes += 'mover membros\n'
            moderador = True
        if perm.manage_nicknames:
            permissoes += 'gerenciar apilidos\n'
            moderador = True
        if perm.manage_roles:
            permissoes += 'gerenciar cargos\n'
            moderador = True
        if perm.manage_emojis:
            permissoes += 'gerenciar emojis\n'
    if moderador:
        ustatus += 'moderador do server\n'
    if administrador:
        ustatus += 'admin do servidor\n'
    if True:
        ustatus += 'normal\n'

    if str(boost) == 'None':
        boost = 'sem boost'
    embed = discord.Embed(colour=discord.Colour(0x1))

    embed.set_author(name=f"{client.user.name}", icon_url=f"{client.user.avatar_url}")
    embed.set_footer(text=f"Pedido por: {ctx.author} | {ctx.author.id}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url=user.avatar_url)

    embed.add_field(name=f"**informações de\n{user}**",
    value=f"**nome**\n_{user.name}_\n**descriminador**\n_{user.discriminator}_\n**id**\n{user.id}", inline=True)
    embed.add_field(name="**permissões**", value=f"{permissoes}", inline=True)
    embed.add_field(name="**Status do usuário**", value=f"{ustatus}", inline=True)
    embed.add_field(name="**entrou no servidor**", value=f"{user.joined_at}", inline=True)
    embed.add_field(name="**boost desde**", value=f"{boost}", inline=True)

    await ctx.send(content=f"{ctx.author.mention}", embed=embed)

#adicionar o id da mensagem no arquivo "messageid.json".
@client.command()
@commands.has_permissions(manage_roles=True)
async def rolemsgid(ctx, append: int):
    jfile.adicionar_json('messageid.json', append=append)
   
	
#mutar membros.
@client.command()
@commands.has_guild_permissions(mute_members=True)
async def mutar(ctx, user: discord.Member, tempo: int, operator:str = 's', *, razão:str = 'mutado'):
    print(str(operator)[0])
    if str(operator)[0] == str('s'):
        temporador = tempo
    elif str(operator)[0] == str('m'):
        temporador = tempo * 60
    elif str(operator)[0] =='h':
        temporador = tempo * 60 * 60
    elif str(operator)[0] == str('S'):
        temporador = tempo
    elif str(operator)[0] == str('M'):
        temporador = tempo * 60
    elif str(operator)[0] =='h':
        temporador = tempo * 60 * 60
    else:
        temporador = tempo

    roles = await ctx.guild.fetch_roles()
    count = False
    for role in roles:
        if role.name == "muted":
            count = True
        if count:
            role = role
    if not count:
        perms = discord.Permissions(speak=False, send_messages=False)
        muted = await ctx.guild.create_role(name='muted')
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted, send_messages=False,
												speak=False)


    role = discord.utils.get(ctx.guild.roles, name='muted')
    await user.add_roles(role, reason=razão)
    embed = discord.Embed(title="usuario mutado", colour=discord.Colour(0xf8db63), description=f"{user} foi mutado por: {razão}")
    embed.set_author(name=f"{client.user.name}", url="https://discordapp.com", icon_url=client.user.avatar_url)
    embed.add_field(name="tempo", value=f"{temporador}{operator}.", inline=True)
    embed.add_field(name="servidor", value=f"{ctx.guild}.", inline=True)

    if str(ctx.guild.system_channel) != 'none':
        await ctx.guild.system_channel.send(embed=embed)
    await ctx.send(embed=embed)

    await asyncio.sleep(temporador)

    embed = discord.Embed(title="usuario desmutado", colour=discord.Colour(0xf8db63), description=f"{user} foi desmutado por: o tempo acabou")
    embed.set_author(name=f"{client.user.name}", url="https://discordapp.com", icon_url=client.user.avatar_url)
    embed.add_field(name="servidor", value=f"{ctx.guild}.", inline=True)

    if str(ctx.guild.system_channel) != 'none':
        await ctx.guild.system_channel.send(embed=embed)
    await ctx.send(embed=embed)
    await user.remove_roles(role, reason='tempo acabou!')

#erros que podem acontecer no comando de mutar
@mutar.error
async def mutar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        print(error)
        if str(error) == 'user is a required argument that is missing.':
            await ctx.send('esqueceu de marcar o usuario')
        elif str(error) == 'tempo is a required argument that is missing.':
            await ctx.send('esqueceu de botar o tempo')
    elif isinstance(error, commands.ConversionError):
        if str(error) == 'Converting to "int" failed for parameter "tempo".':
            await ctx.send('falha ao converter o tempo para inteiro, use numeros')
    else: 
        print(error)

#comando para limpar chat reservado apenás pra quem tem a permissão de gerenciar mensagens, limpar quantidade.
@client.command()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, amount=6):
    await ctx.channel.purge(limit=amount)


#comando para expulsar usuarios reservado apenás pra quem tem a permissão de expulsar membros
@client.command()
@has_permissions(kick_members=True)
async def expulsar(ctx, user: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    await ctx.send(f'```diff\n-membro: {user}, foi Kickado\n Razão: <{reason}>. by @{ctx.message.author}```')
    await user.kick(reason=reason)


#comando para banir usuarios reservado apenás pra quem tem a permissão de banir membros, banir @membro razão.
@client.command()
@commands.has_permissions(ban_members=True)
async def banir(ctx, user: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    await ctx.send(f'```diff\n-membro: {user}, foi Banido\n Razão: <{reason}>. by @{ctx.message.author}```')
    await user.ban(reason=reason)


@client.command()
@commands.has_permissions(ban_members=True)
async def desbanir(ctx, *, member):
    usuario_banido = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for banido in usuario_banido:
        user = banido.  user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'unbanned {user.name}#{user.discriminator}')    


#esse comando altera o nome do canal
@client.command()
@commands.has_permissions(manage_channels=True)
async def renomear(ctx, *,nome:str):
    nome = nome.replace(' ', '-')
    await ctx.send(f'```diff\nlembrando que o bot necessita de permissão para executar esse processo\n-tentando: trocando o nome do canal para: {nome}\n```\n**processando...**')
    await ctx.send('__pode demorar um pouco as vezes__')
    await ctx.channel.edit(name=nome, reason=f'nome editado a pedido de {ctx.author}')
    await ctx.send(f'pronto! nome trocado para: {nome}')


#esse comando altera o topico do canal
@client.command()
@commands.has_permissions(manage_channels=True)
async def topico(ctx, *, topico:str):
    await ctx.send(f'```diff\nlembrando que o bot necessita de permissão para executar esse processo\n-tentando: trocando o topico do canal para:\n\n{topico}\n```\n**processando...**')
    await ctx.send('__pode demorar um pouco as vezes__')
    await ctx.channel.edit(topic=topico, reason=f'topico editado a pedido de {ctx.author}')
    await ctx.send(f'pronto! topico trocado para:\n{topico}\n```Concluido.```')


#esse comando altera o tempo para falar caso esteja 0 sera desativado para quem tem a permissao de gerenciar mensagens
@client.command()
@commands.has_permissions(manage_channels=True)
async def lento(ctx, tempo=0):
    tempo = int(tempo)
    await ctx.channel.edit(slowmode_delay=tempo)
    if tempo == 0:
        await ctx.send(f'Modo chat lento desativado!')
    else:
        await ctx.send(f'Modo chat lento com tempo de {tempo}!')


#isso e para o dono do bot escrever como o bot no chat
@client.command()
@commands.has_permissions(manage_channels=True)
async def diga(ctx, *, msg):
    await ctx.channel.purge(limit=1)
    await ctx.send(msg)                

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Olá {member.name}, Seja bem-vindo ao meu servidor!!'
    )

@client.command(pass_context=True)
async def hug(ctx, member: discord.Member):
    """Hug someone."""
    embed = discord.Embed(title="Abraço!", description="**{1}** Abraçou **{0}**!".format(member.name, ctx.message.author.name), color=0x176cd5)
    embed.set_thumbnail(url="https://media1.tenor.com/images/0be55a868e05bd369606f3684d95bf1e/tenor.gif?itemid=7939558")
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def slap(ctx, member: discord.Member):
    """Slap someone."""
    embed = discord.Embed(title="Tapa!", description="**{1}** Bateu em **{0}**!".format(member.name, ctx.message.author.name), color=0x176cd5)
    embed.set_image(url="https://loritta.website/assets/img/actions/slap/female_x_female/gif_196.gif")
    embed.set_image(url="https://loritta.website/assets/img/actions/slap/female_x_female/gif_203.gif")
    await ctx.send(embed=embed)


client.run('Token')
