
# Email Parser & Organizer (Streamlit)

## Setup (Local)

1. Unzip the project.
2. In VS Code terminal:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deploy on Streamlit Cloud

1. Push this to a GitHub repo.
2. Deploy using https://streamlit.io/cloud
3. Go to App → Settings → Secrets and paste:

```toml
IMAP_HOST = "your.imap.server"
EMAIL_USER = "your@email.com"
EMAIL_PASS = "your-app-password"
```
