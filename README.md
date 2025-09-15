# NLP to SQL - Streamlit App

A professional and minimal Streamlit application that demonstrates natural language to SQL conversion capabilities.

## Features

- 🤖 AI-powered natural language processing
- 💬 Intuitive query interface  
- ⚡ Fast and accurate SQL generation
- 🔒 Secure and reliable processing

## Deployment

This app is designed for deployment on Streamlit Cloud. The AI provider configuration is read from environment variables.

### Environment Variables Required

- `AI_PROVIDER`: The AI service provider (e.g., "claude")

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration (see `.env.example`)

3. Run the app:
```bash
streamlit run app.py
```

## Tech Stack

- **Streamlit**: Web application framework
- **Python-dotenv**: Environment variable management
- **AI Integration**: Configurable AI provider support

---

Built with ❤️ using Streamlit