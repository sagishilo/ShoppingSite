import datetime
import os
import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# ---------- CONFIG ----------
st.set_page_config(page_title="ShoppingSite", page_icon="🛒", layout="wide")

API_URL = "http://localhost:8000"
# ---------- HEADER ----------
def render_header():
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
    with col1:
        if st.button("## 🛒 ShoppingSite", help="חזרה לדף הבית"):
            st.session_state["page"] = "home"
            st.rerun()
    with col2:
        if st.session_state["user"]:
            st.write(f"שלום, **{st.session_state['user']['first_name']}** 👋")
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


    with col5:
        if st.session_state["user"] is not None:
            if st.button("AI Assistant", use_container_width=True):
                st.session_state["page"] = "chat"
                st.rerun()
    st.divider()

#---------------------------PAGES----------------------------------

def show_ai_assistant_page():
    # הגדרת מפתח ה-API
    os.environ["OPENAI_API_KEY"] = "---------------------------your_key_here-------------------"
    client = OpenAI()
    st.title("Store Assistant 🤖")
    user_id=st.session_state["user"]["id"]
    content = requests.get(f"{API_URL}/gpt/content/{user_id}", timeout=5)

    if "messages_buffer" not in st.session_state:
        st.session_state.messages_buffer = [
            {"role": "system",
             "content": content}
        ]
    if "chat_counter" not in st.session_state:
        st.session_state.chat_counter = 0

    for msg in st.session_state.messages_buffer:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.chat_counter >= 5:
        st.error("Reached the limit of 5 prompts per session.")
        return

    if user_input := st.chat_input("Ask me about our products..."):

        st.session_state.messages_buffer.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            with st.spinner("Assistant is typing..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages_buffer,
                    temperature=0.9,
                    max_tokens=300
                )
                answer = response.choices[0].message.content

            st.session_state.messages_buffer.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.chat_counter += 1

            if st.session_state.chat_counter >= 5:
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")





