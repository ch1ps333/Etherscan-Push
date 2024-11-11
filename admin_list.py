from database import get_admins
from asyncio import sleep
admin_list = []

async def update_admin_list():
    global admin_list
    while True:
        admins = await get_admins()

        admin_list = [admin.tg_id for admin in admins]
        await sleep(30)
