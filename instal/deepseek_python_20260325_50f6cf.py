import telebot
import json
import os
import time
from datetime import datetime
from telebot.types import LabeledPrice, ShippingOption, PreCheckoutQuery

# ТОКЕН ВАШЕГО БОТА
TOKEN = "8013266999:AAF4tHwXGHOmvGZJnPivM2-QhiASrB7KMZE"

# ВАШ ID
ADMIN_ID = 5160379987

# Номер карты (для ручных переводов, как запасной вариант)
CARD_NUMBER = "9112 3801 3310 4473"

# Ссылка на сайт
SITE_URL = "https://darkyo-donate.ru"

bot = telebot.TeleBot(TOKEN)

# Хранилище заказов
orders_file = "orders.json"

def load_orders():
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(orders_file, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# Товары (цены в рублях)
PRODUCTS = {
    "kit_plus": {"name": "⚡ КИТ PLUS", "price": 9, "stars": 10, "desc": "Полуалмазная броня, меч острота I, 12 золотых яблок"},
    "kit_rare": {"name": "💎 КИТ РЕДКИЙ", "price": 19, "stars": 21, "desc": "Алмазная броня, меч острота II, 24 алмаза"},
    "kit_epic": {"name": "⭐ КИТ ЕПИК", "price": 29, "stars": 32, "desc": "Полунезерит, меч острота III"},
    "kit_mythic": {"name": "🐉 КИТ МИФИК", "price": 37, "stars": 41, "desc": "Незерит, меч+копье"},
    "kit_legendary": {"name": "👑 КИТ ЛЕГЕНДАРНЫЙ", "price": 39, "stars": 43, "desc": "Фулл незерит, меч острота IV"},
    "kit_god": {"name": "⚡ КИТ БОГА", "price": 99, "stars": 110, "desc": "Божественный набор"},
    "prefix_plus": {"name": "🏷️ ПРЕФИКС ПЛЮС", "price": 19, "stars": 21, "desc": "Префикс Plus"},
    "prefix_diamond": {"name": "💎 ПРЕФИКС АЛМАЗ", "price": 39, "stars": 43, "desc": "Префикс Алмаз"},
    "prefix_dragon": {"name": "🐉 ПРЕФИКС ДРАКОН", "price": 59, "stars": 65, "desc": "Префикс Дракон"},
    "prefix_lord": {"name": "👑 ПРЕФИКС ЛОРД", "price": 129, "stars": 142, "desc": "Префикс Лорд"},
    "prefix_darklord": {"name": "💀 ПРЕФИКС ТЕМНЫЙ ЛОРД", "price": 199, "stars": 219, "desc": "Самый редкий префикс"},
}

# ГЛАВНОЕ МЕНЮ
@bot.message_handler(commands=['start'])
def start_command(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки товаров
    btn_kit_plus = telebot.types.InlineKeyboardButton("⚡ КИТ PLUS - 9₽", callback_data="buy_kit_plus")
    btn_kit_rare = telebot.types.InlineKeyboardButton("💎 КИТ РЕДКИЙ - 19₽", callback_data="buy_kit_rare")
    btn_kit_epic = telebot.types.InlineKeyboardButton("⭐ КИТ ЕПИК - 29₽", callback_data="buy_kit_epic")
    btn_kit_mythic = telebot.types.InlineKeyboardButton("🐉 КИТ МИФИК - 37₽", callback_data="buy_kit_mythic")
    btn_kit_legendary = telebot.types.InlineKeyboardButton("👑 КИТ ЛЕГЕНДАРНЫЙ - 39₽", callback_data="buy_kit_legendary")
    btn_kit_god = telebot.types.InlineKeyboardButton("⚡ КИТ БОГА - 99₽", callback_data="buy_kit_god")
    
    btn_prefix_plus = telebot.types.InlineKeyboardButton("🏷️ ПРЕФИКС ПЛЮС - 19₽", callback_data="buy_prefix_plus")
    btn_prefix_diamond = telebot.types.InlineKeyboardButton("💎 ПРЕФИКС АЛМАЗ - 39₽", callback_data="buy_prefix_diamond")
    btn_prefix_dragon = telebot.types.InlineKeyboardButton("🐉 ПРЕФИКС ДРАКОН - 59₽", callback_data="buy_prefix_dragon")
    btn_prefix_lord = telebot.types.InlineKeyboardButton("👑 ПРЕФИКС ЛОРД - 129₽", callback_data="buy_prefix_lord")
    btn_prefix_darklord = telebot.types.InlineKeyboardButton("💀 ПРЕФИКС ТЕМНЫЙ ЛОРД - 199₽", callback_data="buy_prefix_darklord")
    
    btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    btn_how = telebot.types.InlineKeyboardButton("❓ КАК КУПИТЬ?", callback_data="how_to_buy")
    
    markup.add(btn_kit_plus, btn_kit_rare, btn_kit_epic, btn_kit_mythic, btn_kit_legendary, btn_kit_god)
    markup.add(btn_prefix_plus, btn_prefix_diamond, btn_prefix_dragon, btn_prefix_lord, btn_prefix_darklord)
    markup.add(btn_support, btn_how)
    
    bot.send_message(
        message.chat.id,
        f"🌟 <b>DARKDONATE БОТ</b> 🌟\n\n"
        f"⚡ <b>Выберите товар для оплаты:</b>\n\n"
        f"💳 <b>Способы оплаты:</b>\n"
        f"• Telegram Stars (⭐) — моментально\n"
        f"• Банковская карта — ручная проверка\n\n"
        f"✅ <b>После оплаты товар выдадут в течение 5 минут!</b>\n\n"
        f"📞 Поддержка: @DarkYo_offical",
        parse_mode='HTML',
        reply_markup=markup
    )

# Обработка выбора товара
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_product(call):
    product_key = call.data.replace('buy_', '')
    product = PRODUCTS.get(product_key)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки оплаты
    btn_stars = telebot.types.InlineKeyboardButton(f"⭐ Оплатить {product['stars']} Stars", callback_data=f"pay_stars_{product_key}")
    btn_card = telebot.types.InlineKeyboardButton(f"💳 Оплатить картой {product['price']}₽", callback_data=f"pay_card_{product_key}")
    btn_back = telebot.types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu")
    
    markup.add(btn_stars, btn_card, btn_back)
    
    bot.edit_message_text(
        f"🛒 <b>ТОВАР: {product['name']}</b>\n\n"
        f"📦 Описание: {product['desc']}\n"
        f"💰 Цена: {product['price']} ₽ / {product['stars']} ⭐\n\n"
        f"<b>Выберите способ оплаты:</b>",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ОПЛАТА ЧЕРЕЗ TELEGRAM STARS
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_stars_'))
def pay_with_stars(call):
    product_key = call.data.replace('pay_stars_', '')
    product = PRODUCTS.get(product_key)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден!")
        return
    
    # Запрашиваем никнейм игрока
    msg = bot.send_message(
        call.message.chat.id,
        f"🎮 <b>Введите ваш игровой никнейм:</b>\n\n"
        f"Товар: {product['name']}\n"
        f"Сумма: {product['stars']} ⭐\n\n"
        f"После ввода ника откроется окно оплаты",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, lambda m: process_stars_payment(m, product, call.message))

def process_stars_payment(message, product, original_msg):
    nick = message.text.strip()
    if not nick:
        bot.send_message(message.chat.id, "❌ Введите корректный никнейм!")
        return
    
    # Создаём инвойс для оплаты Telegram Stars
    prices = [LabeledPrice(label=product['name'], amount=product['stars'])]
    
    try:
        bot.send_invoice(
            message.chat.id,
            title=f"DarkDonate - {product['name']}",
            description=f"Игрок: {nick}\n{product['desc']}",
            invoice_payload=f"stars_{product['name']}_{nick}_{int(time.time())}",
            provider_token="",  # Для Telegram Stars оставляем пустым
            currency="XTR",  # XTR = Telegram Stars
            prices=prices,
            start_parameter="darkdonate",
            need_name=False,
            need_phone_number=False,
            need_email=False
        )
        
        # Сохраняем временный заказ
        orders = load_orders()
        order_id = str(int(time.time()))
        orders[order_id] = {
            'id': order_id,
            'product': product['name'],
            'price': product['price'],
            'stars': product['stars'],
            'player': nick,
            'user_id': message.chat.id,
            'username': message.from_user.username,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending',
            'payment_method': 'stars'
        }
        save_orders(orders)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# Обработка успешной оплаты Telegram Stars
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    payment = message.successful_payment
    invoice_payload = payment.invoice_payload
    
    # Извлекаем данные из payload
    parts = invoice_payload.split('_')
    if len(parts) >= 3:
        product_name = parts[1]
        nick = parts[2]
        
        # Обновляем статус заказа
        orders = load_orders()
        for order_id, order in orders.items():
            if order['player'] == nick and order['product'] == product_name and order['status'] == 'pending':
                order['status'] = 'completed'
                order['payment_id'] = payment.telegram_payment_charge_id
                order['confirmed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_orders(orders)
                
                # Уведомляем админа
                bot.send_message(
                    ADMIN_ID,
                    f"✅ <b>ОПЛАТА ПОЛУЧЕНА ЧЕРЕЗ STARS!</b>\n\n"
                    f"🎁 {product_name}\n"
                    f"💰 {payment.total_amount / 100} ⭐\n"
                    f"👤 {nick}\n"
                    f"🆔 {payment.telegram_payment_charge_id}",
                    parse_mode='HTML'
                )
                
                # Уведомляем покупателя
                markup = telebot.types.InlineKeyboardMarkup()
                btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
                markup.add(btn_support)
                
                bot.send_message(
                    message.chat.id,
                    f"✅ <b>ОПЛАТА УСПЕШНА!</b>\n\n"
                    f"🎁 Товар: {product_name}\n"
                    f"👤 Игрок: {nick}\n\n"
                    f"🎉 Товар будет выдан в течение 5 минут!\n\n"
                    f"📞 Если возникли вопросы: @DarkYo_offical",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                break

# ОПЛАТА КАРТОЙ (ручная проверка)
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
        f"Сумма: {product['price']} ₽\n\n"
        f"После оплаты нажмите кнопку подтверждения",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, lambda m: process_card_payment(m, product, call.message))

def process_card_payment(message, product, original_msg):
    nick = message.text.strip()
    if not nick:
        bot.send_message(message.chat.id, "❌ Введите корректный никнейм!")
        return
    
    # Создаём заказ
    order_id = str(int(time.time()))
    orders = load_orders()
    orders[order_id] = {
        'id': order_id,
        'product': product['name'],
        'price': product['price'],
        'player': nick,
        'user_id': message.chat.id,
        'username': message.from_user.username,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'pending',
        'payment_method': 'card'
    }
    save_orders(orders)
    
    # Кнопки
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_confirm = telebot.types.InlineKeyboardButton("✅ ПОДТВЕРДИТЬ ОПЛАТУ", callback_data=f"confirm_card_{order_id}")
    btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    markup.add(btn_confirm, btn_support)
    
    bot.send_message(
        message.chat.id,
        f"💳 <b>ЗАКАЗ #{order_id}</b>\n\n"
        f"🎁 Товар: {product['name']}\n"
        f"💰 Сумма: {product['price']} ₽\n"
        f"👤 Игрок: {nick}\n\n"
        f"💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"📝 <b>В комментарии к переводу укажите:</b> <code>{nick}</code>\n\n"
        f"✅ После оплаты нажмите кнопку ниже",
        parse_mode='HTML',
        reply_markup=markup
    )
    
    # Уведомляем админа
    bot.send_message(
        ADMIN_ID,
        f"🛒 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
        f"🎁 {product['name']}\n"
        f"💰 {product['price']} ₽\n"
        f"👤 {nick}\n"
        f"👥 @{message.from_user.username}\n"
        f"💳 Оплата картой (ожидает подтверждения)",
        parse_mode='HTML'
    )

# Подтверждение оплаты картой
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
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    markup.add(btn_support)
    
    bot.edit_message_text(
        f"✅ <b>ЗАКАЗ #{order_id} ПОДТВЕРЖДЁН!</b>\n\n"
        f"🎁 Товар: {order['product']}\n"
        f"💰 Сумма: {order['price']} ₽\n"
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
        f"💰 {order['price']} ₽\n"
        f"👤 {order['player']}\n"
        f"🕐 {order['confirmed_at']}",
        parse_mode='HTML'
    )
    
    bot.answer_callback_query(call.id, "✅ Заказ подтверждён!")

# КАК КУПИТЬ
@bot.callback_query_handler(func=lambda call: call.data == "how_to_buy")
def how_to_buy(call):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_back = telebot.types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_menu")
    markup.add(btn_back)
    
    bot.edit_message_text(
        f"📝 <b>КАК СДЕЛАТЬ ЗАКАЗ:</b>\n\n"
        f"<b>Способ 1: Telegram Stars ⭐ (Мгновенно)</b>\n"
        f"1️⃣ Выберите товар\n"
        f"2️⃣ Нажмите \"Оплатить Stars\"\n"
        f"3️⃣ Введите никнейм\n"
        f"4️⃣ Подтвердите оплату в Telegram\n"
        f"5️⃣ ✅ Товар выдадут автоматически!\n\n"
        f"<b>Способ 2: Банковская карта 💳 (Ручная проверка)</b>\n"
        f"1️⃣ Выберите товар\n"
        f"2️⃣ Нажмите \"Оплатить картой\"\n"
        f"3️⃣ Введите никнейм\n"
        f"4️⃣ Переведите сумму на карту: <code>{CARD_NUMBER}</code>\n"
        f"5️⃣ В комментарии укажите свой никнейм\n"
        f"6️⃣ Нажмите кнопку \"ПОДТВЕРДИТЬ ОПЛАТУ\"\n"
        f"7️⃣ ✅ Администратор проверит и выдаст товар\n\n"
        f"📞 Поддержка: @DarkYo_offical",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# НАЗАД В МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    btn_kit_plus = telebot.types.InlineKeyboardButton("⚡ КИТ PLUS - 9₽", callback_data="buy_kit_plus")
    btn_kit_rare = telebot.types.InlineKeyboardButton("💎 КИТ РЕДКИЙ - 19₽", callback_data="buy_kit_rare")
    btn_kit_epic = telebot.types.InlineKeyboardButton("⭐ КИТ ЕПИК - 29₽", callback_data="buy_kit_epic")
    btn_kit_mythic = telebot.types.InlineKeyboardButton("🐉 КИТ МИФИК - 37₽", callback_data="buy_kit_mythic")
    btn_kit_legendary = telebot.types.InlineKeyboardButton("👑 КИТ ЛЕГЕНДАРНЫЙ - 39₽", callback_data="buy_kit_legendary")
    btn_kit_god = telebot.types.InlineKeyboardButton("⚡ КИТ БОГА - 99₽", callback_data="buy_kit_god")
    
    btn_prefix_plus = telebot.types.InlineKeyboardButton("🏷️ ПРЕФИКС ПЛЮС - 19₽", callback_data="buy_prefix_plus")
    btn_prefix_diamond = telebot.types.InlineKeyboardButton("💎 ПРЕФИКС АЛМАЗ - 39₽", callback_data="buy_prefix_diamond")
    btn_prefix_dragon = telebot.types.InlineKeyboardButton("🐉 ПРЕФИКС ДРАКОН - 59₽", callback_data="buy_prefix_dragon")
    btn_prefix_lord = telebot.types.InlineKeyboardButton("👑 ПРЕФИКС ЛОРД - 129₽", callback_data="buy_prefix_lord")
    btn_prefix_darklord = telebot.types.InlineKeyboardButton("💀 ПРЕФИКС ТЕМНЫЙ ЛОРД - 199₽", callback_data="buy_prefix_darklord")
    
    btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    btn_how = telebot.types.InlineKeyboardButton("❓ КАК КУПИТЬ?", callback_data="how_to_buy")
    
    markup.add(btn_kit_plus, btn_kit_rare, btn_kit_epic, btn_kit_mythic, btn_kit_legendary, btn_kit_god)
    markup.add(btn_prefix_plus, btn_prefix_diamond, btn_prefix_dragon, btn_prefix_lord, btn_prefix_darklord)
    markup.add(btn_support, btn_how)
    
    bot.edit_message_text(
        f"🌟 <b>DARKDONATE БОТ</b> 🌟\n\n"
        f"⚡ <b>Выберите товар для оплаты:</b>\n\n"
        f"💳 <b>Способы оплаты:</b>\n"
        f"• Telegram Stars (⭐) — моментально\n"
        f"• Банковская карта — ручная проверка\n\n"
        f"✅ <b>После оплаты товар выдадут в течение 5 минут!</b>",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# КОМАНДА /status
@bot.message_handler(commands=['status'])
def status_command(message):
    try:
        order_id = message.text.split()[1]
        orders = load_orders()
        
        if order_id in orders:
            order = orders[order_id]
            status_text = "✅ ВЫПОЛНЕН" if order['status'] == 'completed' else "⏳ ОЖИДАЕТ"
            status_emoji = "✅" if order['status'] == 'completed' else "⏳"
            
            bot.send_message(
                message.chat.id,
                f"📦 <b>ЗАКАЗ #{order_id}</b>\n\n"
                f"🎁 Товар: {order['product']}\n"
                f"💰 Сумма: {order['price']} ₽\n"
                f"👤 Игрок: {order['player']}\n"
                f"📅 Дата: {order['date']}\n"
                f"📊 Статус: {status_emoji} {status_text}",
                parse_mode='HTML'
            )
        else:
            bot.send_message(message.chat.id, "❌ Заказ не найден!")
    except:
        bot.send_message(message.chat.id, "📝 Используйте: /status НОМЕР_ЗАКАЗА")

# КОМАНДА /stats для админа
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещён!")
        return
    
    orders = load_orders()
    total = len(orders)
    pending = sum(1 for o in orders.values() if o['status'] == 'pending')
    completed = sum(1 for o in orders.values() if o['status'] == 'completed')
    revenue = sum(float(o['price']) for o in orders.values() if o['status'] == 'completed')
    
    bot.send_message(
        message.chat.id,
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"📦 Всего заказов: {total}\n"
        f"⏳ Ожидают: {pending}\n"
        f"✅ Выполнено: {completed}\n"
        f"💰 Выручка: {revenue} ₽",
        parse_mode='HTML'
    )

print("=" * 50)
print("🤖 БОТ DARKDONATE ЗАПУЩЕН!")
print("=" * 50)
print(f"📱 Бот: https://t.me/DarkYoDonateBot")
print(f"👑 Админ ID: {ADMIN_ID}")
print(f"💳 Карта: {CARD_NUMBER}")
print("=" * 50)
print("✅ ДОСТУПНЫЕ СПОСОБЫ ОПЛАТЫ:")
print("   • Telegram Stars — моментальная оплата внутри бота")
print("   • Банковская карта — ручная проверка")
print("=" * 50)

bot.polling(none_stop=True)