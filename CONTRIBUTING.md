# Contributing to Telegram Series Network (TSN)

Thank you for your interest in contributing to TSN! We want to make this the best Telegram media bot available, and your help is appreciated.

## 🛠️ How to Contribute

### 1. Reporting Bugs
If you find a bug, please open an Issue on GitHub. Include:
*   Your OS and Docker version.
*   Steps to reproduce the bug.
*   Logs (remove sensitive info like API keys!).

### 2. Suggesting Features
Have an idea? Open a "Feature Request" issue. We love hearing how to improve the "Single Network" experience.

### 3. Pull Requests
*   **Fork the repo** and create a new branch (`feature/my-new-feature` or `fix/bug-fix`).
*   **Code Style**: We use `ruff` and `black` for Python formatting. Please ensure your code is clean and commented.
*   **Testing**: If you add a new feature, please test it thoroughly.
*   **Commit Messages**: Write clear, descriptive commit messages.

## ⚠️ Important Guidelines

1.  **No Piracy Features**: We will **reject** any PR that adds scraping capabilities (e.g., torrent search, yt-dlp integration for illegal sites) or features designed solely to facilitate copyright infringement. This project is for *organizing own files*, not *finding files*.
2.  **Security**: Never expose the `BOT_TOKEN` or `TMDB_API_KEY` in the client-side code (WebApp). Always use the backend proxy.

## 🏗️ Development Setup

1.  Clone your fork.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Set up a local MongoDB (or use the `docker-compose.yml` provided).
4.  Run the bot: `python -m app.main`.

Thank you for building with us!
