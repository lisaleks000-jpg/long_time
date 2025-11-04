# bot_webhook.py — версия для webhook (Render)
from pathlib import Path
from typing import Set, List, Optional

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

# URL вашего приложения на Render
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://long-time.onrender.com")
PORT = int(os.getenv("PORT", 8080))

# ---- Контент ----
PROJECT_NAME = "СПб: Женские истории репрессий"

WELCOME_TEXT = (
    "Добро пожаловать! Этот бот — короткая и бережная прогулка по Санкт-Петербургу.\n\n"
    "Мы предлагаем 6 точек памяти о женщинах, пострадавших от репрессий. "
    "Каждая точка — это место, факт и несколько строк, помогающих увидеть город иначе.\n\n"
    "🎧 Не забудьте наушники — некоторые голоса долго ждали, чтобы быть услышанными."
)

ABOUT_TEXT = (
    "📍 *О проекте*\n\n"
    "Этот маршрут создан, чтобы напомнить о женщинах, чьи истории были стёрты репрессиями. "
    "Мы проходим мимо этих мест каждый день, но редко задумываемся о том, что здесь происходило.\n\n"
    "Маршрут включает 6 точек в Санкт-Петербурге. Каждая — это конкретная история, конкретная судьба.\n\n"
    "Проект создан [название вашей организации/инициативы]."
)

HELP_TEXT = (
    "ℹ️ *Как пользоваться ботом:*\n\n"
    "• *Начать экскурсию* — бот проведёт вас последовательно по 6 точкам\n"
    "• *Карта маршрута* — посмотрите все точки на карте\n"
    "• *О проекте* — узнайте больше о замысле\n"
    "• *Обратная связь* — поделитесь впечатлениями\n\n"
    "Команды: /start, /menu, /help"
)

FINAL_MESSAGE = (
    "Спасибо, что прошли маршрут. 🙏\n\n"
    "Память держится на конкретных историях — иногда тихие знаки рядом с нами значат больше слов.\n\n"
    "💬 *Поделитесь впечатлениями* — нам важно ваше мнение."
)

ASSETS = Path("assets")
MAP_IMAGE = ASSETS / "map.jpg"
MAP_CAPTION = (
    "🗺️ *Карта маршрута*\n\n"
    "6 точек памяти в Санкт-Петербурге. "
    "Вы можете начать с первой — бот проведёт вас шаг за шагом."
)

# Аудио файлы для приветствия
AUDIO1 = ASSETS / "audio1.ogg"
AUDIO2 = ASSETS / "audio2.ogg"

# ---- Структура точек маршрута ----
POINTS = [
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 1]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc1_photo.jpg",
        "texts": [
            "Первое сообщение с информацией о точке 1...",
            "Второе сообщение с дополнительной информацией...",
            "Третье сообщение (опционально)...",
        ],
        "audio": ASSETS / "loc1_audio.ogg",
        "audio_description": "🎧 В этом аудио: [краткое описание содержания аудио для точки 1]",
    },
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 2]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc2_photo.jpg",
        "texts": [
            "Первое сообщение с информацией о точке 2...",
            "Второе сообщение с дополнительной информацией...",
        ],
        "audio": ASSETS / "loc2_audio.ogg",
        "audio_description": "🎧 В этом аудио: [краткое описание содержания аудио для точки 2]",
    },
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 3]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc3_photo.jpg",
        "texts": [
            "Первое сообщение с информацией о точке 3...",
            "Второе сообщение с дополнительной информацией...",
            "Третье сообщение (опционально)...",
        ],
        "audio": ASSETS / "loc3_audio.ogg",
        "audio_description": "🎧 В этом аудио: [краткое описание содержания аудио для точки 3]",
    },
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 4]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc4_photo.jpg",
        "texts": [
            "Первое сообщение с информацией о точке 4...",
            "Второе сообщение с дополнительной информацией...",
        ],
        "audio": None,  # Точка 4 — БЕЗ аудио
        "audio_description": None,
    },
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 5]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc5_photo.jpg",
        "texts": [
            "Первое сообщение с информацией о точке 5...",
            "Второе сообщение с дополнительной информацией...",
            "Третье сообщение (опционально)...",
        ],
        "audio": None,  # Точка 5 — БЕЗ аудио
        "audio_description": None,
    },
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 6]\n\n[краткое описание как добраться]",
        "photo": ASSETS / "loc6_photo.jpg",
        "texts": [
            "Лидия Чуковская родилась 11/24 марта 1907 года в Петербурге в семье писателей Корнея Чуковского. "
            "Лидия Корнеевна получила прекрасное образование в частной женской гимназии Таганцевой, позднее в 15-ой единой "
            "трудовой школе, а затем она поступила и окончила отделение курсов при Институте истории искусств. Благодаря "
            "литературной деятельности отца, Чуковская с юности была знакома с выдающимися деятелями культуры: Ахматовой, "
            "Мандельштамом, Блоком, Гумилёвым и другими.",
            
            "Летом 1926 года Лидия была арестована по подозрению в составлении антисоветской листовки, по приговору "
            "суду была сослана в Саратов.\n\n"
            "В 1933 она находит замуж за Матвея Бронштейна, физика-теоретика, занимавшегося научной деятельностью и "
            "популяризацией науки. В начале 1935 года \"органы\" вызвали Лидию Корнееву с требованием и угпузы за "
            "досрочное освобождение на ссылку стать сотрудницей НКВД, несмотря угрозы, она не согласилась.",
            
            "В августе 1937 года был арестован Матвей Бронштейн. С ордером на арест Лидии Чуковской приходили на "
            "Загородный проспект 11, но её удалось скрыться.",
        ],
        "audio": ASSETS / "loc6_audio.ogg",
        "audio_description": "🎧 В этом аудио: [краткое описание содержания аудио для точки 6]",
        "extra_audio": ASSETS / "loc6_voice.ogg",  # Голос Лидии Чуковской
        "extra_audio_description": "🎧 Голос Лидии Чуковской",
    },
]

