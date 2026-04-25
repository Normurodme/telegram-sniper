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
    
    print(f"✅ Kirildi")
    
    while True:
        for name in USERNAMES:
            name = name.strip()
            if not name:
                continue
            try:
                # To'g'ridan-to'g'ri egallashga urinish
                await client(functions.account.UpdateUsernameRequest(name))
                print(f"🎉 @{name} EGALLANDI!")
            except Exception as e:
                err = str(e)
                if "USERNAME_NOT_OCCUPIED" in err:
                    # Bo'sh, lekin egallay olmadi – darhol qayta urinish
                    print(f"⚡ @{name} bo'sh! Qayta urinish...")
                    await asyncio.sleep(0.1)
                    try:
                        await client(functions.account.UpdateUsernameRequest(name))
                        print(f"🎉 @{name} EGALLANDI!")
                    except:
                        pass
                elif "USERNAME_INVALID" in err:
                    print(f"❌ @{name} noto'g'ri format")
                else:
                    print(f"❌ @{name}: Band")
            await asyncio.sleep(0.2)  # 0.2 sekund – juda tez!
        await asyncio.sleep(0.5)  # Har 0.5 sekundda to'liq sikl

if __name__ == "__main__":
    asyncio.run(main())
