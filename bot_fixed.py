import telebot
import json
import os
import time
from datetime import datetime
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

# ==================== НАСТРОЙКИ ====================
TOKEN = "8013266999:AAF4tHwXGHOmvGZJnPivM2-QhiASrB7KMZE"
ADMIN_ID = 5160379987
CARD_NUMBER = "9112 3801 3310 4473"
# Ссылка на GitHub Pages (замени после деплоя!)
SITE_URL = "https://твой-ник.github.io/darkdonate"

bot = telebot.TeleBot(TOKEN)

# ==================== ТОВАРЫ ====================
PRODUCTS = {
    "kit_plus": {"name": "⚡ КИТ PLUS", "price_rub": 9, "stars": 10, "desc": "Полуалмазная броня, меч острота I, 12 золотых яблок"},
    "kit_rare": {"name": "💎 КИТ РЕДКИЙ", "price_rub": 19, "stars": 21, "desc": "Алмазная броня, меч острота II, 24 алмаза"},
    "kit_epic": {"name": "⭐ КИТ ЕПИК", "price_rub": 29, "stars": 32, "desc": "Полунезерит, меч острота III"},
    "kit_mythic": {"name": "🐉 КИТ МИФИК", "price_rub": 37, "stars": 41, "desc": "Незерит, меч+копье"},
    "kit_legendary": {"name": "👑 КИТ ЛЕГЕНДАРНЫЙ", "price_rub": 39, "stars": 43, "desc": "Фулл незерит, меч острота IV"},
    "kit_god": {"name": "⚡ КИТ БОГА", "price_rub": 99, "stars": 110, "desc": "Божественный набор"},
    "prefix_plus": {"name": "🏷️ ПРЕФИКС ПЛЮС", "price_rub": 19, "stars": 21, "desc": "Префикс Plus"},
    "prefix_diamond": {"name": "💎 ПРЕФИКС АЛМАЗ", "price_rub": 39, "stars": 43, "desc": "Префикс Алмаз"},
    "prefix_dragon": {"name": "🐉 ПРЕФИКС ДРАКОН", "price_rub": 59, "stars": 65, "desc": "Префикс Дракон"},
    "prefix_lord": {"name": "👑 ПРЕФИКС ЛОРД", "price_rub": 129, "stars": 142, "desc": "Префикс Лорд"},
    "prefix_darklord": {"name": "💀 ПРЕФИКС ТЕМНЫЙ ЛОРД", "price_rub": 199, "stars": 219, "desc": "Самый редкий префикс"},
}

# ==================== ХРАНЕНИЕ ЗАКАЗОВ ====================
orders_file = "orders.json"

def load_orders():
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(orders_file, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# ==================== ГЛАВНОЕ МЕНЮ ====================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        InlineKeyboardButton("⚡ КИТЫ", callback_data="show_kits"),
        InlineKeyboardButton("👑 ПРЕФИКСЫ", callback_data="show_prefixes")
    )
    markup.add(
        InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical"),
        InlineKeyboardButton("❓ КАК КУПИТЬ?", callback_data="how_to_buy")
    )
    markup.add(
        InlineKeyboardButton("📊 СТАТУС ЗАКАЗА", callback_data="check_status")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "🌟 <b>DARKDONATE БОТ</b> 🌟\n\n"
        "⚡ <b>Выберите категорию:</b>\n\n"
        "💳 <b>Способы оплаты:</b>\n"
        "• Telegram Stars (⭐) — моментально\n"
        "• Банковская карта — ручная проверка\n\n"
        "✅ <b>После оплаты товар выдадут в течение 5 минут!</b>",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

# ==================== ПОКАЗ КИТОВ ====================
@bot.callback_query_handler(func=lambda call: call.data == "show_kits")
def show_kits(call):
    markup = InlineKeyboardMarkup(row_width=1)
    
    kits = ["kit_plus", "kit_rare", "kit_epic", "kit_mythic", "kit_legendary", "kit_god"]
    for kit in kits:
        p = PRODUCTS[kit]
        markup.add(InlineKeyboardButton(f"{p['name']} - {p['price_rub']}₽ / {p['stars']}⭐", callback_data=f"buy_{kit}"))
    
    markup.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        "⚔️ <b>ВЫБЕРИТЕ КИТ:</b>\n\n"
        "Кликните на товар для оплаты",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ==================== ПОКАЗ ПРЕФИКСОВ ====================
@bot.callback_query_handler(func=lambda call: call.data == "show_prefixes")
def show_prefixes(call):
    markup = InlineKeyboardMarkup(row_width=1)
    
    prefixes = ["prefix_plus", "prefix_diamond", "prefix_dragon", "prefix_lord", "prefix_darklord"]
    for pref in prefixes:
        p = PRODUCTS[pref]
        markup.add(InlineKeyboardButton(f"{p['name']} - {p['price_rub']}₽ / {p['stars']}⭐", callback_data=f"buy_{pref}"))
    
    markup.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        "👑 <b>ВЫБЕРИТЕ ПРЕФИКС:</b>\n\n"
        "Кликните на товар для оплаты",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ==================== ВЫБОР ТОВАРА ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_product(call):
    product_key = call.data.replace('buy_', '')
    product = PRODUCTS.get(product_key)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⭐ Оплатить {product['stars']} Stars", callback_data=f"pay_stars_{product_key}"),
        InlineKeyboardButton(f"💳 Оплатить картой {product['price_rub']}₽", callback_data=f"pay_card_{product_key}")
    )
    markup.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        f"🛒 <b>{product['name']}</b>\n\n"
        f"📦 {product['desc']}\n\n"
        f"💰 Цена: {product['price_rub']} ₽ / {product['stars']} ⭐\n\n"
        f"<b>Выберите способ оплаты:</b>",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ==================== ОПЛАТА STARS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_stars_'))
