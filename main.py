import asyncio
import os
import platform

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import ConfigParser

from telethon import TelegramClient
from telethon.sessions import StringSession

from scanner.scanner import Scanner, UsernameState

script_file_path = os.path.abspath(__file__)
script_current_dir = os.path.dirname(script_file_path)

def parse_arguments():
    '''Configure command prompt argument manager'''

    parser = ArgumentParser(
        prog="scanner.py",
        usage="%(prog)s [options] [filename]",
        description="Telegram username scanner",
        epilog=(
            "Examples:\n\n"
            "\tpython scanner.py wordlist.txt\n"
            "\tpython scanner.py -c settings.ini wordlist.txt\n"
            "\tpython scanner.py -o result.txt wordlist.txt\n"
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-c', '--config',
        default=None,
        type=str,
        help='configuration file'
    )

    parser.add_argument(
        '-o', '--output',
        default=None,
        type=str,
        help='output file'
    )

    parser.add_argument(
        'filename',
        type=str,
        help='wordlist file'
    )

    return parser.parse_args()

def parse_configuration(path: str):
    '''Create parser and read configuration file'''

    parser = ConfigParser()
    parser.read(path)
    return parser['general']

def create_client(cfg) -> TelegramClient:
    '''Create Telethon client by configuration values'''

    return TelegramClient(
        session=StringSession(cfg['string_session']),
        api_id=cfg['api_id'],
        api_hash=cfg['api_hash'],
        flood_sleep_threshold=0,
        receive_updates=False,
    )

def load_wordlist(file: str) -> list:
    '''Load wordlist file'''

    with open(file, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def log(text: str, level: str = "info"):
    '''Print a log'''
    print(f"[{level.upper()}] {text}")

async def main():
    '''The main executor'''

    if platform.system().lower() == "windows":
        clear_cmd = "cls"

    else:
        clear_cmd = "clear"

    args = parse_arguments()
    filename = args.filename
    config_file = args.config
    output_file = args.output

    wordlist = load_wordlist(file=filename)
    if not wordlist:
        log(text="Wordlist is empty.", level="ERR")
        return

    if not config_file:
        config_file = os.path.join(script_current_dir, 'settings.ini')

    if not output_file:
        output_file = os.path.join(script_current_dir, "result.txt")

    config = parse_configuration(path=config_file)
    client = create_client(cfg=config)

    username_count = len(wordlist)
    log(text=f"{username_count} username's loaded successfully!")
    log(text="Starting...")

    # A few delay to see console logs
    await asyncio.sleep(2.0)

    try:
        scanner = Scanner(client=client)
        inital = await scanner.initate()

        if not inital:
            log(text="Client session is wrong or expired!", level="ERR")
            return

        occupied = 0
        invalid = 0
        on_fragment = 0
        unknown = 0

        counter = 0
        async for uname, state in scanner.scan(wordlist):
            if state in (UsernameState.OCCUPIED, UsernameState.NOT_OCCUPIED):
                occupied += 1

            elif state == UsernameState.INVALID:
                invalid += 1

            elif state == UsernameState.ON_FRAGMENT:
                on_fragment += 1

            else:
                unknown += 1

            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f'{uname}:{state.name}\n')

            counter += 1

            os.system(clear_cmd)
            print(
                f"[STATS]\n\n"
                f"• Occupied [or not]: {occupied:,}\n"
                f"• Invalid [banned or NFT]: {invalid:,}\n"
                f"• On Fragment [auction]: {on_fragment:,}\n\n"
                f"• Unknown [error]: {unknown:,}\n\n"
                f"• Progress: {counter:,} scanned from {username_count:,} "
                f"({(counter*100)/username_count:.2f}%)\n\n"
                f"\t@{uname} => {state.name!r}"
            )

            await asyncio.sleep(0.001) # To avoid ToS violation

    except Exception as e:
        log(text=e, level="ERR")

    finally:
        await scanner.stop()
        log("Scan done.")

    input()

if __name__ == "__main__":
    asyncio.run(main())