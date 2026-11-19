import asyncio
import logging
import os
from collections import deque

from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID
from modules.youtube import download_youtube

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("serene")

# The user account joins the voice chat. The bot account handles commands.
assistant = Client(
    "serene_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
)
bot = Client("serene_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
calls = PyTgCalls(assistant)

queues = {}
current_files = {}
play_locks = {}


def is_owner(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == OWNER_ID)


def chat_queue(chat_id):
    return queues.setdefault(chat_id, deque())


async def start_track(chat_id, path, title="Audio"):
    await calls.play(chat_id, AudioPiped(path))
    current_files[chat_id] = path
    return title


async def next_track(chat_id):
    q = chat_queue(chat_id)
    if not q:
        current_files.pop(chat_id, None)
        return False
    path, title = q.popleft()
    await start_track(chat_id, path, title)
    return title


@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message):
    await message.reply_text(
        "🎧 **Serene Music Bot is online!**\n\n"
        "Add me to your group and make me an admin. "
        "The assistant account must also be in the group and have permission "
        "to manage voice chats.\n\n"
        "Commands: /play, /pause, /resume, /skip, /stop, /queue, /volume"
    )


@bot.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(
        "**Serene Music Bot commands**\n"
        "/play <YouTube URL> — play YouTube audio\n"
        "Reply /play to an audio file — play Telegram audio\n"
        "/pause — pause\n/resume — resume\n/skip — skip current track\n"
        "/stop — stop and clear queue\n/queue — show queued tracks\n"
        "/volume 1-200 — set volume\n\n"
        "Only the configured owner can control this starter version."
    )


@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(_, message):
    if not is_owner(message):
        return await message.reply_text("Only the bot owner can use this command.")

    chat_id = message.chat.id
    status = await message.reply_text("🔎 Getting your audio...")

    try:
        if message.reply_to_message and (
            message.reply_to_message.audio or message.reply_to_message.voice
            or message.reply_to_message.document
        ):
            media = (message.reply_to_message.audio
                     or message.reply_to_message.voice
                     or message.reply_to_message.document)
            path = await message.reply_to_message.download(
                file_name=f"/tmp/serene_{chat_id}_{media.file_unique_id}"
            )
            title = getattr(media, "file_name", None) or "Telegram audio"
        else:
            if len(message.command) < 2:
                return await status.edit_text(
                    "Send `/play YouTube_URL` or reply to an audio file with `/play`."
                )
            url = message.text.split(maxsplit=1)[1].strip()
            path, title = await download_youtube(url, chat_id)

        q = chat_queue(chat_id)
        if chat_id in current_files:
            q.append((path, title))
            await status.edit_text(f"➕ Added to queue: **{title}**")
        else:
            await start_track(chat_id, path, title)
            await status.edit_text(f"▶️ Now playing: **{title}**")
    except Exception as exc:
        log.exception("Could not start playback")
        await status.edit_text(f"❌ Couldn't play that audio: `{exc}`")


@bot.on_message(filters.command("pause") & filters.group)
async def pause_cmd(_, message):
    if not is_owner(message):
        return
    try:
        await calls.pause(message.chat.id)
        await message.reply_text("⏸ Paused.")
    except Exception as exc:
        await message.reply_text(f"Couldn't pause: `{exc}`")


@bot.on_message(filters.command("resume") & filters.group)
async def resume_cmd(_, message):
    if not is_owner(message):
        return
    try:
        await calls.resume(message.chat.id)
        await message.reply_text("▶️ Resumed.")
    except Exception as exc:
        await message.reply_text(f"Couldn't resume: `{exc}`")


@bot.on_message(filters.command("skip") & filters.group)
async def skip_cmd(_, message):
    if not is_owner(message):
        return
    chat_id = message.chat.id
    try:
        await calls.leave_call(chat_id)
        current_files.pop(chat_id, None)
        title = await next_track(chat_id)
        await message.reply_text(f"⏭ Skipped. Now playing: **{title}**" if title else "⏹ Queue is empty.")
    except Exception as exc:
        await message.reply_text(f"Couldn't skip: `{exc}`")


@bot.on_message(filters.command("stop") & filters.group)
async def stop_cmd(_, message):
    if not is_owner(message):
        return
    chat_id = message.chat.id
    try:
        await calls.leave_call(chat_id)
    except Exception:
        pass
    current_files.pop(chat_id, None)
    chat_queue(chat_id).clear()
    await message.reply_text("⏹ Playback stopped and queue cleared.")


@bot.on_message(filters.command("queue") & filters.group)
async def queue_cmd(_, message):
    q = list(chat_queue(message.chat.id))
    if not q:
        return await message.reply_text("The queue is empty.")
    lines = [f"{i}. {title}" for i, (_, title) in enumerate(q, 1)]
    await message.reply_text("**Queued tracks**\n" + "\n".join(lines[:20]))


@bot.on_message(filters.command("volume") & filters.group)
async def volume_cmd(_, message):
    if not is_owner(message):
        return
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply_text("Usage: `/volume 1-200`")
    volume = int(message.command[1])
    if not 1 <= volume <= 200:
        return await message.reply_text("Volume must be between 1 and 200.")
    try:
        await calls.change_volume_call(message.chat.id, volume)
        await message.reply_text(f"🔊 Volume set to {volume}%.")
    except Exception as exc:
        await message.reply_text(f"Couldn't change volume: `{exc}`")


async def health(_request):
    return web.Response(text="Serene Music Bot is running.")


async def run_health_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "10000")))
    await site.start()
    return runner


async def main():
    runner = await run_health_server()
    await assistant.start()
    await bot.start()
    await calls.start()
    log.info("Serene Music Bot started")
    try:
        await asyncio.Event().wait()
    finally:
        await calls.stop()
        await bot.stop()
        await assistant.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
