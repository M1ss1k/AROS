#import psycopg2
import configparser
import discord
import sqlite3
config = configparser.ConfigParser()
config.read('config.ini')
postgres = config["postgresql"] # Данные от БД
#general = config["general"]

#conn = psycopg2.connect(host=postgres["host"], dbname=postgres["db"], user=postgres["user"], password=postgres["password"])
conn = sqlite3.connect('maind.db')
curs = conn.cursor()

    #--------------------------------------#
    #-----Снятие денег со счёта игрока-----#
    #--------------------------------------#

def RemoveBalance(wallet_or_bank: str, member: discord.Member, money_count: int):
            
            curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
            bal = curs.fetchone()
            try:
                wallet = bal[0]
                bank = bal[1]
            except:
                wallet = 0
                bank = 0

            if wallet_or_bank == 'bank':
                curs.execute(f"UPDATE money SET bank = {bank - int(money_count)} WHERE user_id = {member.id}")
                conn.commit()
                print(f"bank: has been removed on {money_count}. Current balance: {bank}")
            elif wallet_or_bank == 'wallet':
                curs.execute(f"UPDATE money SET wallet = {wallet - int(money_count)} WHERE user_id = {member.id}")
                conn.commit()
                print(f"wallet: has been removed on {money_count}. Current balance: {wallet}")

    #-----------------------------------------#
    #-----Добавление денег на счёт игрока-----#
    #-----------------------------------------#

def AddBalance(wallet_or_bank: str, member: discord.Member, money_count: int):
            curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
            bal = curs.fetchone()
            try:
                wallet = bal[0]
                bank = bal[1]
            except:
                wallet = 0
                bank = 0

            if wallet_or_bank == 'bank':
                curs.execute(f"UPDATE money SET bank = {bank + int(money_count)} WHERE user_id = {member.id}")
                conn.commit()
                print(f"bank: has been added on {money_count}. Current balance: {bank}")
            elif wallet_or_bank == 'wallet':
                curs.execute(f"UPDATE money SET wallet = {wallet + int(money_count)} WHERE user_id = {member.id}")
                conn.commit()
                print(f"wallet: has been added on {money_count}. Current balance: {wallet}")

    #----------------------------------#
    #-----Изменение баланса игрока-----#
    #----------------------------------#

def UpdateBalance(wallet_or_bank: str, member: discord.Member, money_count: int):
            curs.execute(f"SELECT wallet, bank FROM money WHERE user_id = {member.id}")
            bal = curs.fetchone()
            try:
                wallet = bal[0]
                bank = bal[1]
            except:
                wallet = 0
                bank = 0
            
            if wallet_or_bank == 'bank':
                curs.execute(f"UPDATE money SET bank = {money_count} WHERE user_id = {member.id}")
                conn.commit()
                print(f"bank: has been updated on {money_count}. Current balance: {bank}")
            elif wallet_or_bank == 'wallet':
                curs.execute(f"UPDATE money SET wallet = {money_count} WHERE user_id = {member.id}")
                conn.commit()
                print(f"wallet: has been updated on {money_count}. Current balance: {wallet}")