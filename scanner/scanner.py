from enum import Enum
from typing import AsyncGenerator

from telethon import errors
from telethon.tl import functions

class UsernameState(Enum):
    OCCUPIED = 1
    NOT_OCCUPIED = 2
    INVALID = 3
    ON_FRAGMENT = 4
    UNKNOWN = 5

class Scanner:
    def __init__(self, client) -> None:
        self._client = client

    async def initate(self) -> bool:
        '''Initiate Telethon client and return authorization status'''

        if not self._client.is_connected():
            await self._client.connect()

        return await self._client.is_user_authorized()

    async def stop(self) -> bool:
        '''Stop and disconnect the Telethon client'''

        try:
            await self._client.disconnect()
            return True

        except:
            return False            

    async def _get_user_state(self, username: str) -> UsernameState:
        '''Specify username status by MTProto API Request'''

        try:
            await self._client(
                functions.account.CheckUsernameRequest(
                    username=username
                )
            )
            return UsernameState.OCCUPIED

        except errors.FloodWaitError:
            return UsernameState.OCCUPIED

        except errors.UsernameInvalidError:
            return UsernameState.INVALID

        except errors.BadRequestError:
            return UsernameState.ON_FRAGMENT

        except:
            return UsernameState.UNKNOWN

    async def scan(self, usernames: list) -> AsyncGenerator[tuple, None]:
        '''Scan usernames and yielding a tuple'''

        for username in usernames:
            user_state = await self._get_user_state(username=username)
            yield username, user_state

        return