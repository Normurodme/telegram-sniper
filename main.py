import asyncio
import os
import sys
from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.account import UpdateUsernameRequest

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE_NUMBER", "")
USERNAMES = os.getenv("USERNAMES", "").split(",")

async def main():
    if not API_ID or not API_HASH or not PHONE:
        print("Error: API_ID, API_HASH, PHONE_NUMBER required")
        return
    
    # Session faylni /tmp da saqlash (Railway'da yozish mumkin)
    session_file = f"/tmp/telegram_{PHONE}"
    client = TelegramClient(session_file, API_ID, API_HASH)
    
    await client.start(phone=PHONE)
    
    me = await client.get_me()
    print(f"Logged in as: {me.username or me.first_name}")
    
    while True:
        for username in USERNAMES:
            username = username.strip()
            if not username:
                continue
            
            try:
                # Check if username is available
                result = await client(ResolveUsernameRequest(username))
                if not result:
                    print(f"✅ Username @{username} is FREE!")
                    try:
                        await client(UpdateUsernameRequest(username))
                        print(f"🏆 SUCCESS! Claimed @{username}")
                    except errors.RPCError as e:
                        print(f"Claim failed: {e}")
                else:
                    print(f"❌ @{username} is taken")
            except errors.UsernameNotOccupiedError:
                print(f"✅ Username @{username} is FREE! Trying to claim...")
                try:
                    await client(UpdateUsernameRequest(username))
                    print(f"🏆 SUCCESS! Claimed @{username}")
                except errors.RPCError as e:
                    print(f"Claim failed: {e}")
            except Exception as e:
                print(f"Error checking @{username}: {e}")
            
            await asyncio.sleep(2)
        
        print("Waiting 10 seconds before next check...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
