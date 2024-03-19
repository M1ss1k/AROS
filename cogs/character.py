import configparser
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.utils import MISSING

# import psycopg2
import sqlite3

config = configparser.ConfigParser()
config.read('config.ini')
postgres = config["postgresql"]  # Данные от БД
general = config["general"]

# conn = psycopg2.connect(host=postgres["host"], dbname=postgres["db"], user=postgres["user"], password=postgres["password"])
conn = sqlite3.connect('main.db')
curs = conn.cursor()


class Character(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="character", description="Карточка вашего персонажа")
    async def character(self, interaction: discord.Interaction):

        curs.execute(f'SELECT * FROM passport WHERE discord = {interaction.user.id} ')
        data = curs.fetchone()
        try:
            name = data[1]
            birthdate = data[2]
            biography = data[3]
        except:
            name = None
            birthdate = None
            biography = None

        # -----Ембед для просмотра информации о персонаже-----#
        embed = discord.Embed(title='Ваш персонаж', color=0x00ff9d)
        embed.add_field(name="Фамилия Имя Отчество", value=name, inline=True)
        embed.add_field(name="Дата рождения", value=birthdate, inline=True)
        embed.add_field(name="Биография", value=biography, inline=False)

        if data == None:
            await interaction.response.send_modal(PassportModal(bot=self.bot))

        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)


# -----Регистрация персонажа (Модаль)-----#

class PassportModal(ui.Modal, title="Регистрация персонажа"):
    

    name = ui.TextInput(label="ФИО", placeholder="Иванов Иван Иванович",
                        style=discord.TextStyle.short)
    birthdate = ui.TextInput(label="Дата рождения персонажа", placeholder="01.01.1999", style=discord.TextStyle.short)
    biography = ui.TextInput(label="Биография персонажа. 5-7 предложений!", placeholder="...",
                             style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            'Вы успешно подали заявку! Информацию о ней вы сможете увидеть в личных сообщениях.', ephemeral=True)

        # -----Информирование о отправки заявки в ЛС-----#

        embed1 = discord.Embed(title='Сообщение от МВД Фестонского Королевства', color=0x00ff9d)
        embed1.add_field(name="", value="Вы успешно подали заявку на получение паспорта! Ожидайте принятия заявки.",
                         inline=False)
        embed1.add_field(name="Ваши паспортные данные которые вы указали в заявке",
                         value=f"**・ФИО ** \n {str(self.name)} \n **・Дата рождения ** \n {str(self.birthdate)} \n **・Биография ** \n {str(self.biography)}",
                         inline=False)

        # -----Информирование об одобрении заявки в ЛС-----#

        embed2 = discord.Embed(
            title='Уведомление от МВД Фестонского Королевства по поводу заявки на получение паспорта', color=0x00ff33)
        embed2.add_field(name="",
                         value="Ваша заявка на получение паспорта одобрена. Теперь вы полноценный резидент Фестонии!",
                         inline=False)

        # -----Информирование об отклонении заявки в ЛС-----#

        embed3 = discord.Embed(
            title='Уведомление от МВД Фестонского Королевства по поводу заявки на получение паспорта', color=0xff0000)
        embed3.add_field(name="",
                         value="Ваша заявка на получение паспорта, к сожалению, была отклонена. За подробностями пожалуйста пройдите в чат для нерезидентов для получения дополнительной информации.",
                         inline=False)

        # -----Ембед для отправления админам-----#

        embed = discord.Embed(color=0xfedc01)
        embed.add_field(name="Заявка на регистрацию персонажа от пользователя", value='', inline=False)
        embed.add_field(name="Человек подавший заявку", value=interaction.user.mention, inline=False)
        embed.add_field(name="Фамилия Имя Отчество", value=str(self.name), inline=True)
        embed.add_field(name="Дата рождения", value=str(self.birthdate), inline=True)
        embed.add_field(name="Биография", value=str(self.biography), inline=False)

        # -----Отправка всего говна-----#
        view = PassButtons(timeout=None, name=self.name, birthdate=self.birthdate, biography=self.biography,
                           user=interaction.user, aembed=embed2, cembed=embed3)

        channel = self.bot.get_channel(1076960652565938218)
        await channel.send(embed=embed, view=view)
        await interaction.user.send(embed=embed1)


