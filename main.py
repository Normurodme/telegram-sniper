import asyncio
import os
from telethon import TelegramClient
from telethon.tl import functions

API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'
SESSION_FILE = '923558778274.session'

# ⬇️ KANALLAR ⬇️
CHANNELS = [
    'https://t.me/nutoniy',
    'https://t.me/beckeds',
    'https://t.me/solomastere',
]

USERNAMES = os.getenv("USERNAMES", "bank,kitob,doira").split(",")

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    
    # Kanallarni tekshirish
    channels = []
    for ch_link in CHANNELS:
        try:
            ch = await client.get_entity(ch_link)
            channels.append(ch)
            print(f"✅ Kanal: {ch.title} (@{ch.username})")
        except Exception as e:
            print(f"❌ Kanal topilmadi {ch_link}: {e}")
    
    if not channels:
        print("❌ Hech qanday kanal topilmadi!")
        return
    
    print(f"\n🚀 Kuzatilayotgan usernameler: {USERNAMES}")
    print(f"📢 Kanal soni: {len(channels)}\n")
    
    while True:
        for name in USERNAMES:
            name = name.strip()
            if not name:
                continue
            
            for channel in channels:
                try:
                    await client(functions.channels.UpdateUsernameRequest(
                        channel=channel,
                        username=name
                    ))
                    print(f"🎉 {channel.title} ga @{name} egallandi!")
                except Exception as e:
                    err = str(e)
                    if "USERNAME_NOT_OCCUPIED" in err:
                        print(f"⚡ @{name} bo'sh! Qayta urinish...")
                        await asyncio.sleep(0.2)
                        try:
                            await client(functions.channels.UpdateUsernameRequest(
                                channel=channel,
                                username=name
                            ))
                            print(f"🎉 {channel.title} ga @{name} egallandi!")
                        except:
                            pass
                    elif "USERNAME_INVALID" in err:
                        print(f"❌ @{name} noto'g'ri format")
                    else:
                        print(f"❌ @{name} -> {err[:50]}")
                await asyncio.sleep(2)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
