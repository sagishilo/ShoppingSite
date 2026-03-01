import streamlit as st
import requests
import random
st.set_page_config(page_title="ShoppingSite", page_icon="🛒", layout="wide")

API_URL = "http://localhost:8000"

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "user" not in st.session_state:
    st.session_state["user"] = None  # מידע על המשתמש המחובר

# ---------- HEADER ----------
def render_header():
    col1, col2, col3 = st.columns([6, 2, 2])

    with col1:
        st.markdown("## 🛒 ShoppingSite")

    with col2:
        if st.session_state["user"]:
            st.write(f"שלום, {st.session_state['user']['user_name']} 👋")
        else:
            if st.button("הרשמה"):
                st.session_state["page"] = "register"

    with col3:
        if st.session_state["user"] is None:
            if st.button("התחברות"):
                st.session_state["page"] = "login"
        else:
            if st.button("התנתק"):
                st.session_state["user"] = None
                st.session_state["page"] = "home"

    st.divider()

# ---------- PAGES ----------
def show_home_page():
    render_header()
    st.markdown("### 🔥 כל המוצרים")

    # ---------- LOAD PRODUCTS ----------
    @st.cache_data(ttl=30)
    def get_items():
        response = requests.get(f"{API_URL}/item", timeout=5)
        response.raise_for_status()
        return response.json()

    try:
        products = get_items()
    except Exception:
        st.error("❌ לא ניתן לטעון מוצרים מהשרת")
        st.stop()

    if not products:
        st.info("אין מוצרים זמינים כרגע")
        return

    # ---------- PLACEHOLDER IMAGES ----------
    PLACEHOLDER_IMAGES = [
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "https://images.unsplash.com/photo-1518441902117-fec81d36d6d0",
        "https://images.unsplash.com/photo-1587202372775-e229f172b9d7"
    ]

    # ---------- GRID ----------
    cols = st.columns(4)
    for idx, product in enumerate(products):
        with cols[idx % 4]:
            st.image(
                random.choice(PLACEHOLDER_IMAGES),
                use_container_width=True
            )
            st.markdown(f"**{product['item_name']}**")
            st.markdown(f"💰 {product['price']} ₪")
            st.button("הוסף לעגלה", key=f"add_{idx}")

    st.divider()
    st.caption("© 2026 ShoppingSite")

# ---------- REGISTER PAGE ----------
def show_register_page():
    render_header()
    st.title("📝 הרשמה לאתר")

    with st.form("signup_form"):
        first_name = st.text_input("שם פרטי")
        last_name = st.text_input("שם משפחה")
        user_name = st.text_input("שם משתמש")
        email = st.text_input("אימייל")
        phone = st.text_input("טלפון")
        address = st.text_input("כתובת")
        password = st.text_input("סיסמה", type="password")
        confirm_password = st.text_input("אימות סיסמה", type="password")

        submitted = st.form_submit_button("הרשמה")

    if submitted:
        if not all([first_name, last_name, user_name, email, password, confirm_password]):
            st.error("❌ יש למלא את כל השדות החובה")
        elif password != confirm_password:
            st.error("❌ הסיסמאות לא תואמות")
        else:
            payload = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "address": address,
                "user_name": user_name,
                "password": password
            }

            try:
                # ⚠️ POST ל-endpoint הנכון
                response = requests.post(f"{API_URL}/user", json=payload, timeout=5)

                if response.status_code in (200, 201):
                    st.success("✅ המשתמש נוצר בהצלחה!")
                    st.session_state["user"] = {"user_name": user_name}
                    st.session_state["page"] = "home"
                elif response.status_code == 409:
                    st.error("❌ שם המשתמש כבר קיים")
                else:
                    st.error(f"❌ שגיאה: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ לא ניתן להתחבר לשרת")

# ---------- LOGIN PAGE ----------
def show_login_page():
    render_header()
    st.title("🔐 התחברות")

    with st.form("login_form"):
        user_name = st.text_input("שם משתמש")
        password = st.text_input("סיסמה", type="password")
        submitted = st.form_submit_button("התחבר")

    if submitted:
        if not user_name or not password:
            st.error("❌ יש למלא שם משתמש וסיסמה")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/user/login",
                    json={"user_name": user_name, "password": password},
                    timeout=5
                )

                if response.status_code == 200:
                    st.success("✅ התחברת בהצלחה!")
                    st.session_state["user"] = {"user_name": user_name}
                    st.session_state["page"] = "home"
                else:
                    st.error("❌ שם משתמש או סיסמה לא נכונים")

            except requests.exceptions.ConnectionError:
                st.error("❌ לא ניתן להתחבר לשרת")



# ---------- ROUTER ----------
if st.session_state["page"] == "home":
    show_home_page()
elif st.session_state["page"] == "register":
    show_register_page()
elif st.session_state["page"] == "login":
    show_login_page()