def show_user_dashboard():
    render_header()
    if not st.session_state.get("user"):
        st.warning("❌ עליך להתחבר כדי לראות את האזור האישי")
        return

    user_id = st.session_state["user"]["id"]
    colss = st.columns([1, 1, 2, 1, 1])
    with colss[2]:
        st.title("אזור אישי 👤",  )

    st.divider()
    # --------------------- הזמנות סגורות ---------------------
    st.subheader("הזמנות סגורות 📦")

    try:
        res_orders = requests.get(f"{API_URL}/order/user/closed/{user_id}", timeout=5)
        if res_orders.status_code == 200:
            orders = res_orders.json()
            if not orders:
                st.info("לא נמצאו הזמנות סגורות")
            else:
                for i in range(0, len(orders), 5):
                    cols = st.columns(5)
                    chunk = orders[i: i + 5]

                    for idx, o in enumerate(chunk):
                        with cols[idx]:
                            with st.container(border=True):
                                o_id = o.get('order_id')
                                raw_date = o.get("order_date", "")
                                order_date = datetime.datetime.fromisoformat(raw_date).strftime(
                                    "%d/%m") if raw_date else "N/A"

                                st.markdown(f"**# {o_id}**")
                                st.caption(f"📅 {order_date} | ₪{o.get('total_price', 0)}")

                                # כפתור "פרטים" קטן שפותח פופ-אפ (Modal) כדי לא להרוס את הגריד
                                if st.button("פרטים", key=f"btn_{o_id}"):
                                    @st.dialog(f"פירוט הזמנה {o_id}")
                                    def show_order_details(order_info):
                                        st.write(f"📍 **כתובת משלוח:** {order_info.get('order_address', 'לא צוינה')}")
                                        st.write(f"💰 **סכום סופי:** ₪{order_info.get('total_price', 0)}")
                                        st.write(f"🔢 **כמות פריטים:** {order_info.get('total_items', 0)}")
                                        st.divider()

                                        # קריאה למוצרים
                                        items_res = requests.get(f"{API_URL}/item-in-order/order/{o_id}", timeout=5)
                                        if items_res.status_code == 200:
                                            items_data = items_res.json()
                                            for item_entry in items_data:
                                                if isinstance(item_entry, dict):
                                                    name = item_entry.get('item', {}).get('item_name', 'מוצר')
                                                    qty = item_entry.get('amount_in_order', 0)
                                                    st.write(f"📦 {name}       \n כמות:  {qty}")
                                                else:
                                                    st.error("פורמט נתונים לא תקין")
                                        else:
                                            st.error("לא הצלחנו לטעון את המוצרים")

                                    show_order_details(o)
        else:
            st.toast(f"שגיאה בטעינת ההזמנות: {res_orders.text}")
    except Exception as e:
        st.error(f"שגיאה בתקשורת: {e}")


    st.subheader("המועדפים שלי❤️")

    # ---- callback למועדפים ----
    def toggle_fav_callback(item_id, user_id):
        favorites = st.session_state.get("favorites", [])
        is_fav = item_id in favorites
        success = toggle_favorite(user_id, item_id, is_fav)
        if success:
            if is_fav:
                st.session_state["favorites"] = [f for f in favorites if f != item_id]
            else:
                st.session_state["favorites"] = favorites + [item_id]

    # ---- מוצרים מועדפים ----
    try:
        res_fav = requests.get(f"{API_URL}/fav-item/{user_id}", timeout=5)
        if res_fav.status_code == 200:
            fav_items = res_fav.json()
            if not fav_items:
                st.info("לא קיימים מוצרים מועדפים")
            else:
                # הכנת DataFrame
                data = []
                for item in fav_items:
                    p_id = int(item.get("id", 0))
                    is_fav = p_id in st.session_state.get("favorites", [])
                    data.append({
                        "שם מוצר": item.get("item_name", "Unknown"),
                        "מחיר (₪)": item.get("price", 0),
                        "מלאי": item.get("amount_in_stock", 0),
                        "מועדף": is_fav,
                        "תמונה": item.get("image_url") or "https://katzr.net/a0cf43",
                        "item_id": p_id
                    })
                df = pd.DataFrame(data)

                # הצגת DataFrame
                for index, row in df.iterrows():
                    cols = st.columns([2,1,1,1,1])
                    with cols[0]:
                        st.image(row["תמונה"], width=60)
                        st.markdown(f"**{row['שם מוצר']}**")
                    with cols[1]:
                        st.markdown(f"💰 {row['מחיר (₪)']}")
                    with cols[2]:
                        st.markdown(f" left in stock {row['מלאי']}")
                    with cols[3]:
                        # Checkbox למעקב מועדפים
                        st.checkbox(
                            "",
                            value=row["מועדף"],
                            key=f"fav_chk_{row['item_id']}",
                            on_change=toggle_fav_callback,
                            args=(row['item_id'], user_id)
                        )

        else:
            st.toast(f"שגיאה בטעינת המוצרים המועדפים: {res_fav.text}")
    except Exception as e:
        st.toast(f"שגיאה בתקשורת: {e}")

    ##----------------מחיקת משתמש-------------------
    st.divider()
    st.subheader("⚙️ ניהול חשבון")

    with st.expander("🔴 אזור מסוכן: מחיקת חשבון לצמיתות"):
        st.warning("""
                שים לב: מחיקת החשבון היא פעולה בלתי הפיכה. 
                כל המידע שלך יימחק לצמיתות מהמערכת, כולל:
                * היסטוריית הזמנות
                * רשימת מוצרים מועדפים
                * פרטי התקשרות וכתובות
            """)

        # תיבת אישור חובה להפעלת הכפתור
        confirm_deletion = st.checkbox(
            "אני מאשר שאני מעוניין למחוק את החשבון שלי וכל המידע הקשור אליו",
            key="delete_confirm_check"
        )

        # הכפתור פעיל רק אם הצ'קבוקס מסומן
        if st.button("מחק את החשבון שלי לצמיתות", type="primary", disabled=not confirm_deletion):
            try:
                res_delete = requests.delete(f"{API_URL}/user/{user_id}", timeout=10)

                if res_delete.status_code == 200:
                    st.success("החשבון נמחק בהצלחה. להתראות!")
                    # ניקוי ה-Session State כדי לנתק את המשתמש
                    st.session_state.clear()

                    # השהייה קלה כדי שהמשתמש יראה את הודעת ההצלחה
                    import time
                    time.sleep(1)

                    # העברה לדף הבית וריענון
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error(f"המחיקה נכשלה: {res_delete.text}")
            except Exception as e:
                st.error(f"שגיאה בתקשורת עם השרת: {e}")



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


