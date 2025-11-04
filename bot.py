# bot_webhook.py — версия для webhook (Render)
from pathlib import Path
from typing import Set

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Переменная окружения TELEGRAM_TOKEN не найдена. Проверь .env")

# URL вашего приложения на Render (замените после создания!)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://long-time.onrender.com")
PORT = int(os.getenv("PORT", 8080))

# ---- Контент (правь под себя) ----
PROJECT_NAME = "СПб: Женские истории репрессий"
ABOUT_TEXT = (
    "Этот бот — короткая и бережная прогулка по Санкт-Петербургу. "
    "Мы предлагаем 4 точки памяти о женщинах, пострадавших от репрессий. "
    "Каждая точка — это место, факт и несколько строк, помогающих увидеть город иначе."
)

HELP_TEXT = (
    "Как пользоваться:\n"
    "• Нажмите «Карта маршрута», чтобы увидеть все точки.\n"
    "• «Начать экскурсию» проведёт вас последовательно по маршруту.\n"
    "• «О проекте» — краткое описание замысла.\n\n"
    "Команды: /start, /menu, /help"
)

FINAL_MESSAGE = (
    "Спасибо, что прошли маршрут. Память держится на конкретных историях — "
    "иногда тихие знаки рядом с нами значат больше слов."
)

ASSETS = Path("assets")
MAP_IMAGE = ASSETS / "map.jpg"
MAP_CAPTION = "Карта маршрута: 4 точки памяти. Вы можете начать с первой — бот проведёт вас шаг за шагом."

# Аудио файлы для приветствия
AUDIO1 = ASSETS / "audio1.ogg"
AUDIO2 = ASSETS / "audio2.ogg"

# 4 точки (заглушки текста и имена файлов; положи фото в assets/)
POINTS = [
    {
        "title": "Точка 1 — Дом на …",
        "text": (
            "Краткий бережный текст (200–300 слов): что это за место, чья это история, "
            "какие даты и факты связаны с репрессиями. Пиши спокойно и точно, без оценочных клише."
        ),
        "photos": [ASSETS / "p1_1.jpg", ASSETS / "p1_2.jpg"],
    },
    {
        "title": "Точка 2 — …",
        "text": (
            "Основной текст (200–300 слов). Хорошо, если будет небольшая цитата из документа или письма "
            "— 1–2 строки, чтобы дать голос времени."
        ),
        "photos": [ASSETS / "p2_1.jpg"],
    },
    {
        "title": "Точка 3 — …",
        "text": (
            "Основной текст (200–300 слов). Можно мягко соотнести прошлое с сегодняшним видом места."
        ),
        "photos": [ASSETS / "p3_1.jpg"],
    },
    {
        "title": "Точка 4 — …",
        "text": (
            "Финальная точка (200–300 слов). Аккуратно подведи к ощущению общей памяти и уважения."
        ),
        "photos": [ASSETS / "p4_1.jpg"],
    },
]

# ---- callback_data для кнопок ----
CB_MENU_MAP = "menu_map"
CB_MENU_START = "menu_start"
CB_MENU_ABOUT = "menu_about"

# Новые callback для первого меню
CB_AUDIO_INFO = "audio_info"
CB_FEEDBACK = "feedback"
CB_PROBLEMS = "problems"

# Callback для подменю
CB_START_TOUR = "start_tour"
CB_WRITE_US = "write_us"
CB_BACK_TO_MENU = "nav_menu"

CB_NEXT = "nav_next"
CB_BACK_TO_MAP = "nav_map"

# ---- Разметка кнопок ----

# Первое меню после /start
def welcome_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎧 Аудио", callback_data=CB_AUDIO_INFO)],
            [InlineKeyboardButton("💬 Обратная связь", callback_data=CB_FEEDBACK)],
            [InlineKeyboardButton("❓ Возникли проблемы?", callback_data=CB_PROBLEMS)],
        ]
    )