def pay_with_stars(call):
    product_key = call.data.replace('pay_stars_', '')
    product = PRODUCTS.get(product_key)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
        return
    
    # Запрашиваем никнейм
    msg = bot.send_message(
        call.message.chat.id,
        f"🎮 <b>Введите ваш игровой никнейм:</b>\n\n"
        f"Товар: {product['name']}\n"
        f"Сумма: {product['stars']} ⭐",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, lambda m: process_stars_payment(m, product, call.message))

def process_stars_payment(message, product, original_msg):
    nick = message.text.strip()
    if not nick or len(nick) < 3:
        bot.send_message(message.chat.id, "❌ Введите корректный никнейм (минимум 3 символа)!")
        return
    
    # Создаем счет для оплаты Stars
    prices = [LabeledPrice(label=product['name'], amount=product['stars'])]
    
    try:
        bot.send_invoice(
            message.chat.id,
            title=f"DarkDonate - {product['name']}",
            description=f"Игрок: {nick}\n{product['desc']}",
            invoice_payload=f"stars_{product_key}_{nick}_{int(time.time())}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="darkdonate_payment",
            need_name=False,
            need_phone_number=False,
            need_email=False
        )
        
        # Сохраняем заказ
        orders = load_orders()
        order_id = str(int(time.time()))
        orders[order_id] = {
            'id': order_id,
            'product': product['name'],
            'price_rub': product['price_rub'],
            'stars': product['stars'],
            'player': nick,
            'user_id': message.chat.id,
            'username': message.from_user.username,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending',
            'payment_method': 'stars'
        }
        save_orders(orders)
        
        bot.send_message(
            ADMIN_ID,
            f"🛒 <b>НОВЫЙ ЗАКАЗ (STARS)</b>\n\n"
            f"🎁 {product['name']}\n"
            f"⭐ {product['stars']} Stars\n"
            f"👤 {nick}\n"
            f"🆔 #{order_id}",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ==================== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ STARS ====================
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    payment = message.successful_payment
    invoice_payload = payment.invoice_payload
    
    parts = invoice_payload.split('_')
    if len(parts) >= 4:
        product_key = parts[1]
        nick = parts[2]
        product = PRODUCTS.get(product_key)
        
        if product:
            orders = load_orders()
            for order_id, order in orders.items():
                if order['player'] == nick and order['product'] == product['name'] and order['status'] == 'pending':
                    order['status'] = 'completed'
                    order['payment_id'] = payment.telegram_payment_charge_id
                    order['confirmed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_orders(orders)
                    
                    bot.send_message(
                        ADMIN_ID,
                        f"✅ <b>ОПЛАЧЕНО STARS!</b>\n\n"
                        f"🎁 {product['name']}\n"
                        f"⭐ {payment.total_amount / 100} Stars\n"
                        f"👤 {nick}",
                        parse_mode='HTML'
                    )
                    
                    markup = InlineKeyboardMarkup()
                    markup.add(
                        InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical"),
                        InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
                    )
                    
                    bot.send_message(
                        message.chat.id,
                        f"✅ <b>ОПЛАТА УСПЕШНА!</b>\n\n"
                        f"🎁 Товар: {product['name']}\n"
                        f"⭐ Списано: {payment.total_amount / 100} Stars\n"
                        f"👤 Игрок: {nick}\n\n"
                        f"🎉 Товар будет выдан в течение 5 минут!",
                        parse_mode='HTML',
                        reply_markup=markup
                    )
                    break

# ==================== ОПЛАТА КАРТОЙ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_card_'))
def pay_with_card(call):
    product_key = call.data.replace('pay_card_', '')
    product = PRODUCTS.get(product_key)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
        return
    
    # Запрашиваем никнейм
    msg = bot.send_message(
        call.message.chat.id,
        f"🎮 <b>Введите ваш игровой никнейм:</b>\n\n"
        f"Товар: {product['name']}\n"
        f"Сумма: {product['price_rub']} ₽",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, lambda m: process_card_payment(m, product, call.message))

def process_card_payment(message, product, original_msg):
    nick = message.text.strip()
    if not nick or len(nick) < 3:
        bot.send_message(message.chat.id, "❌ Введите корректный никнейм (минимум 3 символа)!")
        return
    
    order_id = str(int(time.time()))
    orders = load_orders()
    orders[order_id] = {
        'id': order_id,
        'product': product['name'],
        'price_rub': product['price_rub'],
        'player': nick,
        'user_id': message.chat.id,
        'username': message.from_user.username,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'pending',
        'payment_method': 'card'
    }
    save_orders(orders)
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("✅ ПОДТВЕРДИТЬ ОПЛАТУ", callback_data=f"confirm_card_{order_id}"),
        InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    )
    
    bot.send_message(
        message.chat.id,
        f"💳 <b>ЗАКАЗ #{order_id}</b>\n\n"
        f"🎁 Товар: {product['name']}\n"
        f"💰 Сумма: {product['price_rub']} ₽\n"
        f"👤 Игрок: {nick}\n\n"
        f"💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"📝 <b>В комментарии к переводу ОБЯЗАТЕЛЬНО укажите:</b>\n"
        f"<code>{nick}</code>\n\n"
        f"✅ После оплаты нажмите кнопку ниже",
        parse_mode='HTML',
        reply_markup=markup
    )
    
    bot.send_message(
        ADMIN_ID,
        f"🛒 <b>НОВЫЙ ЗАКАЗ (КАРТА)</b>\n\n"
        f"🎁 {product['name']}\n"
        f"💰 {product['price_rub']} ₽\n"
        f"👤 {nick}\n"
        f"🆔 #{order_id}",
        parse_mode='HTML'
    )

# ==================== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ КАРТОЙ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_card_'))
def confirm_card_payment(call):
    order_id = call.data.replace('confirm_card_', '')
    orders = load_orders()
    
    if order_id not in orders:
        bot.answer_callback_query(call.id, "❌ Заказ не найден!")
        return
    
    order = orders[order_id]
    if order['status'] == 'completed':
        bot.answer_callback_query(call.id, "✅ Заказ уже выполнен!")
        return
    
    order['status'] = 'completed'
    order['confirmed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_orders(orders)
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical"),
        InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
    )
    
    bot.edit_message_text(
        f"✅ <b>ЗАКАЗ #{order_id} ПОДТВЕРЖДЁН!</b>\n\n"
        f"🎁 Товар: {order['product']}\n"
        f"💰 Сумма: {order['price_rub']} ₽\n"
        f"👤 Игрок: {order['player']}\n\n"
        f"🎉 Товар будет выдан в течение 5 минут!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    
    bot.send_message(
        ADMIN_ID,
        f"✅ <b>ЗАКАЗ #{order_id} ПОДТВЕРЖДЁН!</b>\n\n"
        f"🎁 {order['product']}\n"
        f"💰 {order['price_rub']} ₽\n"
        f"👤 {order['player']}",
        parse_mode='HTML'
    )
    
    bot.answer_callback_query(call.id, "✅ Заказ подтверждён!")

# ==================== ПРОВЕРКА СТАТУСА ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_status")
def check_status(call):
    msg = bot.send_message(
        call.message.chat.id,
        "📝 <b>Введите номер заказа:</b>\n\n"
        "Пример: /status 1734567890",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, lambda m: process_status_check(m, call.message))

def process_status_check(message, original_msg):
    try:
        order_id = message.text.strip()
        orders = load_orders()
        
        if order_id in orders:
            order = orders[order_id]
            status_text = "✅ ВЫПОЛНЕН" if order['status'] == 'completed' else "⏳ ОЖИДАЕТ ОПЛАТЫ"
            status_emoji = "✅" if order['status'] == 'completed' else "⏳"
            
            bot.send_message(
                message.chat.id,
                f"📦 <b>ЗАКАЗ #{order_id}</b>\n\n"
                f"🎁 Товар: {order['product']}\n"
                f"💰 Сумма: {order['price_rub']} ₽\n"
                f"👤 Игрок: {order['player']}\n"
                f"📅 Дата: {order['date']}\n"
                f"📊 Статус: {status_emoji} {status_text}",
                parse_mode='HTML'
            )
        else:
            bot.send_message(message.chat.id, "❌ Заказ не найден! Проверьте номер.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка! Введите номер заказа.")

# ==================== КАК КУПИТЬ ====================
@bot.callback_query_handler(func=lambda call: call.data == "how_to_buy")
def how_to_buy(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        f"📝 <b>КАК СДЕЛАТЬ ЗАКАЗ:</b>\n\n"
        f"<b>Способ 1: Telegram Stars ⭐ (Мгновенно)</b>\n"
        f"1️⃣ Выберите товар\n"
        f"2️⃣ Нажмите \"Оплатить Stars\"\n"
        f"3️⃣ Введите никнейм\n"
        f"4️⃣ Подтвердите оплату в Telegram\n"
        f"5️⃣ ✅ Товар выдадут автоматически!\n\n"
        f"<b>Способ 2: Банковская карта 💳</b>\n"
        f"1️⃣ Выберите товар\n"
        f"2️⃣ Нажмите \"Оплатить картой\"\n"
        f"3️⃣ Введите никнейм\n"
        f"4️⃣ Переведите сумму на карту: <code>{CARD_NUMBER}</code>\n"
        f"5️⃣ В комментарии укажите свой никнейм\n"
        f"6️⃣ Нажмите кнопку \"ПОДТВЕРДИТЬ ОПЛАТУ\"\n\n"
        f"📞 Поддержка: @DarkYo_offical",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ==================== НАЗАД В МЕНЮ ====================
@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    bot.edit_message_text(
        "🌟 <b>DARKDONATE БОТ</b> 🌟\n\n"
        "⚡ <b>Выберите категорию:</b>\n\n"
        "💳 <b>Способы оплаты:</b>\n"
        "• Telegram Stars (⭐) — моментально\n"
        "• Банковская карта — ручная проверка\n\n"
        "✅ <b>После оплаты товар выдадут в течение 5 минут!</b>",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=main_menu()
    )
    bot.answer_callback_query(call.id)

# ==================== СТАТИСТИКА ДЛЯ АДМИНА ====================
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещён!")
        return
    
    orders = load_orders()
    total = len(orders)
    pending = sum(1 for o in orders.values() if o['status'] == 'pending')
    completed = sum(1 for o in orders.values() if o['status'] == 'completed')
    revenue = sum(float(o['price_rub']) for o in orders.values() if o['status'] == 'completed')
    
    bot.send_message(
        message.chat.id,
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"📦 Всего заказов: {total}\n"
        f"⏳ Ожидают оплаты: {pending}\n"
        f"✅ Выполнено: {completed}\n"
        f"💰 Выручка: {revenue} ₽",
        parse_mode='HTML'
    )

# ==================== ЗАПУСК ====================
print("=" * 50)
print("🤖 БОТ DARKDONATE ЗАПУЩЕН!")
print("=" * 50)
print(f"📱 Бот: https://t.me/DarkYoDonateBot")
print(f"👑 Админ ID: {ADMIN_ID}")
print(f"💳 Карта: {CARD_NUMBER}")
print("=" * 50)

bot.polling(none_stop=True)