def update_cart_item(iio_id, idx, new_amount):
    if new_amount < 1:
        return

    response = requests.put(f"{API_URL}/item-in-order/{iio_id}", json={"amount_in_order": new_amount})
    if response.status_code == 200:
        st.session_state["cart"][idx]["amount_in_order"] = new_amount
        st.rerun()

def delete_cart_item(iio_id, idx):
    response = requests.delete(f"{API_URL}/item-in-order/{iio_id}")
    if response.status_code == 200:
        st.session_state["cart"].pop(idx)
        st.rerun()

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
            st.toast(f"שגיאת ולידציה (422): {res.json()}")  # זה ידפיס לך בדיוק מה חסר ב-JSON
            return False

        return res.status_code in (200, 201)
    except Exception as e:
        st.toast(f"שגיאה בתקשורת: {e}")
        return False



def load_temp_cart():
    try:
        user_id = st.session_state["user"]["id"]
        res_order = requests.get(f"{API_URL}/order/user/temp/{user_id}", timeout=5)
        if res_order.status_code == 200 and res_order.json():
            order = res_order.json()
            st.session_state["temp_order_id"] = order["id"]
            # עכשיו נטען את פרטי העגלה
            res_items = requests.get(f"{API_URL}/item-in-order/order/{order['id']}", timeout=5)
            if res_items.status_code == 200:
                st.session_state["cart"] = res_items.json()
            else:
                st.session_state["cart"] = []
        else:
            st.session_state["temp_order_id"] = None
            st.session_state["cart"] = []
    except:
        st.session_state["temp_order_id"] = None
        st.session_state["cart"] = []


def add_to_cart(product):
    if not st.session_state.get("user"):
        show_login_dialog()
        return
    order_id = st.session_state.get("temp_order_id") or new_order()
    if not order_id:
        return
    payload = {
        "order_id": int(order_id),
        "item_id": int(product["id"]),
        "amount_in_order": 1
    }
    res = requests.post(f"{API_URL}/item-in-order/", json=payload)
    if res.status_code in (200, 201):
        sync_cart_from_db()
        st.toast(f"✅ {product['item_name']} נוסף לעגלה!")
        st.rerun()
    else:
        st.toast(f"❌ שגיאה: {res.text}")




def increase_cart_amount(product, in_cart, max_stock):
    new_amount = in_cart["amount_in_order"] + 1

    if new_amount > max_stock:
        st.toast("❌ אין מספיק מלאי")
        return

    res = requests.put(
        f"{API_URL}/item-in-order/{in_cart['id']}",
        params={"new_amount_in_order": new_amount}
    )

    if res.status_code == 200:
        # עדכון ישיר של session_state
        cart = st.session_state.get("cart", [])
        for idx, item in enumerate(cart):
            if item["id"] == in_cart["id"]:
                st.session_state["cart"][idx]["amount_in_order"] = new_amount
                # עדכון מפתחות temp ו-orig
                temp_key = f"temp_{in_cart['id']}"
                orig_key = f"orig_{in_cart['id']}"
                st.session_state[temp_key] = new_amount
                st.session_state[orig_key] = new_amount
                break

        st.toast(f"✅ כמות {product['item_name']} עודכנה ל-{new_amount}")
        st.rerun()
    else:
        st.toast(f"❌ שגיאה: {res.text}")


def update_ui_cart(iio):
    iio_id = iio.get("id")
    new_amount = iio.get("amount_in_order", 1)
    orig_key = f"orig_{iio_id}"
    temp_key = f"temp_{iio_id}"

    st.session_state[temp_key] = new_amount
    st.session_state[orig_key] = new_amount


