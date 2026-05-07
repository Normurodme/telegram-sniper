import asyncio
import os
import time
from telethon import TelegramClient
from telethon.tl import functions
from telethon.errors import FloodWaitError

API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'
SESSION_FILE = '923551670822.session'

CHANNELS = [
    'https://t.me/mandepo',
    'https://t.me/nerstes',
    'https://t.me/nermed',
]

USERNAMES = os.getenv("USERNAMES", "themart,solikhov,bookmaker,masters,prices,verti").split(",")

# 🔥 RATE LIMIT: 1 daqiqada 3 ta tekshiruv
MAX_CHECKS_PER_MINUTE = 3
CHECK_INTERVAL = 20  # 60 / 3 = 20 soniya

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    
    channels = []
    for ch_link in CHANNELS:
        try:
            ch = await client.get_entity(ch_link)
            channels.append({
                'entity': ch,
                'title': ch.title,
                'done': False
            })
            print(f"✅ Kanal: {ch.title}")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    if not channels:
        print("❌ Hech qanday kanal topilmadi!")
        return
    
    print(f"\n🚀 Usernameler: {USERNAMES}")
    print(f"📢 Kanal soni: {len(channels)}")
    print(f"⏱️  Cheklov: {MAX_CHECKS_PER_MINUTE} ta tekshiruv/daqiqa")
    print(f"⏱️  Oraliq: {CHECK_INTERVAL} soniya\n")
    
    index = 0
    
    while True:
        active = [ch for ch in channels if not ch['done']]
        if not active:
            print("✅ Barcha kanallar tugadi!")
            break
        
        # Navbatdagi username va kanal
        channel_idx = (index // len(USERNAMES)) % len(active)
        username_idx = index % len(USERNAMES)
        
        channel = active[channel_idx]
        username = USERNAMES[username_idx].strip()
        
        print(f"📡 {channel['title']} -> @{username}")
        
        try:
            await client.get_entity(f"https://t.me/{username}")
            print(f"   📌 @{username} - BAND")
        except ValueError:
            print(f"   ⚡ @{username} - BO'SH! Egallanmoqda...")
            try:
                await client(functions.channels.UpdateUsernameRequest(
                    channel=channel['entity'],
                    username=username
                ))
                print(f"   🎉 @{username} egallandi!")
                channel['done'] = True
                if username in USERNAMES:
                    USERNAMES.remove(username)
                index = 0
                continue
            except Exception as e:
                print(f"   ❌ Xato: {str(e)[:50]}")
        except FloodWaitError as e:
            print(f"   ⏳ Flood wait: {e.seconds} soniya")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"   ❌ Xato: {str(e)[:50]}")
        
        index += 1
        
        # 🔥 1 daqiqada 3 ta tekshiruv = 20 soniya kutish
        await asyncio.sleep(CHECK_INTERVAL)
        
        done_count = sum(1 for ch in channels if ch['done'])
        print(f"\n📊 Egallangan: {done_count}/{len(channels)} | Qolgan: {len(USERNAMES)}")
        print(f"⏳ Keyingi tekshiruv {CHECK_INTERVAL} soniyadan keyin\n")

if __name__ == "__main__":
    asyncio.run(main())
