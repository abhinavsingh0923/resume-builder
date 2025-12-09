# 🚀 AI Resume Builder

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Powered-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Built with uv](https://img.shields.io/badge/Built%20with-uv-purple?style=for-the-badge)](https://github.com/astral-sh/uv)

**Build your dream resume with the power of Artificial Intelligence.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Docker](#-docker-setup) • [Usage](#-usage-guide)

</div>

---

## 📖 Introduction

**AI Resume Builder** is a next-generation resume creation tool that leverages **Google's Gemini AI** to act as your personal career coach. Unlike static templates, this intelligent application effectively *interviews* you, extracts your key achievements, and automatically formats them into a professional, ATS-optimized resume.

Stop struggling with writer's block. Let our agents guide you through building a CV that stands out.

## 🌟 Features

### 🧠 Intelligent AI Agents
- **Reviewer Agent**: Analyzes your target job description and asks probing questions to gather relevant experience.
- **Refinement Agent**: Instantly transforms basic answers into powerful, STAR-method (Situation, Task, Action, Result) bullet points.
- **ATS Scanner**: Real-time scoring of your resume against the job requirements with actionable feedback.

### ⚡ Modern Experience
- **Interactive Chat Interface**: Build your resume through a natural conversation.
- **Real-time Preview**: See your resume evolve as you answer questions.
- **Auth System**: Secure login/signup to save multiple versions of your resume.

### 📄 Professional Output
- **One-Click PDF**: Generate beautifully formatted, standard-compliant PDFs ready for application.
- **Clean Design**: Minimalist and professional layout favored by recruiters.

## �️ Tech Stack

This project is built with a modern, robust stack designed for performance and scalability.

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | Interactive web interface |
| **Orchestration** | ![LangChain](https://img.shields.io/badge/-LangGraph-1C3C3C?style=flat-square) | Agent workflow orchestration |
| **LLM** | ![Gemini](https://img.shields.io/badge/-Google%20Gemini-4285F4?style=flat-square&logo=google&logoColor=white) | The brains behind the operation |
| **Database** | ![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white) | User and session data storage |
| **Package Manager** | ![uv](https://img.shields.io/badge/-uv-purple?style=flat-square) | Blazing fast Python package installer |
| **Containerization** | ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Easy deployment |

## 🚀 Installation

### Prerequisites
- **Python 3.12+**
- **MongoDB** (Local or Atlas URL)
- **Google Cloud API Key** (Gemini)

### Local Setup (The Fast Way with `uv`)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-resume-builder.git
   cd ai-resume-builder
   ```

2. **Install `uv` (if not installed)**
   ```bash
   pip install uv
   ```

3. **Sync Dependencies**
   ```bash
   uv sync
   ```

4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=resume_builder
   ```

5. **Run the App**
   ```bash
   uv run streamlit run app/main.py
   ```
   Visit `http://localhost:8501` to start building!

## 🐳 Docker Setup

We provide a fully dockerized environment for zero-hassle setup.

1. **Ensure Docker is running**.

2. **Configure `.env`** as shown above.

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the App**
   Open your browser at `http://localhost:8501`.

   *Note: The MongoDB service is automatically set up on port `27017`.*

## 📂 Project Structure

```text
.
├── app/
│   ├── agents/          # AI Agent definitions & Graphs
│   ├── core/            # Database & Auth logic
│   ├── pages/           # Streamlit sub-pages (Builder UI)
│   ├── services/        # PDF Generation & external services
│   ├── ui/              # Reusable UI components
│   └── main.py          # Entry point
├── .dockerignore        # Docker build exclusions
├── Dockerfile           # App container definition
├── docker-compose.yaml  # Orchestration service definition
├── pyproject.toml       # Dependencies (uv/standard)
└── uv.lock              # Lockfile
```

## 📝 Usage Guide

1. **Sign Up**: Create an account to save your progress.
2. **Dashboard**: View past sessions or start a new one.
3. **Start New**: Paste the **Job Description** you are applying for.
4. **Chat**: Answer the AI's questions about your experience. Watch as it refines your answers.
5. **Review**: Check the Real-time ATS score in the sidebar.
6. **Download**: Once satisfied, click **Download PDF**.

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
<div align="center">
Made with ❤️ by the AI Resume Builder Team
</div>
