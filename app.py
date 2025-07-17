import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client  # ✅ Correct


# Load environment variables from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# App title
st.set_page_config(page_title="My Journal", page_icon="📝")
st.title("📝 My Personal Journal")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------------
# 🔐 AUTH BLOCK
# -------------------------------
def show_login_signup():
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res and res.user:
                    st.success("✅ Logged in successfully!")
                    st.session_state.user = res.user
                    st.rerun()
                else:
                    st.error("❌ Login failed. Check credentials.")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        if st.button("Create Account"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                if res and res.user:
                    st.success("✅ Account created. Please check your email to confirm.")
                else:
                    st.error("❌ Signup failed. Try again or use another email.")
            except Exception as e:
                st.error(f"Signup error: {str(e)}")

# -------------------------------
# 📝 JOURNAL DASHBOARD
# -------------------------------
def show_journal_dashboard():
    st.write(f"👋 Welcome, **{st.session_state.user.email}**")

    with st.form("journal_form", clear_on_submit=True):
        title = st.text_input("Title")
        content = st.text_area("Write your thoughts...")
        mood = st.selectbox("Mood", ["😊 Happy", "😢 Sad", "😤 Angry", "😐 Neutral"])
        submitted = st.form_submit_button("Save Entry")
        if submitted:
            try:
                data = {
                    "title": title,
                    "content": content,
                    "mood": mood,
                    "user_id": st.session_state.user.id
                }
                supabase.table("journal_entries").insert(data).execute()
                st.success("✅ Entry saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving entry: {str(e)}")

    # Fetch and display journal entries
    try:
        result = supabase.table("journal_entries").select("*").eq("user_id", st.session_state.user.id).order("id", desc=True).execute()
        entries = result.data if result and result.data else []
        if entries:
            st.subheader("📚 Your Entries")
            for entry in entries:
                with st.expander(f"{entry['title']} ({entry['mood']})"):
                    st.write(entry["content"])
        else:
            st.info("No journal entries yet. Start writing!")
    except Exception as e:
        st.error(f"Error fetching entries: {str(e)}")

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

# -------------------------------
# 🚀 MAIN APP
# -------------------------------
if st.session_state.user is None:
    show_login_signup()
else:
    show_journal_dashboard()