# ----------------------------------------#
# -----Регистрация персонажа (Кнопки)-----#
# ----------------------------------------#

class PassButtons(discord.ui.View):

    def __init__(self, timeout, name, birthdate, biography, user, aembed, cembed):
        super().__init__()
        self.value = None
        self.timeout = timeout
        self.name = name
        self.birthdate = birthdate
        self.biography = biography
        self.user = user
        self.aembed = aembed
        self.cembed = cembed

    @discord.ui.button(label='Принять', style=discord.ButtonStyle.green)
    async def pb1(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='✅ Принятая заявка на регистрацию персонажа', color=0x00ff33)
        embed.add_field(name="Человек подавший заявку", value=self.user.mention, inline=False)
        embed.add_field(name="Администратор принявший заявку", value=interaction.user.mention, inline=False)
        embed.add_field(name="Фамилия Имя Отчество", value=str(self.name), inline=True)
        embed.add_field(name="Дата рождения", value=str(self.birthdate), inline=True)
        embed.add_field(name="Биография", value=str(self.biography), inline=False)
        accept_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Принять":
                accept_button = child
                child.disabled = True
                break
        cancel_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Отказ":
                cancel_button = child
                child.disabled = True
                break
        await interaction.response.edit_message(embed=embed, view=self)
        curs.execute(f""" INSERT INTO passport(discord,name,date,biography) 
                          VALUES( {self.user.id},'{self.name}','{self.birthdate}','{self.biography}' )""")
        conn.commit()
        await self.user.send(embed=self.aembed)
        self.value = False
        self.stop()

    @discord.ui.button(label='Отказ', style=discord.ButtonStyle.danger)
    async def pb2(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='❌ Отклонённая заявка на регистрацию персонажа', color=0xff0000)
        embed.add_field(name="Человек подавший заявку", value=self.user.mention, inline=False)
        embed.add_field(name="Администратор отклонивший заявку", value=interaction.user.mention, inline=False)
        embed.add_field(name="Фамилия Имя Отчество", value=str(self.name), inline=True)
        embed.add_field(name="Дата рождения", value=str(self.birthdate), inline=True)
        embed.add_field(name="Биография", value=str(self.biography), inline=False)
        accept_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Принять":
                accept_button = child
                child.disabled = True
                break
        cancel_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Отказ":
                cancel_button = child
                child.disabled = True
                break
        await interaction.response.edit_message(embed=embed, view=self)
        await self.user.send(embed=self.cembed)
        self.value = False
        self.stop()


class CompanyModal(ui.Modal, title="Регистрация ООО или ИП"):
    owner_name = ui.TextInput(label="ФИО владельца или владельцев", placeholder="Иванов Иван Иванович",
                              style=discord.TextStyle.short)
    company_type = ui.TextInput(label="Тип компании (ООО или ИП)", placeholder="ООО", style=discord.TextStyle.short)
    company_name = ui.TextInput(label="Название компании", placeholder="...", style=discord.TextStyle.short)
    whatitdoes = ui.TextInput(label="Деятельность компании", placeholder="Продажа товаров",
                              style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            'Вы успешно подали заявку! Информацию о ней вы сможете увидеть в личных сообщениях.', ephemeral=True)

        sql = ''' INSERT INTO company(id,owner_name,company_type,company_name,whatitdoes) VALUES(, ?, ?, ?, ?) '''
        params = (str(interaction.user), str(self.owner_name), str(self.company_name), str(self.company_type),
                  str(self.whatitdoes))

        view = CompanyButtons(sql=sql, params=params, owner_name=self.owner_name, company_type=self.company_type,
                              company_name=self.company_name, whatitdoes=self.whatitdoes, user=interaction.user,
                              userid=interaction.user.id)

        embed = discord.Embed(color=0xfedc01)
        embed.add_field(name="Заявка на получние ООО/ИП", value='', inline=False)
        embed.add_field(name="Владелец(ы)", value=str(self.owner_name), inline=False)
        embed.add_field(name="Тип", value=str(self.company_type), inline=True)
        embed.add_field(name="Название", value=str(self.company_name), inline=True)
        embed.add_field(name="Деятельность", value=str(self.whatitdoes), inline=False)

        channel = client.get_channel(1076960652565938218)
        await channel.send(embed=embed, view=view)


