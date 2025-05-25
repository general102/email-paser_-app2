import os, json, io, zipfile
import imaplib, email
from email.header import decode_header
import streamlit as st
from dotenv import load_dotenv

# Create `.env` file if missing
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write('IMAP_HOST=\nEMAIL_USER=\nEMAIL_PASS=\n')
    st.warning("`.env` created. Please fill in your IMAP_HOST, EMAIL_USER & EMAIL_PASS and rerun.")
    st.stop()

# Create `lunche.json` if missing
if not os.path.exists('lunche.json'):
    default_rules = {
        "groups": {
            "Alerts": ["alert@", "no-reply@"],
            "Newsletters": ["newsletter@", "digest@"]
        }
    }
    with open('lunche.json', 'w') as f:
        json.dump(default_rules, f, indent=2)
    st.info("`lunche.json` created with default groups. Customize as you like!")

load_dotenv('.env')
IMAP_HOST = os.getenv('IMAP_HOST')
USER = os.getenv('EMAIL_USER')
PASS = os.getenv('EMAIL_PASS')

# Load rules
with open('lunche.json','r') as f:
    rules = json.load(f)

st.title("📧 Email Parser & Organizer")

if not all([IMAP_HOST, USER, PASS]):
    st.error("Please fill in all fields in `.env` and restart.")
    st.stop()

if st.button("Load Emails"):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(USER, PASS)
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        ids = data[0].split()[-20:]
        emails = []
        for i in reversed(ids):
            _, msg_data = mail.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subj, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subj, bytes):
                subj = subj.decode(encoding or 'utf-8', errors='ignore')
            frm = msg.get("From")
            date = msg.get("Date")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            group = "Others"
            for g, keywords in rules.get("groups", {}).items():
                if any(kw.lower() in frm.lower() or kw.lower() in subj.lower() for kw in keywords):
                    group = g
                    break
            emails.append({"From": frm, "Subject": subj, "Date": date, "Snippet": body[:100], "Group": group})
        st.session_state["emails"] = emails
    except Exception as e:
        st.error(f"Failed to fetch: {e}")

if "emails" in st.session_state:
    df = st.session_state["emails"]
    senders = sorted({e["From"] for e in df})
    groups = sorted({e["Group"] for e in df})

    col1, col2 = st.columns(2)
    sel_from = col1.multiselect("Filter by Sender", senders)
    sel_group = col2.multiselect("Filter by Group", groups)

    filtered = [
        e for e in df
        if (not sel_from or e["From"] in sel_from)
        and (not sel_group or e["Group"] in sel_group)
    ]

    for e in filtered:
        st.markdown(f"**{e['Subject']}**  ")
        st.write(f"From: {e['From']}  |  Date: {e['Date']}  |  Group: {e['Group']}")
        st.write(e["Snippet"])
        st.markdown("---")