# ---- callback_data для кнопок ----
CB_START_TOUR = "start_tour"
CB_SHOW_MAP = "show_map"
CB_ABOUT = "about"
CB_FEEDBACK = "feedback"

CB_IM_HERE = "im_here"  # Кнопка "Я тут"
CB_NEXT = "nav_next"
CB_RESTART = "restart_tour"
CB_BACK_TO_MAP = "nav_map"
CB_BACK_TO_MENU = "nav_menu"

# Для точки 3 — "узнать больше"
CB_WANT_MORE = "want_more_yes"
CB_SKIP_AUDIO = "skip_audio_no"

# Для точки 6 — "услышать её голос"
CB_HEAR_VOICE_YES = "hear_voice_yes"
CB_HEAR_VOICE_NO = "hear_voice_no"

# Вставьте сюда ваш Telegram username или ссылку для обратной связи
FEEDBACK_URL = "https://t.me/lisaleksa"  # ← ЗАМЕНИТЕ!

# ---- Разметка кнопок ----

def main_menu_inline() -> InlineKeyboardMarkup:
    """Главное меню — 4 кнопки"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Начать экскурсию", callback_data=CB_START_TOUR)],
            [InlineKeyboardButton("🗺️ Карта маршрута", callback_data=CB_SHOW_MAP)],
            [InlineKeyboardButton("ℹ️ О проекте", callback_data=CB_ABOUT)],
            [InlineKeyboardButton("💬 Обратная связь", url=FEEDBACK_URL)],
        ]
    )

def im_here_button() -> InlineKeyboardMarkup:
    """Кнопка 'Я тут' — показывается после адреса"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Я тут", callback_data=CB_IM_HERE)],
            [InlineKeyboardButton("🗺️ Карта", callback_data=CB_BACK_TO_MAP)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

def want_more_buttons() -> InlineKeyboardMarkup:
    """Кнопки 'узнать больше?' для точки 3"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Да", callback_data=CB_WANT_MORE)],
            [InlineKeyboardButton("➡️ Нет, пропустить", callback_data=CB_SKIP_AUDIO)],
        ]
    )

def hear_voice_buttons() -> InlineKeyboardMarkup:
    """Кнопки 'хотите услышать её голос?' для точки 6"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Да, хочу услышать", callback_data=CB_HEAR_VOICE_YES)],
            [InlineKeyboardButton("➡️ Нет, завершить", callback_data=CB_HEAR_VOICE_NO)],
        ]
    )

