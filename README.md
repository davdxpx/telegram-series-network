# Telegram Series Network (TSN Bot)

**Your Personal Netflix for Telegram.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blueviolet)](https://docs.aiogram.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)](https://www.mongodb.com/atlas)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## 🚀 Overview

**Telegram Series Network (TSN)** is a self-hostable, production-grade Telegram bot that creates a private, legal "mini-Netflix" for you and your close circle (family/friends). It transforms your legally owned media files into a polished streaming service directly within Telegram.

### 🔑 Core Philosophy: Single Network
Unlike multi-tenant bots, **one deployed instance of TSN represents exactly one private Network**.
*   **You (the deployer) are the Owner/Admin.**
*   **You define who has access.**
*   **You control the content.**

This architecture ensures complete privacy, data sovereignty, and performance isolation.

---

## ✨ Key Features

### 🎬 For Viewers
*   **Professional Library**: Browse Series → Seasons → Episodes with rich metadata (posters, plots, ratings) fetched automatically from TMDB.
*   **Smart Playback**:
    *   **Direct Streaming**: Watch instantly via our custom WebApp Player (HTML5).
    *   **Continue Watching**: Cross-device progress tracking. Pause on mobile, resume on desktop.
    *   **Subtitles**: Full support for embedded and external subtitles.
*   **Discovery**:
    *   **Global Search**: Find any episode across all bundles.
    *   **Random Episode**: Let the bot pick an unwatched episode for you.
    *   **Stats**: View personal watch time and network-wide trends.

### 🛠️ For the Owner (Admin)
*   **Powerful Admin WebApp**: manage everything from a beautiful dashboard (accessible via `/admin` or direct link).
    *   **Storage Management**: Connect private Telegram channels as "DB Channels".
    *   **Bundle System**: Create curated collections (e.g., "Marvel Phase 1", "90s Cartoons").
    *   **Batch Import**: The crown jewel of TSN. Upload 100s of files to a channel, and the bot will automatically:
        1.  Detect the show/movie from the filename.
        2.  Fetch metadata.
        3.  Organize them into Seasons/Episodes.
        4.  Add them to the selected Bundle.
    *   **User Management**: Invite users, assign roles (Viewer, Uploader, Moderator), and ban access.
    *   **Analytics**: Deep insights into storage usage and user engagement.

---

## 🏗️ Architecture & Flow

### The "DB Channel" Concept
TSN does not store files on your server. Instead, it leverages Telegram's unlimited cloud storage securely.
1.  **Create a Private Channel**: This is your "Storage Unit".
2.  **Add the Bot**: Make the bot an Admin in this channel.
3.  **Link in Admin Panel**: The bot now listens to this channel.
4.  **Upload**: You upload video files to this channel.
5.  **Indexing**: The bot detects new files, indexes them in its database, and makes them streamable in the WebApp.

**Zero Bandwidth Cost for Storage**: Your server only handles the lightweight database and the streaming proxy (which tunnels the stream from Telegram to the user).

---

## 🚀 Deployment Guide

### Prerequisites
*   **Telegram Bot Token**: Get one from [@BotFather](https://t.me/BotFather).
*   **TMDB API Key**: Get one from [The Movie Database](https://www.themoviedb.org/documentation/api).
*   **MongoDB**: Use [MongoDB Atlas (Free Tier)](https://www.mongodb.com/cloud/atlas) or a local instance.

### Option A: Docker Compose (Recommended)
Perfect for VPS (DigitalOcean, Hetzner, AWS) or Home Server.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/telegram-series-network.git
    cd telegram-series-network
    ```

2.  **Configure Environment**
    ```bash
    cp .env.example .env
    nano .env
    ```
    *   `BOT_TOKEN`: Your Telegram Bot Token.
    *   `OWNER_TELEGRAM_ID`: Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot)). **Crucial for Admin Access.**
    *   `TMDB_API_KEY`: Your TMDB API Key.
    *   `MONGO_URI`: Connection string (default is valid for local docker).
    *   `Host`: The public URL of your bot (e.g., `https://tsn-bot.yourdomain.com`).

3.  **Run with Docker**
    ```bash
    docker-compose up -d --build
    ```

4.  **Initialize**
    *   Open your bot in Telegram.
    *   Type `/start`.
    *   If you are the `OWNER_TELEGRAM_ID`, you will see the Admin Menu.

### Option B: Cloud Deployment (Railway/Render/Heroku)
1.  Fork this repository.
2.  Connect your repo to the cloud provider.
3.  Set the Environment Variables in the provider's dashboard.
4.  Deploy!

---

## 📖 User Manual

### 1. Setting Up Your First Bundle (Batch Import)
The fastest way to populate your network.

1.  **Create a Channel**: Create a new Private Channel in Telegram (e.g., "My Series Storage").
2.  **Add Bot**: Add your TSN Bot as an Administrator to this channel.
3.  **Open Admin Panel**: Send `/admin` to the bot and open the WebApp.
4.  **Add Storage**: Go to **Storage Channels** -> **Add Channel**. Paste the invite link or ID.
5.  **Create Bundle**: Go to **Bundles** -> **Create Bundle**. Name it (e.g., "Sci-Fi Classics").
6.  **Start Import**:
    *   Go to **Batch Import**.
    *   Select the Storage Channel and the Target Bundle.
    *   Click **Start Batch**.
7.  **Upload Files**: Go to your Telegram Channel and upload your video files.
    *   *Tip: Ensure filenames are clean (e.g., "Firefly.S01E01.mkv") for best detection.*
8.  **Finish**: Click **Finish Batch** in the WebApp.
    *   The bot now processes the queue, fetches metadata, and builds your library.

### 2. Watching Content
*   **Home**: The WebApp Home shows "Continue Watching" and "Featured Bundles".
*   **Search**: Use the global search bar to find specific episodes.
*   **Player**: Click "Play" to open the HTML5 player. It supports:
    *   **Quality Selection**: (If multiple versions exist).
    *   **Subtitles**: Toggle on/off.
    *   **Speed**: 0.5x to 2x.

---

## ⚖️ Legal & Disclaimer

**This software is for personal use only.**
By using this bot, you agree to:
1.  Only upload content you legally own (e.g., personal backups, home videos).
2.  Not use this software for piracy or copyright infringement.
3.  Not share access to your instance publicly.

The developers of TSN Bot accept **no liability** for misuse. This is an open-source tool for file organization and private streaming.

See [LEGAL.md](LEGAL.md) for the full legal text.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to report bugs, suggest features, and submit Pull Requests.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
