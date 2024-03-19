import discord
import configparser
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.ext import tasks
import os
import sqlite3
from cogs.character import PassportModal, CompanyModal

config = configparser.ConfigParser()
config.read('config.ini')
postgres = config["postgresql"]
general = config["general"]
economy = config["economy"]


governmentSalaries = {'Полиция': 67000, 'ФСС': 68000, 'ТСФ': 78000, 'Солдат': 87000, 'Водитель': 59000}
governmentSalariesId = {'Полиция': 918543120298283060, 'ФСС': 918543158307070042, 'ТСФ': 1018470711850971176,
                        'Солдат': 918545314783309835, 'Водитель': 918543731634864208}

#conn = psycopg2.connect(host=postgres["host"], dbname=postgres["db"], user=postgres["user"], password=postgres["password"])
conn = sqlite3.connect('main.db')
curs = conn.cursor()

client = commands.Bot(command_prefix=general['prefix'], intents=discord.Intents.all()) # нахуя менять префикс было


@client.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):

            await client.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded Cog: {filename[:-3]}")
        else:
            print("Unable to load pycache folder.")


@client.event
async def on_ready():
    curs.execute(
        'CREATE TABLE IF NOT EXISTS company (id BIGINT, owner_name VARCHAR(255), company_type VARCHAR(255), company_name VARCHAR(255), whatitdoes VARCHAR(255));')
    conn.commit()
    for guild in client.guilds:

        for member in guild.members:

            curs.execute(f'SELECT user_id FROM money WHERE user_id = {member.id}')
            if curs.fetchone() is None:

                curs.execute(f'INSERT INTO money (user_id, wallet, bank) VALUES {(member.id, economy["startmoney"], 0)}')

                conn.commit()

            else:
                pass


@client.event
async def on_member_join(self, member):
    for guild in client.guilds:

        for member in guild.members:

            curs.execute(f'SELECT user_id FROM money WHERE user_id = {member.id}')
            if curs.fetchone() is None:

                curs.execute(
                    f'INSERT INTO money (user_id, wallet, bank) VALUES {(member.id, economy["startmoney"], 0)}')

                conn.commit()

            else:
                pass


@client.tree.command(name="passport",
                     description="Просмотр/Создание паспорта")
async def passport_m(interaction: discord.Interaction):
    curs.execute(f'SELECT * FROM passport WHERE discord = "{interaction.user}" ')
    data = curs.fetchone()
    try:
        name = data[1]
        birthdate = data[2]
        biography = data[3]
    except:
        name = None
        birthdate = None
        biography = None
    embed = discord.Embed(title='Ваш паспорт', color=0x00ff9d)
    embed.add_field(name="Фамилия Имя Отчество", value=name, inline=True)
    embed.add_field(name="Дата рождения", value=birthdate, inline=True)
    embed.add_field(name="Биография", value=biography, inline=False)
    if data == None:
        await interaction.response.send_modal(PassportModal())
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="company",
                      description="Команда для создания компании")
# Перед созданием компании проверить, есть ли у юзера нужная сумма для создания
async def company_m(interaction: discord.Interaction):
    curs.execute(f'SELECT * FROM company WHERE id = {interaction.user.id} ')
    data1 = curs.fetchone()
    print(data1)
    try:
        id = data1[0]
        owner_name = data1[1]
        company_type = data1[2]
        company_name = data1[3]
        whatitdoes = data1[4]
    except:
        id = None
        owner_name = None
        company_type = None
        company_name = None
        whatitdoes = None

    embed = discord.Embed(title=company_name, color=0x00ff9d)
    embed.add_field(name="Владелец(ы)", value=owner_name, inline=True)
    embed.add_field(name="Тип", value=company_type, inline=True)
    # embed.add_field(name="Название", value="3", inline=False)
    embed.add_field(name="Деятельность", value=whatitdoes, inline=False)
    if data1 == None:
        await interaction.response.send_modal(CompanyModal())
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

client.run(general["token"])
