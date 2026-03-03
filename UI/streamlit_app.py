import datetime

import streamlit as st
import requests

# ---------- CONFIG ----------



st.set_page_config(page_title="ShoppingSite", page_icon="🛒", layout="wide")

API_URL = "http://localhost:8000"



def show_order_success_page():
    render_header()
    st.balloons()
    st.container()
    finalize_checkout()
    st.success("🎊 ההזמנה שלך בוצעה בהצלחה!")
    st.write("תודה שקנית ב-ShoppingSite. נשמח לראות אותך שוב בקרוב.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛍️ חזרה לקניות", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
    with col2:
        if st.button("🚪 התנתקות", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["cart"] = []
            st.session_state["temp_order_id"] = None
            st.session_state["page"] = "home"
            st.rerun()


# ---------- SESSION STATE ----------

if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "user" not in st.session_state:
    st.session_state["user"] = None
if "cart" not in st.session_state:
    st.session_state["cart"] = []
if "temp_order_id" not in st.session_state:
    st.session_state["temp_order_id"] = None
if st.session_state["page"] == "order_success":  # עמוד חדש
    show_order_success_page()

# ---------- API ----------

# פונקציית עזר לטעינת עגלה מהשרת (סטטוס TEMP)
def sync_cart_from_db():
    user = st.session_state.get("user")
    if user and "user_id" in user:
        user_id = user["user_id"]
        try:
            # שלב 1: מציאת הזמנת TEMP
            res_order = requests.get(f"{API_URL}/order/user/temp/{user_id}", timeout=5)
            if res_order.status_code == 200 and res_order.json():
                order = res_order.json()
                order_id = order["id"]

                # שלב 2: משיכת הפריטים בתוך ההזמנה הזו
                res_items = requests.get(f"{API_URL}/item-in-order/order/{order_id}", timeout=5)
                if res_items.status_code == 200:
                    items_in_order = res_items.json()
                    for i in items_in_order:
                        st.session_state["cart"].append(i)
                    ##st.session_state["cart"] = items_in_order

        except Exception as e:
            st.error(f"שגיאה בסנכרון העגלה: {e}")

def new_order():
    user = st.session_state.get("user")
    if not user or "user_id" not in user:
        st.error("❌ אין משתמש מחובר")
        return
    user_id = user["user_id"]
    try:
        # 1. הגדרת הכתובת בצורה נקייה
        clean_url = f"{API_URL.strip('/')}/order"

        # 2. יצירת ה-JSON (Payload)
        payload = {
            "buyer_id": int(user_id),
            "order_date": datetime.datetime.now().isoformat(),
            "order_address": user.get("address") or "כתובת לא הוזנה",
            "order_status": "temp"

        }
        # 3. שליחת הבקשה עם Header שמצהיר על JSON
        res = requests.post(
            clean_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if res.status_code in (200, 201):
            order_id = res.json()  # אם ה־API מחזיר את ה-ID
            st.success(f"הזמנה חדשה נוצרה! מספר הזמנה: {order_id}")
            st.session_state["temp_order_id"] = order_id
            st.rerun()
        else:
            st.error(f"❌ שגיאה {res.status_code}")
            with st.expander("ראה פרטים"):
                st.write("URL:", clean_url)
                st.write("Response:", res.text)

    except Exception as e:
        st.error(f"❌ תקלה בתקשורת: {e}")


def finalize_checkout():
    order_id = st.session_state.get("temp_order_id")
    if not order_id:
        st.error("לא נמצאה הזמנה פעילה לסגירה.")
        return

    try:
        res = requests.put(f"{API_URL}/order/close/{order_id}", timeout=5)

        if res.status_code == 200:
            # 1. ניקוי הנתונים
            st.session_state["temp_order_id"] = None
            st.session_state["cart"] = []

            # 2. מעבר לעמוד סיום הזמנה
            st.session_state["page"] = "order_success"
            st.rerun()
        else:
            st.error(f"שגיאה בסגירת ההזמנה: {res.text}")

    except Exception as e:
        st.error(f"תקלה בתקשורת: {e}")


# ---------- DIALOGS (POPUPS) ----------
@st.dialog("⚠️ דרושה התחברות")
def show_login_dialog():
    st.write("כדי להוסיף מוצרים לעגלה ולבצע רכישות, עליך להיות מחובר למערכת.")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("לעמוד התחברות", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
    with col2:
        if st.button("להרשמה מהירה", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()

# ---------- HEADER ----------
def render_header():
    col1, col2, col3 = st.columns([6, 2, 2])
    with col1:
        if st.button("## 🛒 ShoppingSite", help="חזרה לדף הבית"):
            st.session_state["page"] = "home"
            st.rerun()
    with col2:
        if st.session_state["user"]:
            st.write(f"שלום, **{st.session_state['user']['user_name']}** 👋")
        else:
            if st.button("הרשמה", use_container_width=True):
                st.session_state["page"] = "register"
                st.rerun()
    with col3:
        if st.session_state["user"] is None:
            if st.button("התחברות", use_container_width=True, type="primary"):
                st.session_state["page"] = "login"
                st.rerun()
        else:
            if st.button("התנתק", use_container_width=True):
                st.session_state["user"] = None
                st.session_state["cart"] = []
                st.session_state["page"] = "home"
                st.rerun()
    st.divider()


# ---------- PAGES ----------

def show_home_page():
    render_header()

    # אם המשתמש מחובר והעגלה ריקה, ננסה לסנכרן מה-DB (קורה פעם אחת בכניסה)
    if st.session_state["user"] and not st.session_state["cart"]:
        sync_cart_from_db()

    st.markdown("### 🔥 כל המוצרים")

    try:
        response = requests.get(f"{API_URL}/item/", timeout=5)
        response.raise_for_status()
        products = response.json()
    except Exception:
        st.error("❌ לא ניתן לטעון מוצרים מהשרת.")
        return

    # תצוגת מוצרים
    num_cols = 5
    for i in range(0, len(products), num_cols):
        cols = st.columns(num_cols)
        for j, product in enumerate(products[i:i + num_cols]):
            with cols[j]:
                img_url = product.get("image_url") or "https://via.placeholder.com/200"
                st.image(img_url, use_container_width=True)
                st.markdown(f"**{product['item_name']}**")
                st.markdown(f"💰 {product['price']} ₪")

                if st.button("הוסף לעגלה", key=f"add_{product['id']}"):
                    current_user = st.session_state.get("user")
                    if not current_user:
                        show_login_dialog()
                    else:
                        # שלב א': יצירת הזמנה אם היא לא קיימת ב-State
                        if st.session_state.get("temp_order_id") is None:
                            with st.spinner("מכין את העגלה..."):
                                new_order()
                                st.session_state["cart"].append(product)
                                st.toast(f"✅ {product['item_name']} נוסף לעגלה")

                        # שלב ב': הוספת הפריט (רק אם כבר יש ID)
                        if st.session_state.get("temp_order_id"):
                            item_payload = {
                                "order_id": st.session_state["temp_order_id"],
                                "id": product["id"],
                                "amount_in_order": 1
                            }
                            try:
                                res = requests.post(f"{API_URL}/item-in-order/", json=item_payload)
                                if res.status_code == 200:
                                    st.toast(f"✅ {product['item_name']} נוסף!")
                                    sync_cart_from_db()
                                    st.rerun()
                            except Exception as e:
                                st.error("שגיאה בחיבור לשרת")

                        # הוספה ל-Session State
                        st.session_state["cart"].append(product)
                        st.toast(f"✅ {product['item_name']} נוסף לעגלה")
                        st.rerun()
    # סרגל צד לעגלה
    if st.session_state["user"]:
        with st.sidebar:
            st.header("🛒 העגלה שלי")
            if st.session_state["cart"]:
                for item in st.session_state["cart"]:
                    st.write(f"- {item['item_name']} (₪{item['price']})")

                total = sum(item["price"] for item in st.session_state["cart"])
                st.divider()
                st.subheader(f"סה\"כ: {total} ₪")
                if st.button("לתשלום בקופה", use_container_width=True, type="primary"):
                    show_order_success_page()
            else:
                st.info("העגלה שלך ריקה")


def show_register_page():
    render_header()
    st.title("📝 הרשמה לאתר")

    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("שם פרטי")
            user_name = st.text_input("שם משתמש")
            password = st.text_input("סיסמה", type="password")
        with col2:
            last_name = st.text_input("שם משפחה")
            email = st.text_input("אימייל")
            confirm_password = st.text_input("אימות סיסמה", type="password")

        phone = st.text_input("טלפון")
        address = st.text_input("כתובת")

        submitted = st.form_submit_button("צור חשבון")

    if submitted:
        if not all([first_name, last_name, user_name, email, password]):
            st.error("❌ חסרים שדות חובה")
        elif password != confirm_password:
            st.error("❌ הסיסמאות אינן תואמות")
        else:
            payload = {
                "first_name": first_name, "last_name": last_name, "email": email,
                "phone": phone, "address": address, "user_name": user_name, "password": password
            }
            try:
                res = requests.post(f"{API_URL}/user/", json=payload, timeout=5)
                if res.status_code in (200, 201):
                    st.success("נרשמת בהצלחה!")
                    st.session_state["user"] = {"user_name": user_name}
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error(f"שגיאה: {res.text}")
            except:
                st.error("חיבור לשרת נכשל")


def show_login_page():
    render_header()
    st.title("🔐 התחברות")

    with st.form("login_form"):
        u_name = st.text_input("שם משתמש")
        pwd = st.text_input("סיסמה", type="password")
        login_btn = st.form_submit_button("כניסה")

    if login_btn:
        try:
            # 1. הגדרת הכתובת בצורה נקייה
            clean_url = f"{API_URL.strip('/')}/user/auth/login"

            # 2. יצירת ה-JSON (Payload)
            payload = {
                "user_name": u_name,
                "password": pwd
            }

            # 3. שליחת הבקשה עם Header שמצהיר על JSON
            res = requests.post(
                clean_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if res.status_code == 200:
                st.success("✅ התחברת בהצלחה!")
                user_data = res.json()
                st.session_state["user"] = user_data
                st.session_state["page"] = "home"
                st.rerun()
            else:
                # הדפסת הדיבג שתעזור לנו אם זה עדיין נכשל
                st.error(f"❌ שגיאה {res.status_code}")
                with st.expander("ראה פרטים"):
                    st.write("URL:", clean_url)
                    st.write("Response:", res.text)

        except Exception as e:
            st.error(f"❌ תקלה בתקשורת: {e}")


# ---------- ROUTER ----------
if st.session_state["page"] == "home":
    show_home_page()
elif st.session_state["page"] == "register":
    show_register_page()
elif st.session_state["page"] == "login":
    show_login_page()

st.divider()
st.caption("© 2026 ShoppingSite | כל הזכויות שמורות")