def point_nav_inline(is_last: bool) -> InlineKeyboardMarkup:
    """Навигация после просмотра точки"""
    first_row_text = "✅ Завершить маршрут" if is_last else "Следующая точка →"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(first_row_text, callback_data=CB_NEXT)],
            [InlineKeyboardButton("🗺️ Карта", callback_data=CB_BACK_TO_MAP)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

def final_menu_inline() -> InlineKeyboardMarkup:
    """Меню после завершения маршрута"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💬 Оставить отзыв", url=FEEDBACK_URL)],
            [InlineKeyboardButton("🔄 Пройти заново", callback_data=CB_RESTART)],
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
            await chat.send_photo(
                photo=f, 
                caption=MAP_CAPTION,
                parse_mode="Markdown",
                reply_markup=reply_markup or main_menu_inline()
            )
    else:
        await chat.send_message(
            "⚠️ Карта пока не загружена (assets/map.jpg)",
            reply_markup=reply_markup or main_menu_inline()
        )

# ---- ЭТАП 1: Показываем адрес + кнопка "Я тут" ----
async def send_point_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    """
    Отправляет только адрес точки и кнопку "Я тут"
    """
    if not (0 <= idx < len(POINTS)):
        return
    
    st = _state(context)
    st["idx"] = idx

    point = POINTS[idx]
    chat = update.effective_chat
    
    # Отправляем навигацию с прогрессом
    progress = f"\n\n_Точка {idx + 1} из {len(POINTS)}_"
    await chat.send_message(
        text=point["navigation"] + progress,
        parse_mode="Markdown",
        reply_markup=im_here_button()
    )

# ---- ЭТАП 2: После "Я тут" показываем всю информацию ----
async def send_point_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет контент точки после нажатия "Я тут":
    1. Фото
    2. Текстовые сообщения (2-3 штуки)
    3. Аудио + описание (с условиями для точек 3 и 6)
    4. Кнопки навигации
    """
    st = _state(context)
    idx = int(st.get("idx", 0))
    
    if not (0 <= idx < len(POINTS)):
        return
    
    visited: Set[int] = st["visited"]  # type: ignore
    visited.add(idx)

    point = POINTS[idx]
    chat = update.effective_chat
    
    # 1. Отправляем фото
    photo_path = point.get("photo")
    if photo_path and photo_path.exists():
        with open(photo_path, "rb") as f:
            await chat.send_photo(photo=f)
    else:
        await chat.send_message(f"⚠️ Фото не найдено: {photo_path}")
    
    # 2. Отправляем текстовые сообщения
    texts: List[str] = point.get("texts", [])
    for text in texts:
        await chat.send_message(text=text, parse_mode="Markdown")
    
    # 3. СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ТОЧКИ 3 (индекс 2)
    if idx == 2:  # Точка 3
        # Спрашиваем "узнать больше?"
        await chat.send_message(
            "❓ Узнать больше о этом месте?",
            reply_markup=want_more_buttons()
        )
        return  # НЕ отправляем аудио здесь! Оно отправится после нажатия "Да"
    
    # 3. СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ТОЧКИ 6 (индекс 5)
    if idx == 5:  # Точка 6 (последняя)
        # Отправляем основное аудио
        audio_path = point.get("audio")
        audio_desc = point.get("audio_description")
        
        if audio_path and audio_path.exists():
            with open(audio_path, "rb") as f:
                await chat.send_audio(audio=f)
            if audio_desc:
                await chat.send_message(text=audio_desc, parse_mode="Markdown")
        
        # Спрашиваем про голос Лидии
        await chat.send_message(
            "❓ Хотите услышать её голос?",
            reply_markup=hear_voice_buttons()
        )
        return  # Не показываем навигацию
    
    # 3. Для всех остальных точек — отправляем аудио как обычно
    audio_path = point.get("audio")
    audio_desc = point.get("audio_description")
    
    if audio_path and audio_path.exists():
        with open(audio_path, "rb") as f:
            await chat.send_audio(audio=f)
        
        if audio_desc:
            await chat.send_message(text=audio_desc, parse_mode="Markdown")
    elif audio_path:
        await chat.send_message(f"⚠️ Аудио не найдено: {audio_path}")
    
    # 4. Кнопки навигации
    is_last = (idx == len(POINTS) - 1)
    await chat.send_message(
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last),
    )

