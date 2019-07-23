# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.


# This is based on https://github.com/SijmenSchoon/regexbot
# but slightly different.
# https://stackoverflow.com/a/46100580 is also very helpful with the
# explanation on how we could make it work and what we'd need to check.


import re

from userbot.events import outgoing


pattern = r'^(\d+?)?(?:s|sed)/((?:\\/|[^/])+)/((?:\\/|[^/])*)(/.*)?'

async def matchSplitter(match):
    fr = match.group(2)
    to = match.group(3)
    to = re.sub(r'\\/', '/', to)
    to = re.sub(r'\\0', r'\g<0>', to)
    fl = match.group(4)[1:] if match.group(4) else ''

    return fr, to, fl


@outgoing(pattern=pattern, prefix=None)
async def sed(client, event):
    match = event.matches[0]
    line = match.group(1)
    reply = event.reply_to_message

    fr, to, fl = await matchSplitter(match)
    count = 1
    flags = 0

    for f in fl.lower():
        if f == 'a':
            flags |= re.ASCII
        elif f == 'i':
            flags |= re.IGNORECASE
        elif f == 'l':
            flags |= re.LOCALE
        elif f == 'm':
            flags |= re.MULTILINE
        elif f == 's':
            flags |= re.DOTALL
        elif f == 'u':
            flags |= re.UNICODE
        elif f == 'x':
            flags |= re.VERBOSE
        elif f == 'g':
            count = 0
        else:
            await event.edit('Unknown flag: ' + f)
            return

    async def substitute(original):
            s, i = re.subn(fr, to, original, count=count, flags=flags)
            if i > 0:
                return s
            return None

    try:
        if reply:
            original = reply.text or reply.caption
            if not original:
                return

        else:
            original = None
            async for msg in client.iter_history(event.chat.id, offset=1):
                if msg.text:
                    original = msg.text
                    break
                elif msg.caption:
                    original = msg.caption
                    break

        if line:
            line = int(line)
            lines = original.splitlines()
            if len(lines) < line:
                await event.edit("What line? Heh.")
                return

            newLine = await substitute(lines[line - 1])
            lines[line - 1] = newLine
            newStr = '\n'.join(lines)
        else:
            newStr = await substitute(original)

        await event.edit(newStr)

    except Exception as e:
        await event.edit('Like regexbox says, fuck me.\n' + str(e))