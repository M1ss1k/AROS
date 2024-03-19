import configparser
import discord
from discord.ext import commands
# import psycopg2
import random, sqlite3

config = configparser.ConfigParser()
config.read('config.ini')
postgres = config["postgresql"]

class Event(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        #conn = psycopg2.connect(host=postgres["host"], dbname=postgres["db"], user=postgres["user"], password=postgres["password"])
        conn = sqlite3.connect('main.db')
        curs = conn.cursor()

        curs.execute("""CREATE TABLE IF NOT EXISTS money (
                        user_id BIGINT, 
                        wallet BIGINT, 
                        bank BIGINT
                    );
                    """)
        conn.commit()
        print('Bot\'s online')



async def setup(client):
    await client.add_cog(Event(client))