class CompanyButtons(discord.ui.View):
    def __init__(self, sql, params, owner_name, company_type, company_name, whatitdoes, user, userid):
        super().__init__()
        self.value = None
        self.sql = sql
        self.params = params
        self.owner_name = owner_name
        self.company_type = company_type
        self.company_name = company_name
        self.whatitdoes = whatitdoes
        self.user = user
        self.userid = userid

    @discord.ui.button(label='Принять', style=discord.ButtonStyle.green)
    async def pb1(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Проверка на наличии нужной суммы. В случае если нету - отказ
        # Есть - вычитание и далее что ниже

        embed = discord.Embed(title='✅ Принятая заявка на ООО/ИП', color=0x00ff33)
        embed.add_field(name="Человек подавший заявку", value=self.user.mention, inline=False)
        embed.add_field(name="Администратор принявший заявку", value=interaction.user.mention, inline=False)
        embed.add_field(name="Владелец(ы)", value=str(self.owner_name), inline=True)
        embed.add_field(name="Тип", value=str(self.company_type), inline=True)
        embed.add_field(name="Название", value=str(self.company_name), inline=False)
        embed.add_field(name="Деятельность", value=str(self.whatitdoes), inline=False)
        accept_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Принять":
                accept_button = child
                child.disabled = True
                break
        cancel_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Отказ":
                cancel_button = child
                child.disabled = True
                break
        await interaction.response.edit_message(embed=embed, view=self)
        curs.execute(f"""INSERT INTO company(id,owner_name,company_type,company_name,whatitdoes)"""
                     f"""VALUES({self.userid}, '{str(self.owner_name)}', '{str(self.company_type)}', '{str(self.company_name)}', '{str(self.whatitdoes)}')""")

        conn.commit()

        uemded = discord.Embed(title='✅ Заявка на регистрацию ООО/ИП', color=0x00ff33)
        uemded.add_field(name="",
                         value="Вашу заявку на регистрацию ООО/ИП успешно приняли! Пожалуйста придите в МВД Фестонского Королевства для получения документов! ")

        await self.user.send(embed=uemded)
        self.value = False
        self.stop()

    @discord.ui.button(label='Отказ', style=discord.ButtonStyle.danger)
    async def pb2(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='❌ Отклонённая заявка на ООО/ИП', color=0xff0000)
        embed.add_field(name="Человек подавший заявку", value=self.user.mention, inline=False)
        embed.add_field(name="Администратор принявший заявку", value=interaction.user.mention, inline=False)
        embed.add_field(name="Владелец(ы)", value=str(self.owner_name), inline=True)
        embed.add_field(name="Тип", value=str(self.company_type), inline=True)
        embed.add_field(name="Название", value=str(self.company_name), inline=False)
        embed.add_field(name="Деятельность", value=str(self.whatitdoes), inline=False)
        accept_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Принять":
                accept_button = child
                child.disabled = True
                break
        cancel_button = None
        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Отказ":
                cancel_button = child
                child.disabled = True
                break
        await interaction.response.edit_message(embed=embed, view=self)
        await self.user.send(embed=self.cembed)
        self.value = False
        self.stop()


# await interaction.response.send_message(f'НИК ДИСКОРД: {str(interaction.user)}\n ФИО: {str(self.name)}\n ДАТА РОЖДЕНИЯ: {str(self.birthdate)}\n БИОГРАФИЯ:{str(self.biography)}', ephemeral=True)


# Вызвов команды паспорт


# ----------------------------------------#
# -------------Загрузка кога--------------#
# ----------------------------------------#

async def setup(bot):
    await bot.add_cog(Character(bot))