# Подменю для "Аудио"
def audio_submenu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Начать экскурсию", callback_data=CB_START_TOUR)],
            [InlineKeyboardButton("↩️ Вернуться в меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

# Подменю для "Обратная связь"
def feedback_submenu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✍️ Написать нам", callback_data=CB_WRITE_US)],
            [InlineKeyboardButton("↩️ Вернуться в меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

# Главное меню (старое, оставляем для совместимости)
def main_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗺️ КАРТА МАРШРУТА", callback_data=CB_MENU_MAP)],
            [InlineKeyboardButton("▶️ Начать Экскурсию", callback_data=CB_MENU_START)],
            [InlineKeyboardButton("ℹ️ О проекте", callback_data=CB_MENU_ABOUT)],
        ]
    )

def point_nav_inline(is_last: bool) -> InlineKeyboardMarkup:
    first_row_text = "Завершить маршрут →" if is_last else "Следующая точка →"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(first_row_text, callback_data=CB_NEXT)],
            [InlineKeyboardButton("↩️ Вернуться к карте", callback_data=CB_BACK_TO_MAP)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

# ---- состояние пользователя ----
def _state(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "idx" not in context.user_data:
        context.user_data["idx"] = 0
    if "visited" not in context.user_data:
        context.user_data["visited"] = set()  # type: ignore
    return context.user_data

# ---- отправка карты ----
async def send_map(chat, reply_markup=None):
    if MAP_IMAGE.exists():
        with open(MAP_IMAGE, "rb") as f:
            await chat.send_photo(photo=f, caption=MAP_CAPTION, reply_markup=reply_markup or main_menu_inline())
    else:
        await chat.send_message("ПОКА ТУТ НИЧЕГО НЕТ (assets/map.jpg).", reply_markup=reply_markup or main_menu_inline())

# ---- отправка точки ----
async def send_point(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    if not (0 <= idx < len(POINTS)):
        return
    st = _state(context)
    st["idx"] = idx
    visited: Set[int] = st["visited"]  # type: ignore
    visited.add(idx)

    p = POINTS[idx]
    title = f"*{p['title']}*"
    body = p["text"]
    progress = f"\n\n_Прогресс: {len(visited)}/{len(POINTS)}_"

    # текст точки
    await update.effective_chat.send_message(
        text=f"{title}\n\n{body}{progress}",
        parse_mode="Markdown",
    )

    # фото (до 2 штук; если файла нет — пропускаем)
    photos = [ph for ph in p.get("photos", [])[:2] if isinstance(ph, Path) and ph.exists()]
    if photos:
        if len(photos) == 1:
            with open(photos[0], "rb") as f:
                await update.effective_chat.send_photo(photo=f)
        else:
            # media group требует байты
            media = []
            for ph in photos:
                with open(ph, "rb") as f:
                    media.append(InputMediaPhoto(media=f.read()))
            await update.effective_chat.send_media_group(media=media)

    is_last = (idx == len(POINTS) - 1)
    await update.effective_chat.send_message(
        "Навигация по маршруту:",
        reply_markup=point_nav_inline(is_last),
    )

# ---- хэндлеры команд ----
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем 2 аудио + текст с меню"""
    chat = update.effective_chat
    
    # Отправляем первое аудио
    if AUDIO1.exists():
        with open(AUDIO1, "rb") as f:
            await chat.send_audio(audio=f)
    else:
        await chat.send_message("⚠️ Аудио 1 не найдено (assets/audio1.ogg)")
    
    # Отправляем второе аудио
    if AUDIO2.exists():
        with open(AUDIO2, "rb") as f:
            await chat.send_audio(audio=f)
    else:
        await chat.send_message("⚠️ Аудио 2 не найдено (assets/audio2.ogg)")
    
    # Отправляем приветственное сообщение с меню
    welcome_text = "Готовы начать путь? Выберите один из вариантов:"
    await chat.send_message(welcome_text, reply_markup=welcome_menu_inline())

async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=welcome_menu_inline())

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, reply_markup=welcome_menu_inline())

# ---- хэндлеры кнопок ----
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # === ПЕРВОЕ МЕНЮ ===
    if data == CB_AUDIO_INFO:
        await q.message.reply_text(
            "Не забудь наушники, некоторые голоса долго ждали, чтобы быть услышанными",
            reply_markup=audio_submenu_inline()
        )
    
    elif data == CB_FEEDBACK:
        await q.message.reply_text(
            "Мы будем рады, если ты захочешь поделиться своими мыслями",
            reply_markup=feedback_submenu_inline()
        )
    
    elif data == CB_PROBLEMS:
        await q.message.reply_text(
            "Попробуй перезагрузить",
            reply_markup=welcome_menu_inline()
        )
    
    # === ПОДМЕНЮ ===
    elif data == CB_START_TOUR:
        # Начинаем экскурсию с точки 0
        st = _state(context)
        st["idx"] = 0
        st["visited"] = set()
        await send_point(update, context, 0)
    
    elif data == CB_WRITE_US:
        # Здесь можно добавить ссылку на форму или попросить написать сообщение
        await q.message.reply_text(
            "Напишите нам: [ваш email или ссылка на форму]\n\n"
            "Или отправьте сообщение прямо здесь, и мы его получим.",
            reply_markup=welcome_menu_inline()
        )
    
    elif data == CB_BACK_TO_MENU:
        await q.message.reply_text(
            "Главное меню:",
            reply_markup=welcome_menu_inline()
        )
    
    # === СТАРЫЕ КНОПКИ (оставляем для совместимости) ===
    elif data == CB_MENU_MAP:
        await send_map(q.message.chat, reply_markup=main_menu_inline())

    elif data == CB_MENU_START:
        st = _state(context)
        st["idx"] = 0
        st["visited"] = set()
        await send_point(update, context, 0)

    elif data == CB_MENU_ABOUT:
        await q.message.reply_text(ABOUT_TEXT, reply_markup=main_menu_inline())

    elif data == CB_NEXT:
        st = _state(context)
        idx = int(st.get("idx", 0))
        if idx >= len(POINTS) - 1:
            await q.message.reply_text(FINAL_MESSAGE, reply_markup=welcome_menu_inline())
        else:
            await send_point(update, context, idx + 1)

    elif data == CB_BACK_TO_MAP:
        await send_map(q.message.chat, reply_markup=main_menu_inline())

# На всякий случай: любой текст — показываем меню
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=welcome_menu_inline())

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    
    # Webhook вместо polling
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    main()
