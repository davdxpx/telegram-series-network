# Telegram Series Network (TSN Bot)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blueviolet)](https://docs.aiogram.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)](https://www.mongodb.com/atlas)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Telegram Series Network (TSN)** is a professional, self-hosted "mini-Netflix" solution for Telegram. It allows you to create private networks for family and friends to stream your own legally owned media content directly within Telegram, with a polished, app-like experience.

**⚠️ LEGAL DISCLAIMER**: This software is designed strictly for personal use with content you legally own (e.g., home videos, rips of physical media you own). It does not contain any piracy features, scraping tools, or access to illegal content sources. See [LEGAL.md](LEGAL.md) for details.

---

## 🌟 Features

### 📺 Core Experience
*   **Virtual Library**: Organize your files into a clean Series → Seasons → Episodes structure.
*   **Automatic Recognition**: Just upload a file. The bot uses `guessit` to parse the filename (e.g., `Show.Name.S01E02.mkv`) and fetches metadata from TMDB automatically.
*   **Streaming**: Watch videos directly in Telegram or use the **Inline WebApp Player** with seeking, subtitles, and dark mode.
*   **Network Isolation**: One bot instance supports multiple independent "Networks". What happens in your network stays in your network.

### 🚀 Advanced Playback
*   **WebApp Player**: A beautiful HTML5 player that streams securely via a proxy (hiding your bot token) and supports resume functionality.
*   **Cross-Device Progress**: "Continue Watching" saves your spot. Start on your phone, finish on your desktop.
*   **Random Episode**: Can't decide? `/random` plays an unwatched episode from your library.

### 📊 Statistics & Management
*   **Rich Stats**: `/stats` shows total watch time, top series, and most active users.
*   **Role Management**: Owner, Moderators, Uploaders, and Viewers.
*   **Private Storage Channels**: Files are stored in your own private Telegram channels for persistence and redundancy.

---

## 📸 Screenshots

| **Library Browsing** | **Episode Details** | **WebApp Player** |
|:---:|:---:|:---:|
| *[Place Screenshot Here]* | *[Place Screenshot Here]* | *[Place Screenshot Here]* |
| *Browsing Seasons* | *Episode Info & Play* | *Streaming Interface* |

---

## 🛠️ Tech Stack

*   **Language**: Python 3.12+
*   **Bot Framework**: `aiogram` 3.x (Asyncio)
*   **Web Framework**: `FastAPI` (WebApp & Streaming Proxy)
*   **Database**: MongoDB (via `Beanie` ODM + Pydantic v2)
*   **Caching**: Redis
*   **Media Parser**: `guessit`
*   **Metadata**: TMDB API

---

## 🚀 Deployment Guide

### Option A: ☁️ Cloud-First (Recommended)
Use **MongoDB Atlas** (Free Tier) for the database and a VPS/PaaS for the bot.

1.  **Get a MongoDB Connection String**:
    *   Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
    *   Create a Cluster (Free Tier).
    *   Get your connection string (e.g., `mongodb+srv://<user>:<password>@cluster.mongodb.net/...`).
2.  **Get a TMDB API Key**:
    *   Sign up at [TMDB](https://www.themoviedb.org/).
    *   Go to Settings > API to get your key.
3.  **Deploy**:

    [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)
    [![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

    *Set the environment variables `MONGO_URI`, `BOT_TOKEN`, `TMDB_API_KEY` in the dashboard.*

### Option B: 🐳 Self-Hosted (Docker Compose)
Perfect for a home server (Raspberry Pi, NAS, VPS). Includes a local MongoDB container.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/telegram-series-network.git
    cd telegram-series-network
    ```

2.  **Configure Environment**:
    ```bash
    cp .env.example .env
    nano .env
    ```
    *   Fill in `BOT_TOKEN` (from @BotFather).
    *   Fill in `TMDB_API_KEY`.
    *   Leave `MONGO_URI` and `REDIS_URL` as default for local docker setup.

3.  **Run**:
    ```bash
    docker-compose up -d --build
    ```

---

## ⚙️ Configuration (.env)

| Variable | Description | Required |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token | Yes |
| `TMDB_API_KEY` | API Key from The Movie Database | Yes |
| `MONGO_URI` | MongoDB Connection String | Yes |
| `REDIS_URL` | Redis Connection URL | Yes |
| `ADMIN_IDS` | Comma-separated list of Bot Admin IDs | No |
| `LOG_LEVEL` | Logging level (INFO, DEBUG) | No (Default: INFO) |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
