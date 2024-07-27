from asyncpg_lite import DatabaseManager
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import String, Integer, Text, TIMESTAMP
import asyncio

load_dotenv()
pg_manager = DatabaseManager(db_url=os.getenv("PG_DOCKER"), deletion_password=os.getenv("PG_PASS"))


async def create_table_users(table_name="user_message"):
    async with pg_manager:
        columns = [{"name": "id", "type": Integer, "options": {"primary_key": True, "autoincrement": True}},
                    {"name": "username", "type": String, "options": {"nullable": False}},
                    {"name": "messages", "type": Text},
                    {"name": "date", "type": TIMESTAMP, 'options': {"server_default": datetime.datetime.now()}}]
        await pg_manager.create_table(table_name=table_name, columns=columns)

    
async def get_user_messages(username: str, table_name="user_message"):
    async with pg_manager:
        user_info = await pg_manager.select_data(table_name=table_name, where_dict={"username": username}, columns=["messages"])
        if user_info:
            return user_info
        else:
            return None
        

async def insert_user(user_data: dict, table_name="user_message"):
    async with pg_manager:
        await pg_manager.insert_data_with_update(table_name=table_name, records_data=user_data, conflict_column="id")