# ---- Отправка аудио для точки 3 после "Да" ----
async def send_point3_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет аудио для точки 3 после нажатия 'Да'"""
    chat = update.effective_chat
    point = POINTS[2]  # Точка 3 (индекс 2)
    
    # Отправляем аудио
    audio_path = point.get("audio")
    audio_desc = point.get("audio_description")
    
    if audio_path and audio_path.exists():
        with open(audio_path, "rb") as f:
            await chat.send_audio(audio=f)
        
        if audio_desc:
            await chat.send_message(text=audio_desc, parse_mode="Markdown")
    else:
        await chat.send_message(f"⚠️ Аудио не найдено: {audio_path}")
    
    # Показываем навигацию
    await chat.send_message(
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last=False)  # Точка 3 не последняя
    )

# ---- Отправка дополнительного аудио для точки 6 после "Да" ----
async def send_point6_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет дополнительное аудио (голос) для точки 6"""
    chat = update.effective_chat
    point = POINTS[5]  # Точка 6 (индекс 5)
    
    # Отправляем дополнительное аудио
    extra_audio = point.get("extra_audio")
    extra_desc = point.get("extra_audio_description")
    
    if extra_audio and extra_audio.exists():
        with open(extra_audio, "rb") as f:
            await chat.send_audio(audio=f)
        
        if extra_desc:
            await chat.send_message(text=extra_desc, parse_mode="Markdown")
    else:
        await chat.send_message(f"⚠️ Аудио не найдено: {extra_audio}")
    
    # Завершаем маршрут
    await chat.send_message(
        FINAL_MESSAGE,
        parse_mode="Markdown",
        reply_markup=final_menu_inline()
    )

# ---- хэндлеры команд ----
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем 2 аудио + приветственный текст + меню"""
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
    await chat.send_message(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=main_menu_inline()
    )

async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Главное меню:",
        reply_markup=main_menu_inline()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=main_menu_inline()
    )

# ---- хэндлеры кнопок ----
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # === ГЛАВНОЕ МЕНЮ ===
    if data == CB_START_TOUR:
        # Начинаем экскурсию с точки 0 — показываем только адрес
        st = _state(context)
        st["idx"] = 0
        st["visited"] = set()
        await send_point_navigation(update, context, 0)
    
    elif data == CB_SHOW_MAP:
        await send_map(q.message.chat, reply_markup=main_menu_inline())
    
    elif data == CB_ABOUT:
        await q.message.reply_text(
            ABOUT_TEXT,
            parse_mode="Markdown",
            reply_markup=main_menu_inline()
        )
    
    # === КНОПКА "Я ТУТ" ===
    elif data == CB_IM_HERE:
        # Пользователь на месте — показываем контент точки
        await send_point_content(update, context)
    
    # === КНОПКИ "УЗНАТЬ БОЛЬШЕ?" ДЛЯ ТОЧКИ 3 ===
    elif data == CB_WANT_MORE:
        # Пользователь хочет узнать больше — отправляем аудио
        await send_point3_audio(update, context)
    
    elif data == CB_SKIP_AUDIO:
        # Пользователь пропускает — сразу на следующую точку
        st = _state(context)
        idx = int(st.get("idx", 0))
        await send_point_navigation(update, context, idx + 1)
    
    # === КНОПКИ "ХОТИТЕ УСЛЫШАТЬ ЕЁ ГОЛОС?" ДЛЯ ТОЧКИ 6 ===
    elif data == CB_HEAR_VOICE_YES:
        # Пользователь хочет услышать голос — отправляем дополнительное аудио
        await send_point6_voice(update, context)
    
    elif data == CB_HEAR_VOICE_NO:
        # Пользователь пропускает — завершаем маршрут
        await q.message.reply_text(
            FINAL_MESSAGE,
            parse_mode="Markdown",
            reply_markup=final_menu_inline()
        )
    
    # === НАВИГАЦИЯ ПО ТОЧКАМ ===
    elif data == CB_NEXT:
        st = _state(context)
        idx = int(st.get("idx", 0))
        if idx >= len(POINTS) - 1:
            # Завершение маршрута
            await q.message.reply_text(
                FINAL_MESSAGE,
                parse_mode="Markdown",
                reply_markup=final_menu_inline()
            )
        else:
            # Следующая точка — показываем адрес
            await send_point_navigation(update, context, idx + 1)
    
    elif data == CB_RESTART:
        # Пройти маршрут заново
        st = _state(context)
        st["idx"] = 0
        st["visited"] = set()
        await send_point_navigation(update, context, 0)
    
    elif data == CB_BACK_TO_MAP:
        await send_map(q.message.chat, reply_markup=main_menu_inline())
    
    elif data == CB_BACK_TO_MENU:
        await q.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=main_menu_inline()
        )

# На всякий случай: любой текст — показываем меню
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Главное меню:",
        reply_markup=main_menu_inline()
    )

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
