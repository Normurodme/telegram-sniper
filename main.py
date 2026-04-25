import asyncio
import os
import sys
from telethon import TelegramClient, errors

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE_NUMBER", "")
USERNAMES = os.getenv("USERNAMES", "").split(",")

async def main():
    if not API_ID or not API_HASH or not PHONE:
        print("Error: API_ID, API_HASH, PHONE_NUMBER required")
        return
    
    client = TelegramClient(f"sessions/{PHONE}", API_ID, API_HASH)
    await client.start()
    
    print(f"Logged in! Checking usernames: {USERNAMES}")
    
    while True:
        for username in USERNAMES:
            username = username.strip()
            if not username:
                continue
            
            try:
                # Check if username is available
                result = await client(functions.contacts.ResolveUsernameRequest(username))
                if not result:
                    print(f"✅ Username @{username} is FREE!")
                    # Claim the username
                    try:
                        await client(functions.account.UpdateUsernameRequest(username))
                        print(f"🏆 SUCCESS! Claimed @{username}")
                    except errors.RPCError as e:
                        print(f"Claim failed: {e}")
                else:
                    print(f"❌ @{username} is taken")
            except errors.UsernameNotOccupiedError:
                print(f"✅ Username @{username} is FREE! Trying to claim...")
                try:
                    await client(functions.account.UpdateUsernameRequest(username))
                    print(f"🏆 SUCCESS! Claimed @{username}")
                except errors.RPCError as e:
                    print(f"Claim failed: {e}")
            except Exception as e:
                print(f"Error checking @{username}: {e}")
            
            await asyncio.sleep(2)
        
        print(f"Waiting 10 seconds...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
