import datetime
import streamlit as st
import requests

# ---------- CONFIG ----------
st.set_page_config(page_title="ShoppingSite", page_icon="🛒", layout="wide")

API_URL = "http://localhost:8000"
# ---------- HEADER ----------
def render_header():
    col1, col2, col3, col4 = st.columns([5, 2, 2, 2])
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
    with col4:
        if st.session_state.get("user") and st.session_state["page"] != "dashboard" :
            if st.button("👤 אזור אישי", use_container_width=True):
                st.session_state["page"] = "dashboard"
                st.rerun()

    st.divider()

#---------------------------PAGES----------------------------------

def show_user_dashboard():
    render_header()
    if not st.session_state.get("user"):
        st.warning("❌ עליך להתחבר כדי לראות את האזור האישי")
        return

    user_id = st.session_state["user"]["user_id"]
    st.title("👤 אזור אישי")

    st.divider()
    st.subheader("📦 הזמנות סגורות")

    # ---- הזמנות סגורות ----
    try:
        res_orders = requests.get(f"{API_URL}/order/user/closed/{user_id}", timeout=5)
        if res_orders.status_code == 200:
            orders = res_orders.json()
            if not orders:
                st.info("לא נמצאו הזמנות סגורות")
            else:
                for o in orders:
                    order_date = datetime.datetime.fromisoformat(o["order_date"]).strftime("%d/%m/%Y %H:%M")
                    st.write(f"**הזמנה #{o['order_id']}**")
                    st.caption(f"תאריך: {order_date} | סה\"כ מוצרים: {o['total_items']} | סכום כולל: ₪{o['total_price']}")
                    st.divider()
        else:
            st.error(f"שגיאה בטעינת ההזמנות: {res_orders.text}")
    except Exception as e:
        st.error(f"שגיאה בתקשורת: {e}")

    st.divider()
    st.subheader("❤️ המועדפים שלי")

    # ---- מוצרים מועדפים ----
    try:
        res_fav = requests.get(f"{API_URL}/fav-item/{user_id}", timeout=5)
        if res_fav.status_code == 200:
            fav_items = res_fav.json()
            if not fav_items:
                st.info("לא קיימים מוצרים מועדפים")
            else:
                num_cols = 4
                for i in range(0, len(fav_items), num_cols):
                    cols = st.columns(num_cols, gap="medium")
                    for j, item in enumerate(fav_items[i:i+num_cols]):
                        with cols[j]:
                            img_url = item.get("image_url") or "https://katzr.net/a0cf43"
                            st.image(img_url, use_container_width=True)
                            st.markdown(f"**{item['item_name']}**")
                            st.markdown(f"💰 {item['price']} ₪")
        else:
            st.error(f"שגיאה בטעינת המוצרים המועדפים: {res_fav.text}")
    except Exception as e:
        st.error(f"שגיאה בתקשורת: {e}")



def show_order_success_page():
    render_header()
    st.balloons()
    st.container()
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
            st.session_state["favorites"] = []
            st.session_state.pop("favorites_loaded", None)

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
if st.session_state["page"] == "order_success":
    show_order_success_page()
if st.session_state["page"] == "dashboard":
    show_user_dashboard()

# ---------- API ----------
def get_user_favorites(user_id):
    try:
        res = requests.get(f"{API_URL}/fav-item/{int(user_id)}", timeout=5)
        if res.status_code == 200:
            data = res.json()
            # מחלצים רק את ה-ID והופכים אותו למספר שלם
            return [int(item["id"]) for item in data]
    except Exception as e:
        print(f"Error fetching favorites: {e}")
    return []


def toggle_favorite(user_id, item_id, is_favorite):
    # נתיב בסיסי
    base_url = f"{API_URL.strip('/')}/fav-item"

    # הכנת ה-Payload - וודא שהשמות תואמים ל-FastAPI
    payload = {
        "user_id": int(user_id),
        "item_id": int(item_id)
    }

    try:
        if is_favorite:
            res = requests.delete(f"{base_url}/remove/fav", json=payload, timeout=5)
        else:
            res = requests.post(f"{base_url}/", json=payload, timeout=5)

        if res.status_code == 422:
            st.error(f"שגיאת ולידציה (422): {res.json()}")  # זה ידפיס לך בדיוק מה חסר ב-JSON
            return False

        return res.status_code in (200, 201)
    except Exception as e:
        st.error(f"שגיאה בתקשורת: {e}")
        return False



# פונקציית עזר לטעינת עגלה מהשרת (סטטוס TEMP)
def sync_cart_from_db():
    user = st.session_state.get("user")
    if user and "user_id" in user:
        user_id = user["user_id"]
        try:
            res_order = requests.get(f"{API_URL}/order/user/temp/{user_id}", timeout=5)
            if res_order.status_code == 200 and res_order.json():
                order = res_order.json()
                order_id = order["id"]
                st.session_state["temp_order_id"] = order_id

                res_items = requests.get(f"{API_URL}/item-in-order/order/{order_id}", timeout=5)

                if res_items.status_code == 200:
                    data = res_items.json()
                    st.session_state["cart"] = data
                else:
                    st.session_state["cart"] = []

                #if "favorites" not in st.session_state:
                #    st.session_state["favorites"] = []

                #if st.session_state["user"]:
                #    st.session_state["favorites"] = get_user_favorites(st.session_state["user"]["user_id"])

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
        clean_url = f"{API_URL.strip('/')}/order/"

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
            return order_id
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



