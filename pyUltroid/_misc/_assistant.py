# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import inspect
import re
from traceback import format_exc

from telethon import Button
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery, NewMessage
from telethon.tl.types import InputWebDocument

from .. import LOGS, asst, udB, ultroid_bot
from ..fns.admins import admin_check
from . import append_or_update, owner_and_sudos

OWNER = ultroid_bot.full_name

MSG = f"""
**Ryn - UserBot**
➖➖➖➖➖➖➖➖➖➖
**🤴 Owner**: [{OWNER}](tg://user?id={ultroid_bot.uid})
**Support 📝**: @TatsuyaMusicStream
➖➖➖➖➖➖➖➖➖➖
"""

IN_BTTS = [
    [
        Button.url(
            "🤴 Owner",
            url="https://t.me/Usern4DoestExist404",
        ),
        Button.url("Support 📝", url="https://t.me/TatsuyaMusicStream"),
    ]
]


# decorator for assistant


def asst_cmd(pattern=None, load=None, owner=False, **kwargs):
    """𝗗𝗲𝗰𝗼𝗿𝗮𝘁𝗼𝗿 𝗳𝗼𝗿 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁'𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"""
    name = inspect.stack()[1].filename.split("/")[-1].replace(".py", "")
    kwargs["forwards"] = False

    def ult(func):
        if pattern:
            kwargs["pattern"] = re.compile(f"^/{pattern}")

        async def handler(event):
            if owner and event.sender_id not in owner_and_sudos():
                return
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(handler, NewMessage(**kwargs))
        if load is not None:
            append_or_update(load, func, name, kwargs)

    return ult


def callback(data=None, from_users=[], admins=False, owner=False, **kwargs):
    """𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁'𝘀 𝗰𝗮𝗹𝗹𝗯𝗮𝗰𝗸 𝗱𝗲𝗰𝗼𝗿𝗮𝘁𝗼𝗿"""
    if "me" in from_users:
        from_users.remove("me")
        from_users.append(ultroid_bot.uid)

    def ultr(func):
        async def wrapper(event):
            if admins and not await admin_check(event):
                return
            if from_users and event.sender_id not in from_users:
                return await event.answer("Not for You!", alert=True)
            if owner and event.sender_id not in owner_and_sudos():
                return await event.answer(f"This is {OWNER}'s bot!!")
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(wrapper, CallbackQuery(data=data, **kwargs))

    return ultr


def in_pattern(pattern=None, owner=False, **kwargs):
    """𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁'𝘀 𝗶𝗻𝗹𝗶𝗻𝗲 𝗱𝗲𝗰𝗼𝗿𝗮𝘁𝗼𝗿."""

    def don(func):
        async def wrapper(event):
            if owner and event.sender_id not in owner_and_sudos():
                res = [
                    await event.builder.article(
                        title="Ultroid Userbot",
                        url="https://t.me/TatsuyaMusicStream",
                        description="(c) TatsuyaMusicStream",
                        text=MSG,
                        thumb=InputWebDocument(
                            "https://telegra.ph/file/b532ea30e4848301684c3.jpg",
                            0,
                            "image/jpeg",
                            [],
                        ),
                        buttons=IN_BTTS,
                    )
                ]
                return await event.answer(
                    res,
                    switch_pm=f"🤖: Assistant of {OWNER}",
                    switch_pm_param="start",
                )
            try:
                await func(event)
            except QueryIdInvalidError:
                pass
            except Exception as er:
                err = format_exc()

                def error_text():
                    return f"**#ERROR #INLINE**\n\nQuery: `{asst.me.username} {pattern}`\n\n**Traceback:**\n`{format_exc()}`"

                LOGS.exception(er)
                try:
                    await event.answer(
                        [
                            await event.builder.article(
                                title="Unhandled Exception has Occured!",
                                text=error_text(),
                                buttons=Button.url(
                                    "Support", "https://t.me/TatsuyaMusicStream"
                                ),
                            )
                        ]
                    )
                except QueryIdInvalidError:
                    LOGS.exception(err)
                except Exception as er:
                    LOGS.exception(er)
                    await asst.send_message(udB.get_key("LOG_CHANNEL"), error_text())

        asst.add_event_handler(wrapper, InlineQuery(pattern=pattern, **kwargs))

    return don
