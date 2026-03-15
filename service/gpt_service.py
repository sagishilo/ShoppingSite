from service import item_service, order_service, favorite_item_service




## Receives a user id
## Fetches all products and the user's order history, formats them into a readable context
## Returns a dictionary containing the assistant context as a string

async def get_assistant_context(user_id: int):



    try:
        products = await item_service.get_all() or []
    except Exception as e:
        print(f"[ERROR] Failed to fetch products: {e}")
        products = []

    product_info = "PRODUCT CATALOG:\n"
    for p in products:
        try:
            status = "In Stock" if p.amount_in_stock > 0 else "Out of Stock"
            line = f"- {str(p.item_name)}, Price: {str(p.price)}, Status: {status}\n"
            product_info += line
        except Exception as e:
            print(f"[ERROR] Failed product line: {p} | {e}")



    try:
        fav = await favorite_item_service.get_all_by_user_id(user_id) or []
        stats= await favorite_item_service.get_items_popularity_stats() or []
    except Exception as e:
        print(f"[ERROR] Failed to fetch favorites: {e}")
        fav = []
        stats=[]

    favorite_info = "FAVORITES ITEMS:\n"
    for f in fav:
        try:
            name=f"Favorite item name: {f.item_name} \n"
            favorite_info += name
        except Exception as e:
            print(f"[ERROR] Failed favorite line: {f} | {e}")

    for s in stats:
        try:
            name=f"Favorite item name: {s['name']} \n"
            fav_count=f"{s['favorites_count']} voted it as favorite \n"
            line=f"{name}  {fav_count}"
            favorite_info += line
        except Exception as e:
            print(f"[ERROR] Failed favorite line: {s} | {e}")



    try:
        orders = await order_service.get_all_orders_by_user(user_id) or []
    except Exception as e:
        print(f"[ERROR] Failed to fetch orders: {e}")
        orders = []

    order_info = "USER ORDER HISTORY:\n"
    if not orders:
        order_info += "The user hasn't placed any orders yet.\n"

    for o in orders:
        try:
            line = (
                f"- Order ID: {o.id}, Status: {o.order_status}, "
                f"Total: {o.total_price}, Item amount: {o.item_amount}, "
                f"Address: {o.order_address}, Date: {o.order_date}\n"
            )
            for iio in o.order_items or []:
                iio_str=f"Item name: {iio.item.item_name}, Amount in order: {iio.amount_in_order}\n"
                line+=iio_str
            order_info += line
        except Exception as e:
            print(f"[ERROR] Failed order line: {o} | {e}")




    try:
        full_context = (
            "You are an expert shopping assistant. Your goal is to help users by providing technical data, "
            "general knowledge, and helpful suggestions regarding products in the catalog."
            " Use the information below:\n\n"
            f"{product_info}\n"
            f"{order_info}\n"
            f"{favorite_info}\n"
            "Rules:\n- "
            "If asked about a product not listed, say we don't have it.\n"
            "If asked about orders, use the user history.\n"
            "If asked: provide average calorie counts, nutritional values, and dietary compatibility.\n"
            "If asked: suggest recipes, serving ideas, or practical use cases.\n"
            "Temp order is an open order.\n"
            "Be concise and polite."
        )
    except Exception as e:
        print(f"[ERROR] Failed to build full context: {e}")
        full_context = "No context available due to internal error."

    return {"context": full_context}