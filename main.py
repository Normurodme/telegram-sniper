import asyncio
import os
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
                'active': True  # Faol kanal
            })
            print(f"✅ Kanal: {ch.title}")
        except Exception as e:
            print(f"❌ Kanal topilmadi {ch_link}: {e}")
    
    if not channels:
        print("❌ Hech qanday kanal topilmadi!")
        return
    
    print(f"\n🚀 Usernameler: {USERNAMES}")
    print(f"📢 Kanal soni: {len(channels)}")
    print(f"🎯 Qoida: Bo'sh username topilsa DARHOL egallanadi!\n")
    
    channel_index = 0
    username_index = 0
    
    while True:
        # Faqat faol kanallarni olish
        active_channels = [ch for ch in channels if ch['active']]
        
        if not active_channels:
            print("✅ Barcha kanallar username egalladi! Bot to'xtatildi.")
            break
        
        # Joriy kanal (faqat faol)
        channel = active_channels[channel_index % len(active_channels)]
        name = USERNAMES[username_index].strip()
        
        print(f"📡 {channel['title']} -> @{name} tekshirilmoqda...")
        
        try:
            await client(functions.channels.UpdateUsernameRequest(
                channel=channel['entity'],
                username=name
            ))
            print(f"🎉 {channel['title']} ga @{name} egallandi!")
            
            # 🔥 MUHIM: Kanalni faolsizlantirish (endi tekshirilmaydi)
            channel['active'] = False
            print(f"🚫 {channel['title']} endi tekshirilmaydi (username egallangan)")
            
            # Bu usernameni ro'yxatdan o'chirish
            if name in USERNAMES:
                USERNAMES.remove(name)
                print(f"📝 {name} ro'yxatdan olib tashlandi")
            
            # Keyingi username va kanalga o'tish
            username_index = (username_index + 1) % len(USERNAMES) if USERNAMES else 0
            continue
            
        except FloodWaitError as e:
            print(f"⏳ {e.seconds} soniya flood wait - kutish kerak")
            await asyncio.sleep(e.seconds)
            
        except Exception as e:
            err = str(e)
            if "USERNAME_NOT_OCCUPIED" in err:
                print(f"⚡ @{name} bo'sh! DARHOL egallanmoqda...")
                await asyncio.sleep(0.5)
                try:
                    await client(functions.channels.UpdateUsernameRequest(
                        channel=channel['entity'],
                        username=name
                    ))
                    print(f"🎉 {channel['title']} ga @{name} egallandi!")
                    
                    # Egallandi - kanalni faolsizlantirish
                    channel['active'] = False
                    print(f"🚫 {channel['title']} endi tekshirilmaydi")
                    
                    if name in USERNAMES:
                        USERNAMES.remove(name)
                    
                except Exception as e2:
                    print(f"❌ @{name} olinmadi: {str(e2)[:50]}")
                    
            elif "USERNAME_OCCUPIED" in err or "already taken" in err:
                print(f"📌 @{name} band - keyingi username")
                username_index = (username_index + 1) % len(USERNAMES)
                continue
                
            elif "USERNAME_INVALID" in err:
                print(f"❌ @{name} noto'g'ri format")
                username_index = (username_index + 1) % len(USERNAMES)
                continue
                
            else:
                print(f"❌ @{name} -> {err[:60]}")
        
        # Keyingi kanal va username
        channel_index += 1
        if channel_index >= len(active_channels):
            channel_index = 0
            username_index = (username_index + 1) % len(USERNAMES)
        
        # Statistikani ko'rsatish
        active_count = sum(1 for ch in channels if ch['active'])
        print(f"📊 Faol kanallar: {active_count}/{len(channels)} | Qolgan usernameler: {len(USERNAMES)}")
        
        # 15 soniya kutish (flood oldini olish)
        await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
