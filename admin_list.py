from database import get_admins
from asyncio import sleep, run as asrun

import json
from asyncio import sleep

async def update_admin_list():
    global admin_list
    while True:
        admins = await get_admins()

        admin_list = [admin.tg_id for admin in admins]
        
        with open('admin_list.json', 'w') as f:
            json.dump(admin_list, f)

        await sleep(30)

if __name__ == "__main__":
    asrun(update_admin_list())
