# Serene Music Bot

A starter Telegram group voice-chat music bot. It uses:
- Pyrogram bot account for commands
- A separate Telegram user account session as the voice-chat assistant
- PyTgCalls + FFmpeg for voice-chat playback
- yt-dlp for YouTube audio downloads

## Commands
- `/play <YouTube URL>`
- Reply to an audio/voice/document message with `/play`
- `/pause`, `/resume`, `/skip`, `/stop`, `/queue`
- `/volume 1-200`

This starter build has a simple in-memory queue and owner-only controls. The queue is cleared when the service restarts. It does not yet include automatic next-track detection, playlists, search-by-title, or inline controls.

## Telegram setup
1. Create a bot with @BotFather and copy its token.
2. Get `API_ID` and `API_HASH` from https://my.telegram.org.
3. Use a separate Telegram user account as the assistant account. Generate its Pyrogram string session using a trusted session generator you control.
4. Add the bot and assistant account to your group. Make both admins; the assistant account must be able to manage voice chats.
5. Start a voice chat in the group before using `/play`.
6. Get your numeric Telegram user ID and set it as `OWNER_ID`.

Never share your bot token, API hash, or string session. Never commit `.env` or session files to GitHub.

## Render deployment
1. Push this folder to a GitHub repository.
2. In Render, create a **New Web Service** and connect the repository.
3. Choose Docker as the runtime and the Free plan.
4. Add these environment variables in Render:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
   - `STRING_SESSION`
   - `OWNER_ID`
5. Deploy.

Render Free services can sleep after inactivity and are not designed for uninterrupted 24/7 voice-chat streaming. Treat this as a test deployment; playback may stop when the service sleeps or restarts. Local `/tmp` downloads and the in-memory queue are temporary.

## Important
Telegram voice-chat APIs and YouTube availability can change. Test first in a private group. Use audio only when you have the rights and permission to stream it.
