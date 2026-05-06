import asyncio
import os
from telethon import TelegramClient
from telethon.tl import functions
from telethon.errors import FloodWaitError

API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'
SESSION_FILE = '998772656790.session'

CHANNELS = [
    'https://t.me/nutoniy',
    'https://t.me/beckeds',
    'https://t.me/solomastere',
]

USERNAMES = os.getenv("USERNAMES", "bank,kitob,doira").split(",")

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    
    channels = []
    for ch_link in CHANNELS:
        try:
            ch = await client.get_entity(ch_link)
            channels.append(ch)
            print(f"✅ Kanal: {ch.title}")
        except Exception as e:
            print(f"❌ Kanal topilmadi {ch_link}: {e}")
    
    if not channels:
        print("❌ Hech qanday kanal topilmadi!")
        return
    
    print(f"\n🚀 Usernameler: {USERNAMES}")
    print(f"📢 Kanal soni: {len(channels)}\n")
    
    current_index = 0  # Username indeksi
    
    while True:
        # 🔥 O'ZGARISH: Har safar 1 ta username, 1 ta kanal
        name = USERNAMES[current_index].strip()
        channel = channels[0]  # Faqat 1-kanal
        
        try:
            await client(functions.channels.UpdateUsernameRequest(
                channel=channel,
                username=name
            ))
            print(f"🎉 @{name} egallandi! {channel.title}")
            
        except FloodWaitError as e:
            print(f"⏳ {e.seconds} soniya kutish kerak")
            await asyncio.sleep(e.seconds)
            
        except Exception as e:
            err = str(e)
            if "USERNAME_NOT_OCCUPIED" in err:
                print(f"⚡ @{name} bo'sh!")
                await asyncio.sleep(0.2)
                try:
                    await client(functions.channels.UpdateUsernameRequest(
                        channel=channel,
                        username=name
                    ))
                    print(f"🎉 @{name} egallandi!")
                except:
                    pass
            elif "USERNAME_OCCUPIED" in err or "already taken" in err:
                print(f"📌 @{name} band - keyingisiga o'tish")
                current_index = (current_index + 1) % len(USERNAMES)
                await asyncio.sleep(3)
                continue
            else:
                print(f"❌ @{name} -> {err[:80]}")
        
        # Keyingi usernamega o'tish
        current_index = (current_index + 1) % len(USERNAMES)
        
        # 🔥 MUHIM: 5-10 soniya kutish FLOOD oldini oladi
        await asyncio.sleep(8)

if __name__ == "__main__":
    asyncio.run(main())
