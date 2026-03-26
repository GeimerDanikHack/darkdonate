import telebot
import time
import json
import os
from datetime import datetime

# ТОКЕН ВАШЕГО БОТА
TOKEN = "8013266999:AAF4tHwXGHOmvGZJnPivM2-QhiASrB7KMZE"

# ВАШ ID (получен от @userinfobot)
ADMIN_ID = 5160379987  # Ваш ID!

# Номер карты
CARD_NUMBER = "9112 3801 3310 4473"

# Ссылка на сайт - ЗАМЕНИТЕ НА ВАШУ!
SITE_URL = "https://darkyo-donate.ru"  # Замените на ваш реальный URL

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

# Команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Проверяем параметр заказа
    if len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param.startswith('pay_'):
            parts = param.split('_')
            if len(parts) >= 5:
                order_id = parts[1]
                product_name = parts[2]
                price = parts[3]
                player_nick = parts[4]
                
                orders = load_orders()
                orders[order_id] = {
                    'id': order_id,
                    'product': product_name,
                    'price': price,
                    'player': player_nick,
                    'user_id': user_id,
                    'username': username,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'pending'
                }
                save_orders(orders)
                
                # Кнопки
                markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                btn_confirm = telebot.types.InlineKeyboardButton("✅ ПОДТВЕРДИТЬ ОПЛАТУ", callback_data=f"confirm_{order_id}")
                btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
                btn_site = telebot.types.InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
                markup.add(btn_confirm, btn_support, btn_site)
                
                bot.send_message(
                    message.chat.id,
                    f"🎁 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
                    f"📦 Товар: <b>{product_name}</b>\n"
                    f"💰 Сумма: <b>{price} ₽</b>\n"
                    f"👤 Игрок: <b>{player_nick}</b>\n\n"
                    f"💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>\n"
                    f"<code>{CARD_NUMBER}</code>\n\n"
                    f"📝 <b>ВАЖНО!</b> В комментарии к переводу ОБЯЗАТЕЛЬНО укажите:\n"
                    f"<code>{player_nick}</code>\n\n"
                    f"✅ После оплаты нажмите кнопку ниже для подтверждения",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
                # Уведомляем админа
                bot.send_message(
                    ADMIN_ID,
                    f"🛒 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
                    f"🎁 {product_name}\n"
                    f"💰 {price} ₽\n"
                    f"👤 {player_nick}\n"
                    f"👥 @{username}\n"
                    f"🕐 {datetime.now().strftime('%H:%M:%S')}",
                    parse_mode='HTML'
                )
                return
    
    # Обычный /start - КРАСИВОЕ ПРИВЕТСТВИЕ
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_site = telebot.types.InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
    btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
    btn_how = telebot.types.InlineKeyboardButton("❓ КАК КУПИТЬ?", callback_data="how_to_buy")
    btn_status = telebot.types.InlineKeyboardButton("📊 СТАТУС ЗАКАЗА", callback_data="status")
    markup.add(btn_site, btn_support, btn_how, btn_status)
    
    bot.send_message(
        message.chat.id,
        f"🌟 <b>ДОБРО ПОЖАЛОВАТЬ В DARKDONATE!</b> 🌟\n\n"
        f"⚡ Лучший донат магазин сервера DarkYo\n\n"
        f"💳 <b>Реквизиты для оплаты:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"🎁 <b>На сайте вас ждут:</b>\n"
        f"• 25+ уникальных китов\n"
        f"• 10+ эксклюзивных префиксов\n"
        f"• Кейсы с легендарными предметами\n"
        f"• Эффекты и частицы\n\n"
        f"✅ <b>После оплаты товар выдадут в течение 5 минут!</b>\n\n"
        f"📞 <b>Поддержка:</b> @DarkYo_offical",
        parse_mode='HTML',
        reply_markup=markup
    )

# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith('confirm_'):
        order_id = call.data.split('_')[1]
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
        
        # Обновляем сообщение
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_site = telebot.types.InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
        btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
        markup.add(btn_site, btn_support)
        
        bot.edit_message_text(
            f"✅ <b>ЗАКАЗ #{order_id} ПОДТВЕРЖДЁН!</b>\n\n"
            f"🎁 Товар: {order['product']}\n"
            f"💰 Сумма: {order['price']} ₽\n"
            f"👤 Игрок: {order['player']}\n\n"
            f"🎉 <b>Товар будет выдан в течение 5 минут!</b>\n\n"
            f"📞 Если возникли вопросы: @DarkYo_offical",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        
        # Уведомляем админа
        bot.send_message(
            ADMIN_ID,
            f"✅ <b>ЗАКАЗ #{order_id} ПОДТВЕРЖДЁН!</b>\n\n"
            f"🎁 {order['product']}\n"
            f"💰 {order['price']} ₽\n"
            f"👤 {order['player']}\n"
            f"🕐 {order['confirmed_at']}\n\n"
            f"🎁 <b>Нужно выдать товар вручную!</b>",
            parse_mode='HTML'
        )
        
        bot.answer_callback_query(call.id, "✅ Заказ подтверждён! Товар выдадут в ближайшее время")
    
    elif call.data == "how_to_buy":
        markup = telebot.types.InlineKeyboardMarkup()
        btn_back = telebot.types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"📝 <b>КАК СДЕЛАТЬ ЗАКАЗ:</b>\n\n"
            f"1️⃣ <b>Перейдите на сайт</b> {SITE_URL}\n"
            f"2️⃣ <b>Выберите товар</b> и нажмите \"Купить\"\n"
            f"3️⃣ <b>Введите свой никнейм</b> в открывшемся окне\n"
            f"4️⃣ <b>Оплатите на карту</b> <code>{CARD_NUMBER}</code>\n"
            f"5️⃣ <b>В комментарии к переводу укажите свой никнейм</b>\n"
            f"6️⃣ <b>Вернитесь в этот чат</b> и нажмите кнопку \"ПОДТВЕРДИТЬ ОПЛАТУ\"\n\n"
            f"✅ <b>После подтверждения товар выдадут в течение 5 минут!</b>\n\n"
            f"📞 <b>Поддержка:</b> @DarkYo_offical",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
    
    elif call.data == "status":
        markup = telebot.types.InlineKeyboardMarkup()
        btn_back = telebot.types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"📊 <b>ПРОВЕРКА СТАТУСА ЗАКАЗА</b>\n\n"
            f"Чтобы проверить статус заказа, используйте команду:\n"
            f"<code>/status НОМЕР_ЗАКАЗА</code>\n\n"
            f"Пример: <code>/status 1234567890</code>\n\n"
            f"Если вы не знаете номер заказа, обратитесь в поддержку: @DarkYo_offical",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
    
    elif call.data == "back":
        # Возвращаем главное меню
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_site = telebot.types.InlineKeyboardButton("🌐 ПЕРЕЙТИ НА САЙТ", url=SITE_URL)
        btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
        btn_how = telebot.types.InlineKeyboardButton("❓ КАК КУПИТЬ?", callback_data="how_to_buy")
        btn_status = telebot.types.InlineKeyboardButton("📊 СТАТУС ЗАКАЗА", callback_data="status")
        markup.add(btn_site, btn_support, btn_how, btn_status)
        
        bot.edit_message_text(
            f"🌟 <b>ДОБРО ПОЖАЛОВАТЬ В DARKDONATE!</b> 🌟\n\n"
            f"⚡ Лучший донат магазин сервера DarkYo\n\n"
            f"💳 <b>Реквизиты для оплаты:</b>\n"
            f"<code>{CARD_NUMBER}</code>\n\n"
            f"🎁 <b>На сайте вас ждут:</b>\n"
            f"• 25+ уникальных китов\n"
            f"• 10+ эксклюзивных префиксов\n"
            f"• Кейсы с легендарными предметами\n"
            f"• Эффекты и частицы\n\n"
            f"✅ <b>После оплаты товар выдадут в течение 5 минут!</b>\n\n"
            f"📞 <b>Поддержка:</b> @DarkYo_offical",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

# Команда /status
@bot.message_handler(commands=['status'])
def status_command(message):
    try:
        order_id = message.text.split()[1]
        orders = load_orders()
        
        if order_id in orders:
            order = orders[order_id]
            status_text = "✅ ВЫПОЛНЕН" if order['status'] == 'completed' else "⏳ ОЖИДАЕТ ОПЛАТЫ"
            status_emoji = "✅" if order['status'] == 'completed' else "⏳"
            
            markup = telebot.types.InlineKeyboardMarkup()
            btn_support = telebot.types.InlineKeyboardButton("📞 ПОДДЕРЖКА", url="https://t.me/DarkYo_offical")
            markup.add(btn_support)
            
            bot.send_message(
                message.chat.id,
                f"📦 <b>ЗАКАЗ #{order_id}</b>\n\n"
                f"🎁 Товар: <b>{order['product']}</b>\n"
                f"💰 Сумма: <b>{order['price']} ₽</b>\n"
                f"👤 Игрок: <b>{order['player']}</b>\n"
                f"📅 Дата: {order['date']}\n"
                f"📊 Статус: {status_emoji} {status_text}\n\n"
                f"{'🎉 Товар уже выдан! Спасибо за покупку!' if order['status'] == 'completed' else '💳 Оплатите на карту ' + CARD_NUMBER + ' и нажмите кнопку подтверждения'}",
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Заказ не найден! Проверьте номер заказа.")
    except:
        bot.send_message(message.chat.id, "📝 Используйте: /status НОМЕР_ЗАКАЗА\n\nПример: /status 1234567890")

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📚 <b>ДОСТУПНЫЕ КОМАНДЫ:</b>\n\n"
        "/start - Главное меню\n"
        "/status [номер] - Проверить статус заказа\n"
        "/help - Показать это сообщение\n\n"
        f"💳 <b>Реквизиты:</b> <code>{CARD_NUMBER}</code>\n\n"
        f"🌐 <b>Сайт:</b> {SITE_URL}\n\n"
        "📞 <b>Поддержка:</b> @DarkYo_offical",
        parse_mode='HTML'
    )

# Команда /stats для админа
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещён! Эта команда только для администратора.")
        return
    
    orders = load_orders()
    total = len(orders)
    pending = sum(1 for o in orders.values() if o['status'] == 'pending')
    completed = sum(1 for o in orders.values() if o['status'] == 'completed')
    revenue = sum(float(o['price']) for o in orders.values() if o['status'] == 'completed')
    
    # Список последних заказов
    recent = list(orders.values())[-5:] if orders else []
    recent_text = ""
    if recent:
        recent_text = "\n📋 <b>ПОСЛЕДНИЕ ЗАКАЗЫ:</b>\n"
        for o in reversed(recent):
            status = "✅" if o['status'] == 'completed' else "⏳"
            recent_text += f"{status} #{o['id']} - {o['product']} - {o['player']}\n"
    
    bot.send_message(
        message.chat.id,
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"📦 Всего заказов: <b>{total}</b>\n"
        f"⏳ Ожидают оплаты: <b>{pending}</b>\n"
        f"✅ Выполнено: <b>{completed}</b>\n"
        f"💰 Общая выручка: <b>{revenue} ₽</b>\n\n"
        f"{recent_text}",
        parse_mode='HTML'
    )

print("=" * 50)
print("🤖 БОТ DARKDONATE ЗАПУЩЕН!")
print("=" * 50)
print(f"📱 Бот: https://t.me/DarkYoDonateBot")
print(f"👑 Админ ID: {ADMIN_ID}")
print(f"💳 Карта: {CARD_NUMBER}")
print(f"🌐 Сайт: {SITE_URL}")
print("=" * 50)
print("Нажми Ctrl+C для остановки")
print("=" * 50)

bot.polling(none_stop=True)