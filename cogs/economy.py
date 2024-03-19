import configparser
import discord
from discord.ext import commands
from discord import app_commands
#import psycopg2
import sqlite3
config = configparser.ConfigParser()
config.read('config.ini')
postgres = config["postgresql"]


governmentSalaries = {'Полиция': 67000, 'ФСС': 68000, 'ТСФ': 78000, 'Солдат': 87000, 'Водитель': 59000}
governmentSalariesId = {'Полиция': 918543120298283060, 'ФСС': 918543158307070042, 'ТСФ': 1018470711850971176,
                        'Солдат': 918545314783309835, 'Водитель': 918543731634864208}

#conn = psycopg2.connect(host=postgres["host"], dbname=postgres["db"], user=postgres["user"], password=postgres["password"])
conn = sqlite3.connect('main.db')
curs = conn.cursor()

class Economics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -- ЗАРПЛАТА ГОС_ВА --
    @commands.command(pass_context=True)
    @commands.has_role('Управление деньгами')
    async def salary_gov(self, ctx, role_name: str):
        # guild = 917341944424841236
        emb = discord.Embed(title=f'Выдача зарплаты с ролью {role_name}', colour=discord.Color.blue())
        try:
            role = discord.utils.get(ctx.guild.roles, id=governmentSalariesId[role_name])
        except:
            emb_Er = discord.Embed(title=f'Ошибка ❌', colour=discord.Color.red())
            emb_Er.add_field(name=f'Допущена ошибка в роли', value=f'Такой роли в списке государственных не существует')
            return await ctx.send(embed=emb_Er)
        count = 0
        for member in ctx.guild.members:
            if role in member.roles:
                curs.execute(f'SELECT bank FROM money WHERE user_id = {member.id}')
                sal = curs.fetchone()
                try:
                    bank_sal = sal[0]
                except:
                    bank_sal = 0
                curs.execute(
                    f'UPDATE money SET bank = {bank_sal + governmentSalaries[role_name]} WHERE user_id = {member.id}')
                conn.commit()
                count += 1
        emb.add_field(name=f'Выдана зарплата с ролью {role_name}', value=f'Сумма: {governmentSalaries[role_name]}F')
        curs.execute(f"SELECT bank FROM money WHERE user_id = {1078269797223112774} ")
        bot_sal = curs.fetchone()
        try:
            botbank = bot_sal[0]
        except:
            botbank = 0
        curs.execute(
            f'UPDATE money SET bank = {botbank - (count * governmentSalaries[role_name])} WHERE user_id = {1078269797223112774}')
        conn.commit()
        await ctx.send(embed=emb)
        return

    @app_commands.command(name='salary', description='Выдать зарплату ( только владельцы компаний )')
    @app_commands.checks.has_role("владелец компании")
    async def salary_company(self, interaction: discord.Interaction , role_name : str, amount : int):
        emb = discord.Embed(title=f'Выдача з/п работникам с ролью {role_name}', colour=discord.Color.blue())
        emb.add_field(name=f'Выдана зарплата с ролью {role_name}', value=f'Сумма: {amount}F')
        roles = await interaction.guild.fetch_roles()
        for r in roles:
            if r.name.split() == role_name.split():
                roleid = r.id

        try:
            checked_role = discord.utils.get(interaction.guild.roles, id=roleid)
        except:
            emb_Er = discord.Embed(title=f'Ошибка ❌', colour=discord.Color.red())
            emb_Er.add_field(name=f'Допущена ошибка в роли', value=f'Такой роли не существует')
            return await interaction.response.send_message(embed=emb_Er)
        count = 0
        curs.execute(f"SELECT bank FROM money WHERE user_id = {interaction.user.id}")
        check_bal = curs.fetchone()

        try:
            bank = check_bal[0]
        except:
            bank = 0

        for member in interaction.guild.members:
            if checked_role in member.roles:
                count += 1

        if bank < count * int(amount):
            emb_Er = discord.Embed(title=f'Ошибка ❌', colour=discord.Color.red())
            emb_Er.add_field(name=f'Недостаточно средств',
                             value=f'У вас недостаточно средств, чтобы выдать зарплату всем людям с этой ролью.')
            return await interaction.response.send_message(embed=emb_Er)
        else:
            for member in interaction.guild.members:
                if checked_role in member.roles:
                    curs.execute(f"SELECT bank FROM money WHERE user_id = {member.id}")
                    sal = curs.fetchone()
                    try:
                        bank_sal = sal[0]
                    except:
                        bank_sal = 0
                    curs.execute(f"UPDATE money SET bank = {bank_sal + int(amount)} WHERE user_id = {member.id}")
                    conn.commit()

            curs.execute(f"UPDATE money SET bank = {bank - (count * int(amount))} WHERE user_id = {interaction.user.id}")
            conn.commit()
            return await interaction.response.send_message(embed=emb)

    # -- СДЕЛАТЬ ПЕРЕВОД --
    @app_commands.command(name='pay', description='Перевести деньги.')
    @app_commands.choices(wallet_or_bank=[
        app_commands.Choice(name="Перевести в банк", value="bank"),
        app_commands.Choice(name="Передать наличными", value="wallet")])
    async def pay(self, interaction : discord.Interaction, wallet_or_bank: app_commands.Choice[str], member: discord.Member, amount: int):
        emb_succes = discord.Embed(title=f'Перевод клиенту ФесоБанка {member}', colour=0x00ffc8)
        curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {interaction.user.id}")
        bal_sender = curs.fetchone()
        curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
        bal_getter = curs.fetchone()
        try:
            wallet_sender = bal_sender[0]
            bank_sender = bal_sender[1]
            wallet_getter = bal_getter[0]
            bank_getter = bal_getter[1]
        except:
            wallet_sender = 0
            bank_sender = 0
            wallet_getter = 0
            bank_getter = 0
        if amount > bank_sender or amount > wallet_sender or amount < 0:
            emb = discord.Embed(title=f'Ошибка {interaction.user}', colour=discord.Color.red())
            emb.add_field(name='Недостаточно средств ❌',
                          value=f'Вы не можете сделать перевод, так как у вас недостаточно средств.')
            return await interaction.response.send_message(embed=emb, ephemeral=True)
        elif wallet_or_bank.value == 'bank':
            emb_succes.add_field(name='Перевод по счету 🏦', value=f'Сумма: {amount}F')
            curs.execute(f"UPDATE money SET bank = {bank_sender - amount} WHERE user_id = {interaction.user.id}")
            curs.execute(f"UPDATE money SET bank = {bank_getter + amount} WHERE user_id = {member.id}")
            conn.commit()

        elif wallet_or_bank.value  == "wallet":
            emb_succes.add_field(name='Перевод наличными 💶', value=f'Сумма: {amount}F')
            curs.execute(f"UPDATE money SET wallet = {wallet_sender - amount} WHERE user_id = {interaction.user.id}")
            curs.execute(f"UPDATE money SET wallet = {wallet_getter + amount} WHERE user_id = {member.id}")
            conn.commit()

        return await interaction.response.send_message(embed=emb_succes, ephemeral=True)

    # -- ПРОВЕРИТЬ БАЛАНС -

    @app_commands.command(name="balance", description="Проверить баланс")
    async def balance(self, interaction: discord.Interaction, member : discord.Member):

        emb = discord.Embed(title=f'Баланс {member}', colour=discord.Color.green())
        curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
        bal = curs.fetchone()
        try:
            wallet = bal[0]
            bank = bal[1]
        except:
            wallet = 0
            bank = 0

        emb.add_field(name='Наличными 💶', value=f'Наличными: {wallet}F')
        emb.add_field(name='Банк 🏦', value=f'В банке: {bank}F')
        await interaction.response.send_message(embed=emb, ephemeral=True)

    # -- СНЯТЬ ДЕНЬГИ С СЧЕТА --
    @app_commands.command(name='withdraw', description='Снять деньги с банка')
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        curs.execute(f'SELECT * FROM money WHERE user_id = {interaction.user.id}')

        data = curs.fetchone()

        wallet = data[1]
        bank = data[2]


        if bank < amount:
            emb = discord.Embed(title=f'Ошибка {interaction.user}', colour=discord.Color.red())
            emb.add_field(name='Недостаточно средств ❌', value=f'Вы не можете снять больше, чем у вас есть на счету.')
            print(type(bank), type(amount), bank, amount)

        else:
            emb = discord.Embed(title=f'Снятие денег с счета {interaction.user.id}', colour=discord.Color.purple())
            curs.execute(f"UPDATE money SET wallet = {wallet + amount} WHERE user_id = {interaction.user.id}")
            curs.execute(f'UPDATE money SET bank = {bank - amount} WHERE user_id = {interaction.user.id}')
            conn.commit()
            emb.add_field(name='Внутресчетовой перевод ✅', value=f'Вы сняли {amount}F со счета 💶.')

            conn.commit()

        return await interaction.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name='deposit', description='Внести деньги на счет')
    async def deposit(self, interaction: discord.Interaction, amount: int):
        curs.execute(f'SELECT * FROM money WHERE user_id = {interaction.user.id}')

        data = curs.fetchone()

        wallet = data[1]
        bank = data[2]

        if bank < amount:
            emb = discord.Embed(title=f'Ошибка {interaction.user}', colour=discord.Color.red())
            emb.add_field(name='Недостаточно средств ❌', value=f'Вы не можете снять больше, чем у вас есть на счету.')
            print(type(bank), type(amount), bank, amount)

        else:
            emb = discord.Embed(title=f'Снятие денег с счета {interaction.user.id}', colour=discord.Color.purple())
            curs.execute(f"UPDATE money SET wallet = {wallet - amount} WHERE user_id = {interaction.user.id}")
            curs.execute(f'UPDATE money SET bank = {bank + amount} WHERE user_id = {interaction.user.id}')
            conn.commit()
            emb.add_field(name='Внутресчетовой перевод ✅', value=f'Вы внесли {amount}F на счет 💶.')

            conn.commit()

        return await interaction.response.send_message(embed=emb, ephemeral=True)

    # -- ДОБАВИТЬ ДЕНЬГИ НА СЧЕТ ( АДМИН ОНЛИ ) --

    @app_commands.command(name='add-money', description='Добавить деньгми кому-либо. (admin-only)')
    @app_commands.checks.has_role("Управление деньгами")
    @app_commands.choices(wallet_or_bank=[
        app_commands.Choice(name="Перевести в банк", value="bank"),
        app_commands.Choice(name="Передать наличными", value="wallet")])
    async def add_money(self, interaction: discord.Interaction, wallet_or_bank: app_commands.Choice[str], member: discord.Member, money_count : int):

        emb = discord.Embed(title=f'Перевод денег {member}.', colour=discord.Color.dark_blue())
        curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
        bal = curs.fetchone()
        try:
            wallet = bal[0]
            bank = bal[1]

        except:
            wallet = 0
            bank = 0
        if wallet_or_bank.value == 'bank':
            emb.add_field(name=f'Добавлено в банк', value=money_count)
            curs.execute(f"UPDATE money SET bank = {bank + int(money_count)} WHERE user_id = {member.id}")
            conn.commit()


        elif wallet_or_bank.value == 'wallet':

            emb.add_field(name=f'Добавлено в кошелек', value=money_count)
            curs.execute(f"UPDATE money SET wallet = {wallet + int(money_count)} WHERE user_id = {member.id}")
            conn.commit()

        return await interaction.response.send_message(embed = emb, ephemeral=True)

    @app_commands.command(name='remove-money', description='Удалить деньгми кому-либо. (admin-only)')
    @app_commands.checks.has_role("Управление деньгами")
    @app_commands.choices(wallet_or_bank=[
        app_commands.Choice(name="Удалить из банка", value="bank"),
        app_commands.Choice(name="Удалить из кошелька", value="wallet")])
    async def add_money(self, interaction: discord.Interaction, wallet_or_bank: app_commands.Choice[str],
                        member: discord.Member, money_count: int):

        emb = discord.Embed(title=f'Удаление денежных средств {member}.', colour=discord.Color.dark_red())
        curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
        bal = curs.fetchone()
        try:
            wallet = bal[0]
            bank = bal[1]

        except:
            wallet = 0
            bank = 0
        if wallet_or_bank.value == 'bank':
            emb.add_field(name=f'Удалено из банка', value=money_count)
            curs.execute(f"UPDATE money SET bank = {bank - int(money_count)} WHERE user_id = {member.id}")
            conn.commit()


        elif wallet_or_bank.value == 'wallet':

            emb.add_field(name=f'Удалено из кошелька', value=money_count)
            curs.execute(f"UPDATE money SET wallet = {wallet - int(money_count)} WHERE user_id = {member.id}")
            conn.commit()

        return await interaction.response.send_message(embed=emb, ephemeral=True)

async def setup(client):
    await client.add_cog(Economics(client))