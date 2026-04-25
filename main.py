import asyncio
import os
from telethon import TelegramClient
from telethon.tl import functions

API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'
SESSION_FILE = '923558778274.session'
USERNAMES = os.getenv("USERNAMES", "bank,kitob,doira").split(",")

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Kirildi: {me.username or me.first_name}")
    
    while True:
        for name in USERNAMES:
            name = name.strip()
            if not name:
                continue
            try:
                await client(functions.account.UpdateUsernameRequest(name))
                print(f"✅ @{name} egallandi!")
            except Exception as e:
                if "USERNAME_NOT_OCCUPIED" in str(e):
                    print(f"✅ @{name} bo'sh, lekin egallanmadi")
                else:
                    print(f"❌ @{name}: {e}")
            await asyncio.sleep(2)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
