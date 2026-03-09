from service import item_service, order_service


async def get_assistant_context(user_id):

    products = await item_service.get_all()
    product_info = "PRODUCT CATALOG:\n"
    for p in products:
        status = "In Stock" if p.amount_in_stock > 0 else "Out of Stock"
        product_info += f"- {p.item_name}. Price: {p.price} NIS. Status: {status}\n"

    orders = await order_service.get_all_orders_by_user(user_id)
    order_info = "USER ORDER HISTORY:\n"
    if not orders:
        order_info += "The user hasn't placed any orders yet.\n"
    for o in orders:
        order_info += (f"- Order ID: {o.id}, Date: {o.order_date}, Status: {o.order_status}, Total: {o.total_price} NIS\n"
                       f"Order_address: {o.order_address}, Item_amount: {o.item_amount}")

    # 3. איחוד הכל ל-Context אחד
    full_context = f"""
    You are a store assistant. Use the following data to answer:
    {product_info}
    {order_info}
    Answer only based on this info. If asked about an item not here, say we don't have it.
    """
    return full_context