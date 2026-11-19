# Serene Music Bot — Render Docker starter

This package fixes the import path (`from youtube import download_youtube`) and adds a Dockerfile with FFmpeg for Render's Docker runtime.

## Features in this starter
- `/play <YouTube URL>`
- Reply to an audio/voice/document message with `/play`
- `/pause`, `/resume`, `/skip`, `/stop`, `/queue`, `/volume 1-200`
- Separate Pyrogram assistant user session for voice-chat playback
- HTTP health endpoint at `/` and `/health`

## Render setup
1. Upload these files to the root of your GitHub repository (replace the old files; keep the new Dockerfile).
2. In Render, create a **New Web Service** and connect the repository.
3. Select **Docker** as runtime and choose the Free plan for testing.
4. Add environment variables exactly as follows:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
   - `STRING_SESSION`
   - `OWNER_ID`
5. Deploy. The Dockerfile installs FFmpeg and starts `python main.py`.

## Telegram setup
- Add the bot and the assistant user account to your group.
- Make both admins as needed; the assistant user account must be able to manage voice chats.
- Start a voice chat before testing `/play`.
- `OWNER_ID` must be your numeric Telegram user ID.

## Important limitations
- This is a starter build, not a fully tested production release. Test in a private group first.
- Queue state is in memory and is lost on restart. It does not include inline controls, shuffle, playlist search, or automatic next-track detection.
- Render Free web services may sleep or restart; this does **not** guarantee uninterrupted 24/7 voice-chat playback.
- Keep all tokens and session strings private. Never upload `.env` or session files to GitHub.
- Use audio only when you have the rights and permission to stream it.
