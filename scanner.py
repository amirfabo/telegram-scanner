import os
import asyncio
import platform
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

from telethon.tl.functions.account import CheckUsernameRequest

from telethon.errors import FloodWaitError
from telethon.errors import BadRequestError
from telethon.errors import UsernameInvalidError

from configparser import ConfigParser

script_file_path = os.path.abspath(__file__)
script_current_dir = os.path.dirname(script_file_path)

parser = ConfigParser()
parser.read(os.path.join(script_current_dir, "settings.ini"))

GENERAL_SECTION = parser["GENERAL"]

# Executor function to scanning word list
async def executor(client: TelegramClient, word_list: list[str], file_path: str) -> list[str]:

    # To ensure the account limitation :D
    print(f"[INFO] Running loop to get flood limit...")
    for _ in range(50):
        try:
            await client(CheckUsernameRequest(username="durov"))

        except FloodWaitError as err:
            print(f"In {_}th attempt we got flood!")
            if err.seconds >= 10:
                break

        except:
            continue

    results = []
    occupied_count = 0
    invalid_count = 0
    fragment_count = 0

    for num, username in enumerate(word_list, start=1):
        try:
            await client(CheckUsernameRequest(username=username))

        except FloodWaitError:
            tag = "OCCUPIED"
            occupied_count += 1

        except UsernameInvalidError:
            tag = "INVALID"
            invalid_count += 1

        except BadRequestError:
            tag = "ON_FRAGMENT"
            fragment_count += 1

        except Exception as err:
            tag = err.ID
            invalid_count += 1

        result = f"{username}:{tag}"
        results.append(result)

        with open(file_path, "w") as file:
            file.write("\n".join(results))

        os.system(clear_cmd)

        print(
            f"[STATS]\n\n"
            f"• Occupied (Or NOT): {occupied_count:,}\n"
            f"• Invalid (Banned, NFT): {invalid_count:,}\n"
            f"• On Fragment: {fragment_count:,}\n\n"
            f"• Progress: {num:,} scanned from {word_count:,} ({(num*100)/word_count:.2f}%)\n\n"
            f"\t@{username} => {tag!r}"
        )

    return results

async def main():
    global word_count

    wordlist_file_path = input("[ASK] Enter the word list file path: ")
    with open(wordlist_file_path) as file:
        wordlist = file.read().splitlines()

    if not wordlist:
        print("\n[INFO] Wordlist file is empty :(.")
        return

    word_count = len(wordlist)
    print(f"\n[INFO] {word_count:,} username's successfully loaded.\n")

    client = TelegramClient(
        session=StringSession(GENERAL_SECTION['string_session']),
        api_id=GENERAL_SECTION['api_id'],
        api_hash=GENERAL_SECTION['api_hash'],
        receive_updates=False,
        flood_sleep_threshold=0)

    await client.connect()

    if not client.is_connected:
        print(f"[ERROR] Client string session is wrong or expired.")
        return

    try:
        await executor(
            client=client,
            word_list=wordlist,
            file_path=GENERAL_SECTION['result_file'],
        )

    finally:
        await client.disconnect()

if __name__ == "__main__":
    if platform.system().lower() == "windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        clear_cmd = "cls"

    else:
        clear_cmd = "clear"

    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)