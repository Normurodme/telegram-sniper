import asyncio
import os
from telethon import TelegramClient
from telethon.tl import functions
from telethon.errors import FloodWaitError

API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'
SESSION_FILE = '923551670822.session'

# ⬇️ KANALLAR ⬇️
CHANNELS = [
    'https://t.me/nutoniy',
    'https://t.me/beckeds',
    'https://t.me/solomastere',
]

USERNAMES = os.getenv("USERNAMES", "themart,solikhov,bookmaker,masters,prices,verti").split(",")

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    
    # Kanallarni yuklash
    channels = []
    for ch_link in CHANNELS:
        try:
            ch = await client.get_entity(ch_link)
            channels.append({
                'entity': ch,
                'title': ch.title,
                'active': True,
                'last_check': 0
            })
            print(f"✅ Kanal: {ch.title}")
        except Exception as e:
            print(f"❌ Kanal topilmadi {ch_link}: {e}")
    
    if not channels:
        print("❌ Hech qanday kanal topilmadi!")
        return
    
    print(f"\n🚀 Kuzatilayotgan usernameler: {USERNAMES}")
    print(f"📢 Kanal soni: {len(channels)}")
    print(f"🎯 Har bir kanalga navbat bilan 1 tadan username\n")
    
    channel_idx = 0
    username_idx = 0
    
    while True:
        # Faqat faol kanallar
        active = [ch for ch in channels if ch['active']]
        if not active:
            print("✅ Barcha kanallar username egalladi!")
            break
        
        # Joriy kanal va username
        channel = channels[channel_idx % len(channels)]
        if not channel['active']:
            channel_idx += 1
            continue
            
        name = USERNAMES[username_idx % len(USERNAMES)].strip()
        
        print(f"📡 {channel['title']} -> @{name}")
        
        try:
            await client(functions.channels.UpdateUsernameRequest(
                channel=channel['entity'],
                username=name
            ))
            print(f"🎉 @{name} {channel['title']} ga egallandi!")
            channel['active'] = False  # Kanal endi tekshirilmaydi
            if name in USERNAMES:
                USERNAMES.remove(name)
            
        except FloodWaitError as e:
            print(f"⏳ {e.seconds} soniya flood wait - bot to'xtadi")
            await asyncio.sleep(e.seconds)
            
        except Exception as e:
            err = str(e)
            if "USERNAME_NOT_OCCUPIED" in err:
                print(f"⚡ @{name} bo'sh! Egallanmoqda...")
                await asyncio.sleep(1)
                try:
                    await client(functions.channels.UpdateUsernameRequest(
                        channel=channel['entity'],
                        username=name
                    ))
                    print(f"🎉 @{name} egallandi!")
                    channel['active'] = False
                    if name in USERNAMES:
                        USERNAMES.remove(name)
                except:
                    print(f"❌ @{name} olinmadi")
                    
            elif "USERNAME_OCCUPIED" in err or "already taken" in err:
                print(f"📌 @{name} band")
                
            else:
                print(f"❌ {err[:50]}")
        
        # Round-robin: keyingi kanal va username
        channel_idx += 1
        
        # Agar barcha kanallar bo'ylab o'tgan bo'lsa, keyingi username
        if channel_idx % len(channels) == 0:
            username_idx += 1
        
        # 🔥 15-20 soniya kutish FLOOD oldini oladi
        await asyncio.sleep(20)
        
        # Statistikani ko'rsatish
        active_count = sum(1 for ch in channels if ch['active'])
        print(f"📊 Faol kanallar: {active_count}/{len(channels)} | Qolgan: {len(USERNAMES)}")

if __name__ == "__main__":
    asyncio.run(main())
