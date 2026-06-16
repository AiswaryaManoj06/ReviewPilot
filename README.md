# 🔍 ReviewPilot — AI-Powered Code Review

ReviewPilot is an AI-powered web application that automates the initial code review process by analyzing GitHub pull requests or pasted source code. It uses Google Gemini AI to identify potential bugs, security vulnerabilities, performance bottlenecks, and code quality issues.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-green?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_AI-1.5-purple?style=flat-square&logo=google)

## ✨ Features

- **🐛 Bug Detection** — Identifies potential bugs, logic errors, and edge cases
- **🔒 Security Analysis** — Scans for SQL injection, XSS, hardcoded secrets, and more
- **⚡ Performance Insights** — Detects N+1 queries, memory leaks, and inefficiencies
- **📖 Code Readability** — Evaluates naming, complexity, and maintainability
- **📊 Risk Assessment** — Provides overall risk score with severity levels
- **📋 Structured Reports** — Generates actionable reports with fix suggestions

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Google Gemini API key ([get one free](https://aistudio.google.com/apikey))

### Installation

1. **Clone the repository**
   ```bash
   cd ReviewPilot
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Edit .env and add your Gemini API key
   nano .env
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
ReviewPilot/
├── app.py                 # Flask application & routes
├── ai_utils.py            # Gemini AI integration
├── github_utils.py        # GitHub API integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── static/
│   ├── css/
│   │   └── style.css      # Design system & styles
│   └── js/
│       └── app.js         # Frontend JavaScript
└── templates/
    ├── base.html           # Base template
    ├── index.html          # Landing page
    └── review.html         # Review results page
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python) |
| Frontend | HTML, CSS, JavaScript |
| AI Engine | Google Gemini 1.5 Flash |
| GitHub | REST API v3 |
| Styling | Vanilla CSS (Dark Glassmorphism) |

## 📝 Usage

### Review a GitHub Pull Request
1. Navigate to the app
2. Select the **GitHub PR** tab
3. Paste the PR URL (e.g., `https://github.com/owner/repo/pull/123`)
4. Optionally add a GitHub token for private repos
5. Click **Analyze Pull Request**

### Review a Code Snippet
1. Select the **Code Snippet** tab
2. Choose the programming language (or auto-detect)
3. Paste your code
4. Click **Analyze Code**

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
