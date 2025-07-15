import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Title ---
st.set_page_config(page_title="My Journal App", layout="centered")
st.title("📔 Journal App with Mood Tracker")

# --- Authentication ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.subheader("🔐 Login to Continue")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        auth_res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if auth_res.user:
            st.session_state.user = auth_res.user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Login failed. Check credentials.")
    st.stop()

# --- Logout ---
st.sidebar.success(f"Logged in as: {st.session_state.user.email}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.user = None
    st.rerun()

# --- Initialize Session State ---
for key, val in {
    "editing": False,
    "edit_id": None,
    "title_input": "",
    "content_input": "",
    "mood_input": "😊 Happy"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Reset form after submission ---
if st.session_state.get("form_submitted", False):
    st.session_state["form_submitted"] = False
    st.session_state["editing"] = False
    st.session_state["edit_id"] = None
    st.session_state["title_input"] = ""
    st.session_state["content_input"] = ""
    st.session_state["mood_input"] = "😊 Happy"
    st.rerun()

# --- Entry Form ---
st.markdown("### ✍️ Write a New Journal Entry")
with st.form("entry_form"):
    st.text_input("Title", key="title_input")
    st.text_area("Write your thoughts here...", key="content_input")
    st.selectbox("Mood / Tag", 
        ["😊 Happy", "😢 Sad", "💡 Inspired", "😌 Relaxed", "🤔 Reflective"],
        key="mood_input"
    )
    submit_label = "Update Entry" if st.session_state.editing else "Save Entry"
    submitted = st.form_submit_button(submit_label)

    if submitted:
        if st.session_state.editing:
            supabase.table("journal_entries").update({
                "title": st.session_state.title_input,
                "content": st.session_state.content_input,
                "mood": st.session_state.mood_input
            }).eq("id", st.session_state.edit_id).execute()
            st.success("Entry updated!")
        else:
            supabase.table("journal_entries").insert({
                "title": st.session_state.title_input,
                "content": st.session_state.content_input,
                "mood": st.session_state.mood_input,
                "user_id": st.session_state.user.id
            }).execute()
            st.success("Entry saved!")

        st.session_state["form_submitted"] = True

# --- Display Entries ---
st.markdown("---")
st.subheader("📚 Your Journal Entries")

entries = supabase.table("journal_entries") \
    .select("*") \
    .eq("user_id", st.session_state.user.id) \
    .order("created_at", desc=True) \
    .execute()

if entries.data:
    for entry in entries.data:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.markdown(f"### {entry['title']}")
            st.markdown(f"🗓️ *{entry['created_at']}*")
            st.markdown(entry['content'])
            st.markdown(f"**Mood:** {entry.get('mood', '😶 None')}")

        with col2:
            if st.button("✏️ Edit", key=f"edit_{entry['id']}"):
                st.session_state.editing = True
                st.session_state.edit_id = entry["id"]
                st.session_state.title_input = entry["title"]
                st.session_state.content_input = entry["content"]
                st.session_state.mood_input = entry.get("mood", "😊 Happy")
                st.rerun()

            if st.button("🗑️ Delete", key=f"delete_{entry['id']}"):
                supabase.table("journal_entries").delete().eq("id", entry["id"]).execute()
                st.success("Entry deleted!")
                st.rerun()
else:
    st.info("No entries yet. Start journaling!")
