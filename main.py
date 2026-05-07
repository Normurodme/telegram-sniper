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
    print(f"📢 Kanal soni: {len(channels)}\n")
    
    username_index = 0
    
    while True:
        active = [ch for ch in channels if not ch['done']]
        if not active:
            print("✅ Barcha kanallar tugadi!")
            break
        
        username = USERNAMES[username_index % len(USERNAMES)]
        
        for channel in active:
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
                    break
                except Exception as e:
                    print(f"   ❌ Xato: {str(e)[:50]}")
            except FloodWaitError as e:
                print(f"   ⏳ {e.seconds} soniya kutish")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"   ❌ Xato: {str(e)[:50]}")
            
            await asyncio.sleep(8)
        
        username_index += 1
        
        done_count = sum(1 for ch in channels if ch['done'])
        print(f"\n📊 Egallangan: {done_count}/{len(channels)} | Qolgan: {len(USERNAMES)}\n")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
