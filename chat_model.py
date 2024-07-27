import shutil
import requests
from aiogram import types
import json
import uuid
import random
import database as db
from langchain_community.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage
import datetime
import os
from dotenv import load_dotenv


load_dotenv()


async def get_message_by_gigachain(message: types.Message):
    chat = GigaChat(credentials=os.getenv("CREDENTIALS"), verify_ssl_certs=False)

    pipeline = [SystemMessage(content="Ты помощник для ребят на буткемпе и на хакатоне по имени Морти, отвечающий на вопросы. Ответ должен быть не более 30 слов. Ты даешь советы ребятам по программированию ботов с использованием GigaChat API на python. Для ответа используй данные ниже: Буткемп занимается продвижением ребят в сфере ит и искусственного интеллекта. Ты - помогаешь ребятам с их ИТ-продуктами. Буткемп предлагает ребятам разобраться как работает ит-индустрия, получить практический опыт в программировании за короткое время, пополнить портфолио новыми проектами, подготовиться к международным соревнованиям, получить сертификаты и попробовать выиграть призы. Ты также должен уметь рисовать блок-схемы для приложений, описанных ребятами. Твоя задача помогать ребятам изучать новые темы, формировать идеи, писать код, защищать проект, планировать работу команды и распределять задачи. Умеешь генерировать изоображения только по команде /image. Если пользователь попросит сгенерировать изоображение попроси его ввести эту команду")]

    username = message.from_user.username
    user_data = {"username": username, "messages": message.text, "date": datetime.datetime.now()}

    await db.insert_user(user_data)

    user_messages = await db.get_user_messages(username)

    for cur in user_messages[-3:]:
        pipeline.append(HumanMessage(content=cur["messages"]))

    return chat(pipeline).content



def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload='scope=GIGACHAT_API_PERS'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid.UUID(int=random.getrandbits(128), version=4)),
    'Authorization': 'Basic ' + os.getenv("CREDENTIALS")
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    response_json = response.json()

    return response_json["access_token"]


async def get_payload_headers(message: types.Message):
    access_token = get_access_token()

    payload = json.dumps({
    "model": "GigaChat", 
    "stream": False, 
    "update_interval": 0, 
    "function_call": "auto",
    "messages": [
            {
                "role": "system", 
                "content": "нарисуй" + message.text
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': "Bearer " + access_token
    }
    
    return payload, headers


async def save_genrated_image(img_uuid):
    access_token = get_access_token()

    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{img_uuid}/content"
    headers = {
        'Accept': 'application/jpg',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, stream=True)

    with open('image/img.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


async def get_image_by_gigachat(message: types.Message):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload, headers = await get_payload_headers(message)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return_json = response.json()

    content = return_json["choices"][0]["message"]["content"]

    img_uuid = content.split('src="')[1].split('" fuse=')[0]

    await save_genrated_image(img_uuid)
    res_title = return_json["choices"][0]["message"]["data_for_context"][2]["content"]
    return res_title