def filter_products_advanced(products, name_query="", stock_op="", stock_val="", price_op="", price_val=""):
    filtered = []

    # המרת ערכים למספרים אם אפשר
    try:
        stock_val_num = int(stock_val) if stock_val else None
    except:
        stock_val_num = None

    try:
        price_val_num = float(price_val) if price_val else None
    except:
        price_val_num = None

    # פיצול מילים לחיפוש בשם
    name_words = name_query.lower().split() if name_query else []

    for p in products:
        # חיפוש בשם
        name_ok = all(word in p["item_name"].lower() for word in name_words)

        # חיפוש במלאי
        stock_ok = True
        if stock_op and stock_val_num is not None:
            if stock_op == "מעל":
                stock_ok = p.get("amount_in_stock",0) > stock_val_num
            elif stock_op == "מתחת":
                stock_ok = p.get("amount_in_stock",0) < stock_val_num
            elif stock_op == "כמות מדוייקת":
                stock_ok = p.get("amount_in_stock",0) == stock_val_num

        # חיפוש במחיר
        price_ok = True
        if price_op and price_val_num is not None:
            if price_op == "מעל":
                price_ok = p.get("price",0) > price_val_num
            elif price_op == "מתחת":
                price_ok = p.get("price",0) < price_val_num
            elif price_op == "מחיר מדוייק":
                price_ok = p.get("price",0) == price_val_num

        if name_ok and stock_ok and price_ok:
            filtered.append(p)

    return filtered



# פונקציית עזר לטעינת עגלה מהשרת (סטטוס TEMP)
def sync_cart_from_db():

    order_id = st.session_state.get("temp_order_id")

    if not order_id:
        st.session_state["cart"] = []
        return
    try:
        res_items = requests.get(
            f"{API_URL}/item-in-order/order/{order_id}",
            timeout=5
        )
        if res_items.status_code == 200:
            st.session_state["cart"] = res_items.json()
        else:
            st.session_state["cart"] = []

    except Exception as e:
        st.toast(f"שגיאה בסנכרון העגלה: {e}")





def new_order():
    user = st.session_state.get("user")
    if not user or "id" not in user:
        st.toast("❌ אין משתמש מחובר")
        return
    user_id = user["id"]
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
            ##st.success(f"הזמנה חדשה נוצרה! מספר הזמנה: {order_id}")
            st.session_state["temp_order_id"] = order_id
            return order_id
        else:
            st.toast(f"❌ שגיאה {res.status_code}")
            with st.expander("ראה פרטים"):
                st.write("URL:", clean_url)
                st.write("Response:", res.text)

    except Exception as e:
        st.toast(f"❌ תקלה בתקשורת: {e}")


