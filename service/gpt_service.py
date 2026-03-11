from service import item_service, order_service

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
                f"- Order ID: {str(o.id)}, Status: {str(o.order_status)}, "
                f"Total: {str(o.total_price)}, Item amount: {str(o.item_amount)}, "
                f"Address: {str(o.order_address)}, Date: {str(o.order_date)}\n"
            )
            order_info += line
        except Exception as e:
            print(f"[ERROR] Failed order line: {o} | {e}")

    try:
        full_context = (
            "You are a helpful store assistant. Use ONLY the information below:\n\n"
            f"{product_info}\n{order_info}\n"
            "Rules:\n- If asked about a product not listed, say we don't have it.\n"
            "- If asked about orders, use the user history.\n- Be concise and polite."
        )
    except Exception as e:
        print(f"[ERROR] Failed to build full context: {e}")
        full_context = "No context available due to internal error."

    print("[INFO] Returning context successfully")
    return {"context": full_context}