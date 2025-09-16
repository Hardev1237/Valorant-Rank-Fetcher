<div align="center">
  <h1>🎯 Valorant Rank Checker 🎯</h1>
  <p>
    A local web application built with Python to check, save, and automatically track Valorant player ranks.
  </p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/Framework-http.server-orange?style=for-the-badge" alt="http.server">
  <img src="https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite" alt="SQLite">
</p>

---

## ✨ Features

-   **🔍 Rank Checking**: Check any player's rank using their Riot ID and region.
-   **💾 Account Saving**: Save accounts to a local SQLite database for easy tracking.
-   **🔐 Credential Storage**: Optionally store account username and password securely.
-   **🗂️ Custom Sections**: Organize your saved accounts into personalized categories.
-   **🔄 Automatic Refresh**: A background thread automatically updates ranks every minute.
-   **💻 Modern Web Interface**: A clean and simple UI to interact with the application.

---

## 📂 Project Structure

```
├── 📄 app.py            # Main Python web server (http.server)
├── 📄 database.py       # SQLite database management class
├── 📄 api_client.py     # Handles communication with the Valorant API
└── 📁 static/
    ├── 📄 index.html    # Main HTML page
    ├── 📄 style.css     # All CSS styles
    └── 📄 script.js     # Client-side JavaScript
```
---

## 🛠️ Prerequisites

-   **Python 3.6+**
-   The `requests` library

---

## 🚀 How to Run

1.  **Clone the Repository**
    Clone the repository or save all the files into a directory, maintaining the structure outlined above.

2.  **Install Dependencies**
    Open your terminal and install the required Python package.
    >```bash
    >pip install requests
    >```

3.  **Launch the Application**
    Navigate to the project's root directory in your terminal and run the main server file.
    >```bash
    >python app.py
    >```

4.  **Open in Browser**
    The script will automatically open the application in your default web browser at `http://localhost:8000`. You will see server logs and refresh task updates in your terminal.

5.  **🛑 Stop the Server**
    To stop the application, press `Ctrl+C` in the terminal where the server is running.