# ---------- PAGES ----------

def clear_search():
    st.session_state["search_input_val"] = ""


def show_home_page():
    render_header()

    # ---------- אתחול session_state ----------
    if "search_input_val" not in st.session_state:
        st.session_state["search_input_val"] = ""
    if "favorites" not in st.session_state:
        st.session_state["favorites"] = []
    if "favorites_loaded" not in st.session_state and st.session_state["user"]:
        user_id = int(st.session_state["user"]["user_id"])
        st.session_state["favorites"] = get_user_favorites(user_id)
        st.session_state["favorites_loaded"] = True

    # ---------- סנכרון עגלה ----------
    if st.session_state["user"] and not st.session_state.get("cart"):
        sync_cart_from_db()  # לא נוגע במועדפים יותר

    # ---------- שורת חיפוש ----------
    _, search_center, _ = st.columns([1,2,1])
    with search_center:
        search_query = st.text_input(
            "חפש מוצר",
            placeholder="🔍 מה תרצה לקנות היום?",
            label_visibility="collapsed",
            value=st.session_state["search_input_val"],
            key="home_search_input"
        )
        st.session_state["search_input_val"] = search_query

    st.markdown("### 🔥 כל המוצרים")

    # ---------- טעינת מוצרים ----------
    try:
        response = requests.get(f"{API_URL}/item/", timeout=5)
        all_products = response.json()
    except Exception:
        st.error("❌ לא ניתן לטעון מוצרים מהשרת.")
        return

    # סינון לפי חיפוש
    products = [p for p in all_products if search_query.lower() in p['item_name'].lower()] \
        if search_query else all_products

    if not products:
        st.info(f"לא נמצאו מוצרים עבור: **{search_query}**")
        return

    # ---------- גריד מוצרים ----------
    num_cols = 5
    for i in range(0, len(products), num_cols):
        cols = st.columns(num_cols, gap="medium")
        for j, product in enumerate(products[i:i+num_cols]):
            with cols[j]:
                # תמונת מוצר
                img_url = product.get("image_url") or "https://katzr.net/a0cf43"
                st.image(img_url, use_container_width=True)

                # שם ומחיר
                st.markdown(f"**{product['item_name']}**")
                st.markdown(f"💰 {product['price']} ₪")

                # כפתורי פעולה
                col_btn, col_fav = st.columns([3,1])

                with col_btn:
                    if st.button("הוסף לעגלה", key=f"add_{product['id']}", use_container_width=True):
                        if not st.session_state.get("user"):
                            show_login_dialog()
                        else:
                            order_id = st.session_state.get("temp_order_id") or new_order()
                            if order_id:
                                item_payload = {
                                    "order_id": int(order_id),
                                    "item_id": int(product["id"]),
                                    "amount_in_order": 1
                                }
                                res = requests.post(f"{API_URL}/item-in-order/", json=item_payload)
                                if res.status_code in (200,201):
                                    st.toast(f"✅ {product['item_name']} נוסף לעגלה!")
                                    sync_cart_from_db()

                with col_fav:
                    if st.session_state["user"]:
                        u_id = int(st.session_state["user"]["user_id"])
                        p_id = int(product["id"])
                        favorites = st.session_state.get("favorites", [])
                        is_fav = p_id in favorites

                        # Checkbox עם וי למועדפים
                        checked = st.checkbox("", value=is_fav, key=f"fav_chk_{p_id}")
                        if checked != is_fav:
                            success = toggle_favorite(u_id, p_id, is_fav)
                            if success:
                                if is_fav:
                                    st.session_state["favorites"] = [f for f in favorites if f != p_id]
                                else:
                                    st.session_state["favorites"] = favorites + [p_id]

    # ---------- סרגל צד (עגלה) ----------
    if st.session_state["user"]:
        with st.sidebar:
            st.header("🛒 העגלה שלי")
            if st.session_state.get("cart"):
                total = 0
                for iio in st.session_state["cart"]:
                    item = iio.get("item")
                    if item:
                        name = item.get("item_name")
                        price = item.get("price")
                        amount = iio.get("amount_in_order", 1)

                        st.write(f"**{name}**")
                        st.caption(f"{amount} יחידות - ₪{price * amount}")
                        total += (price * amount)

                st.divider()
                st.subheader(f"סה\"כ: {total} ₪")
                if st.button("לתשלום וסגירת הזמנה", use_container_width=True, type="primary"):
                    finalize_checkout()
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
                    user_data = res.json()
                    st.session_state["user"] = user_data
                    st.session_state.pop("favorites_loaded", None)
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