import requests as req
import json
import asyncio
import aiofiles
from decimal import Decimal as dec
from urllib.parse import quote


async def get_json():
    link = 'https://vexboost.ru/api/v2'
    token = 'Pdsi4nmQu8fFyPL1TOQObWwZzuOuz2gU9VRRUYv7fGu7WaBVknc99rxTLCny'
    params = {
        'action': 'services',
        'key': token
    }
    response = req.get(link, params=params).json()
    for item in response:
        if ':' in item['name']:
            item['name'] = item['name'].replace(':', '')
    with open('services.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)


async def get_networks():
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    networks = []
    for i in data:
        network = i['network']
        if network and network not in networks:
            networks.append(network)
    return networks


async def get_categories(network: str):
    async with aiofiles.open('services.json','r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    categories = []
    for i in data:
        category = i['category']
        if i['network'] and i['network'] in network and category not in categories and category:
            categories.append(category)
    return categories


async def get_names(condition: str):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    names = []
    for i in data:
        name = i['name']
        if condition in i['category'] and name and name not in names:
            names.append(name)
    return names


async def get_description(condition: str):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    for i in data:
        if condition in i['name']:
            descr = i['description'][:800] if i['description'] else 'зачем оно тут?'
            id = i['service']
            min = i['min']
            max = i['max']
            refill = 'Йеп' if i['refill'] else 'ноуп'
            cancelling = 'Йеп' if i['cancel'] else 'ноуп'
            price = dec(str(i['rate'])) / 5
            price = price.quantize(dec('1.0000'))
            name = i['name']
            description = (f'📝<b>Название</b>: {name}\n📒<b>Описание</b>: {descr}\n🔮<b>ID Услуги</b>: {id}\n📊<b>Мин|Макс за 1 заказ</b>: {min}|{max}\n'
                           f'♻<b>Доступ к рефилу</b>: {refill}\n🛑<b>Доступ к отмене</b>: {cancelling}\n💵<b>Прайс</b>: <u><em>{price}</em></u>')
            return description


async def get_fullname(short_name: str, category: str='name'):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
        for i in data:
            try:
                if short_name in i[category]:
                    return i[category]
            except:
                pass


async def get_service_id(name: str):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
        for i in data:
            try:
                if name == i['name']:
                    return i['service']
            except:
                pass


async def get_service_name(id: int):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
        for i in data:
            try:
                if id == i['service']:
                    return i['name']
            except:
                pass


async def get_info_id(id: str):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    for i in data:
        if id == str(i['service']):
            return (dec(str(i['rate'])) / 5).quantize(dec('1.0000')), i['name'], i['min'], i['max']


async def make_order(service_id, link, quantity):
    host = 'https://vexboost.ru/api/v2'
    token = 'Pdsi4nmQu8fFyPL1TOQObWwZzuOuz2gU9VRRUYv7fGu7WaBVknc99rxTLCny'
    params = {
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity,
        'key': token
    }
    response = req.get(host, params=params)
    return response.json()


async def id_to_name(id):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    for i in data:
        if i['service'] == id:
            return i['name']


async def name_to_id(name):
    async with aiofiles.open('services.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    for i in data:
        if i['name'] == name:
            return i['service']


async def get_services(mode, condition: str|int=''):
    if mode == 0:
        return await get_networks()
    elif mode == 1:
        return await get_categories(condition)
    elif mode == 2:
        return await get_names(condition)
    elif mode == 3:
        return await get_description(condition)
    elif mode == 4:
        return await get_service_id(condition)
    elif mode == 5:
        return await id_to_name(condition)
    elif mode == 6:
        return await name_to_id(condition)


async def get_order_info(order_id):
    link = 'https://vexboost.ru/api/v2'
    token = 'Pdsi4nmQu8fFyPL1TOQObWwZzuOuz2gU9VRRUYv7fGu7WaBVknc99rxTLCny'
    params = {
        'action': 'status',
        'order': order_id,
        'key': token
    }
    response = req.get(link, params=params).json()
    return response


async def get_orders_info(orders):
    link = 'https://vexboost.ru/api/v2'
    token = 'Pdsi4nmQu8fFyPL1TOQObWwZzuOuz2gU9VRRUYv7fGu7WaBVknc99rxTLCny'
    orders_id = ''
    orders_id = ','.join(str(order[2]) for order in orders)
    url = f'{link}?action=status&orders={orders_id}&key={token}'
    response = req.get(url=url)
    return response.json()


async def updater():
    while True:
        await get_json()
        await asyncio.sleep(3600)