def finalize_checkout():
    order_id = st.session_state.get("temp_order_id")
    if not order_id:
        st.toast("לא נמצאה הזמנה פעילה לסגירה.")
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
            st.toast(f"שגיאה בסגירת ההזמנה: {res.text}")

    except Exception as e:
        st.toast(f"תקלה בתקשורת: {e}")


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
        user_id = int(st.session_state["user"]["id"])
        st.session_state["favorites"] = get_user_favorites(user_id)
        st.session_state["favorites_loaded"] = True


    # ---------- סנכרון עגלה ----------
    if "cart_loaded" not in st.session_state and st.session_state["user"]:
        sync_cart_from_db()
        st.session_state["cart_loaded"] = True

        # ---------- סנכרון שורות חיפוש ----------
    search_keys = ["search_name_input", "stock_val", "price_val", "stock_op", "price_op"]

    # 1. הגדרת המפתחות
    search_keys = ["search_name_input", "stock_op", "stock_val", "price_op", "price_val"]

    # 2. פונקציית ה-Callback לניקוי (תרוץ לפני רינדור הווידג'טים)
    def reset_filters():
        for key in search_keys:
            st.session_state[key] = ""

    with st.form("filter_form"):
        search_center, col_stock, col_stock_val, col_price, col_price_val = st.columns([2, 1, 1, 1, 1])
        with search_center:
            # שימוש ב-key מבטיח ש-product_name_query תמיד יסונכרן עם ה-session_state
            product_name_query = st.text_input("שם מוצר", placeholder="חיפוש...", key="search_name_input")

        with col_stock:
            stock_op = st.selectbox("מלאי", ["", "מתחת", "מעל", "כמות מדוייקת"], key="stock_op")

        with col_stock_val:
            stock_val = st.text_input("כמות", key="stock_val")

        with col_price:
            price_op = st.selectbox("מחיר", ["", "מתחת", "מעל", "מחיר מדוייק"], key="price_op")

        with col_price_val:
            price_val = st.text_input("ערך", key="price_val")

        col_submit, col_reset = st.columns([1, 1])
        with col_submit:
            submitted = st.form_submit_button("🔍 חפש", use_container_width=True)
        with col_reset:
            # בתוך טופס, כפתור ניקוי רגיל עדיין יעבוד עם ה-callback
            st.form_submit_button("🗑️ נקה", on_click=reset_filters, use_container_width=True)

    # --- טעינה וסינון ---
    try:
        response = requests.get(f"{API_URL}/item/", timeout=5)
        response.raise_for_status()
        all_products = response.json()
    except Exception:
        st.error("❌ שגיאה בתקשורת עם השרת")
        return

    # סינון התוצאות
    products = filter_products_advanced(
        all_products,
        name_query=product_name_query,
        stock_op=stock_op,
        stock_val=stock_val,
        price_op=price_op,
        price_val=price_val
    )

    # הצגת התוצאות
    if not products and (product_name_query or stock_val or price_val):
        st.toast("לא נמצאו מוצרים, מציג את כל הרשימה")
        products = all_products


    # ---------- גריד מוצרים ----------
    num_cols = 5
    for i in range(0, len(products), num_cols):
        cols = st.columns(num_cols, gap="medium")
        for j, product in enumerate(products[i:i+num_cols]):
            with cols[j]:
                # תמונת מוצר
                img_url = product.get("image_url") or "https://katzr.net/a0cf43"
                st.image(img_url, use_container_width=True)

                # שם, מחיר וכמות במלאי
                st.markdown(f"**{product['item_name']}**")
                st.markdown(f"💰 {product['price']} ₪")
                st.markdown(f" {product['amount_in_stock']} left in stock")

                # כפתורי פעולה
                col_btn, col_fav = st.columns([3,1])

                with col_btn:
                    cart = st.session_state.get("cart", [])
                    # בדיקה אם המוצר כבר בעגלה
                    in_cart = next((iio for iio in cart if iio["item"]["id"] == product["id"]), None)
                    max_stock = product["amount_in_stock"]
                    if max_stock == 0:
                        st.write("❌ אזל מהמלאי")
                        #continue

                    if in_cart:
                        current_amount = in_cart["amount_in_order"]
                        if current_amount >= max_stock:
                            st.write(f"✅ {product['item_name']} כבר בעגלה - מלאי: {max_stock}")
                        else:
                            if st.button("הוסף לעגלה", key=f"add_{product['id']}", use_container_width=True):
                                increase_cart_amount(product, in_cart, max_stock)
                                st.rerun()

                    else:
                        if max_stock > 0:
                            if st.button("הוסף לעגלה", key=f"add_{product['id']}", use_container_width=True):
                                if not st.session_state.get("user"):
                                    show_login_dialog()
                                else:
                                    add_to_cart(product)
                                    st.rerun()


                with col_fav:
                    if st.session_state["user"]:
                        u_id = int(st.session_state["user"]["id"])
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

    # ---------- עגלה Sidebar ----------
    if st.session_state.get("user"):
        load_temp_cart()
        with st.sidebar:
            st.header("🛒 העגלה שלי")
            cart = st.session_state.get("cart", [])

            if not cart:
                st.info("העגלה שלך ריקה")
            else:
                total_sum = 0

                for idx, iio in enumerate(cart):
                    iio_id = iio.get("id")
                    item = iio.get("item", {})
                    name = item.get("item_name", "מוצר ללא שם")
                    price = item.get("price", 0)
                    amount = iio.get("amount_in_order", 1)
                    in_stock = item.get("amount_in_stock", 0)

                    # מפתחות ל-session_state
                    orig_key = f"orig_{iio_id}"
                    temp_key = f"temp_{iio_id}"
                    if orig_key not in st.session_state:
                        st.session_state[orig_key] = amount
                    if temp_key not in st.session_state:
                        st.session_state[temp_key] = amount

                    with st.container(border=True):
                        # שם מוצר ומחיקה
                        col_name, col_del = st.columns([4, 1])
                        col_name.markdown(f"**{name}**")
                        if col_del.button("🗑️", key=f"rm_{iio_id}"):
                            # מחיקה מהDB ומ-session_state
                            response = requests.delete(f"{API_URL}/item-in-order/{iio_id}")
                            if response.status_code == 200:
                                st.session_state["cart"].pop(idx)
                                st.session_state.pop(orig_key, None)
                                st.session_state.pop(temp_key, None)
                                st.rerun()
                            else:
                                st.toast(f"❌ שגיאה במחיקת מוצר: {response.text}")

                        # שליטה בכמות
                        col_minus, col_num, col_plus = st.columns([1, 2, 1])
                        with col_minus:
                            if st.session_state[temp_key] > 1:
                                if st.button("−", key=f"dec_{iio_id}"):
                                    st.session_state[temp_key] -= 1
                                    st.rerun()
                        with col_num:
                            st.markdown(
                                f"<p style='text-align:center; font-size:1.2em;'>{st.session_state[temp_key]}</p>",
                                unsafe_allow_html=True)
                        with col_plus:
                            if st.session_state[temp_key] < in_stock:
                                if st.button("+", key=f"inc_{iio_id}"):
                                    st.session_state[temp_key] += 1
                                    st.rerun()

                        # כפתור עדכון כמות (מופיע רק אם שונה מהמקורי)
                        if st.session_state[temp_key] != st.session_state[orig_key]:
                            if st.button("עדכן כמות", key=f"update_{iio_id}", use_container_width=True, type="primary"):
                                new_amount = st.session_state[temp_key]
                                response = requests.put(
                                    f"{API_URL}/item-in-order/{iio_id}",
                                    params={"new_amount_in_order": new_amount}
                                )
                                if response.status_code == 200:
                                    st.session_state[orig_key] = new_amount
                                    st.session_state["cart"][idx]["amount_in_order"] = new_amount
                                    st.toast(f"✅ כמות של {name} עודכנה ל-{new_amount}")
                                    st.rerun()
                                else:
                                    st.toast(f"❌ שגיאה בעדכון הכמות: {response.text}")

                        # מחיר סופי לפריט
                        item_total = price * st.session_state[temp_key]
                        total_sum += item_total
                        st.caption(f"מחיר יחידה: ₪{price} | סה\"כ: **₪{item_total}**")

                st.divider()
                st.write(f"📍 **כתובת משלוח:** {st.session_state.get('user', {}).get('address', 'לא צוינה')}")
                if st.button("🚀 לתשלום וסגירת הזמנה", use_container_width=True, type="primary"):
                    finalize_checkout()

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
            st.toast("❌ חסרים שדות חובה")
        elif password != confirm_password:
            st.toast("❌ הסיסמאות אינן תואמות")
        else:
            payload = {
                "first_name": first_name, "last_name": last_name, "email": email,
                "phone": phone, "address": address, "user_name": user_name, "password": password
            }
            success = False
            try:
                res = requests.post(f"{API_URL}/user/", json=payload, timeout=10)

                if res.status_code in (200, 201):
                    st.session_state["user"] = res.json()
                    st.session_state["page"] = "home"
                    st.session_state.pop("favorites_loaded", None)
                    success = True
                else:
                    # חילוץ הודעת השגיאה מה-JSON של השרת
                    try:
                        error_data = res.json()
                        # FastAPI שם את השגיאה בדרך כלל תחת המפתח 'detail'
                        error_msg = error_data.get("detail", str(error_data))
                    except:
                        error_msg = res.text

                    if "username is already existing" in error_msg.lower() or "taken" in error_msg.lower():
                        st.error("⚠️ שם המשתמש כבר תפוס, בחר שם אחר.")
                    elif "validation error" in error_msg.lower():
                        # זה המקרה של ה-ID החסר שראינו קודם
                        st.warning("המשתמש נוצר אך חלה שגיאה בטעינת הנתונים. נסה להתחבר.")
                        st.info(f"פרטים טכניים: {error_msg}")
                    else:
                        st.error(f"שגיאה מהשרת: {error_msg}")

            except Exception as e:
                st.error(f"❌ חיבור לשרת נכשל: {e}")

            if success:
                st.success("✅ נרשמת בהצלחה!")
                import time
                time.sleep(0.5)
                st.rerun()


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
                st.toast(f"❌ שגיאה {res.status_code}")
                with st.expander("ראה פרטים"):
                    st.write("URL:", clean_url)
                    st.write("Response:", res.text)

        except Exception as e:
            st.toast(f"❌ תקלה בתקשורת: {e}")








# ---------- ROUTER ----------
if st.session_state["page"] == "home":
    show_home_page()
elif st.session_state["page"] == "register":
    show_register_page()
elif st.session_state["page"] == "login":
    show_login_page()
elif st.session_state["page"]== "chat":
    show_ai_assistant_page()

st.divider()
st.caption("© 2026 ShoppingSite | כל הזכויות שמורות")