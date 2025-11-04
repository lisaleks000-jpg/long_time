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
    "Привет! Это стартовый текст про бота\n\n"
    "Вот, что это за проект "
    "Вот, как пользоваться ботом\n\n"
    "🎧 Не забудьте наушники — некоторые голоса долго ждали, чтобы быть услышанными."
)

ABOUT_TEXT = (
    "📍 *О проекте*\n\n"
    "Этот маршрут создан, чтобы напомнить о женщинах, чьи истории были стёрты репрессиями. "
    "Мы проходим мимо этих мест каждый день, но редко задумываемся о том, что здесь происходило.\n\n"
    "Маршрут включает 9 домов Санкт-Петербурга\n\n"
    "Проект создан [кем?]."
)

HELP_TEXT = (
    "ℹ️ *Как пользоваться ботом:*\n\n"
    "• *Начать экскурсию* — бот проведёт вас последовательно по 9 точкам\n"
    "• *Карта маршрута* — посмотрите все точки на карте\n"
    "• *О проекте* — узнайте больше о замысле\n"
    "• *Обратная связь* — поделитесь впечатлениями\n\n"
    "Команды: /start, /menu, /help"
)

FINAL_MESSAGE = (
    "Спасибо, что прошли маршрут. 🙏\n\n"
    "Память держится на конкретных историях.\n\n"
    "💬 *Поделитесь впечатлениями* — нам важно ваше мнение."
)

ASSETS = Path("assets")
MAP_IMAGE = ASSETS / "map.jpg"
MAP_CAPTION = (
    "🗺️ *Карта маршрута*\n\n"
    "9 точек памяти в Санкт-Петербурге. "
    "Вы можете начать с первой — бот проведёт вас шаг за шагом."
)

# Аудио файлы для приветствия
AUDIO1 = ASSETS / "audio1.ogg"
AUDIO2 = ASSETS / "audio2.ogg"

# ---- Структура точек маршрута ----
POINTS = [
    # ===== ЛОКАЦИЯ 1 (БЕЗ навигационного фото, с двумя аудио) =====
    {
        "photo": ASSETS / "loc1_photo.jpg",  # Фото Анны Ахматовой
        "texts": [
            # Текст 1 (перед первым аудио)
            "Ленинград. Лето 1937 года. Это было давно.\n\n"
            "Историческая справка — начало «Большого террора» - приказ НКВД № 00447 — установление категорий мер наказания.\n\n"
            "Из приказа. Все репрессируемые кулаки, уголовники и др. антисоветские элементы разбиваются на две категории:\n"
            "а) к первой категории относятся все наиболее враждебные из перечисленных выше элементов. Они подлежат немедленному аресту и РАССТРЕЛУ.\n"
            "б) ко второй категории относятся все остальные менее активные, но все же враждебные элементы. Они подлежат аресту и заключению в лагеря на срок от 8 до 10 лет.",
            
            # Текст 2 (между аудио)
            "«Реквием» Анны Ахматовой был написан в 1935-1940-е годы, период террора. Это поэма о скорби, о личной трагедии Анны Ахматовой, о трагедии каждой женщины.\n\n"
            "В августе 1921 году по обвинению в «контрреволюционной деятельности» был арестован и расстрелян первый муж писательницы, Гумилев Николай Степанович. 30 сентября 1991 года посмертно реабилитирован, установлено, что уголовное дело было полностью сфальсифицировано.\n\n"
            "В октябре 1935 год был совершен первый арест сына Анны Ахматовой, Льва Николаевича Гумилева, дело было прекращено в том же году. В сентябре 1938 году Лев Гумилев был осужден по обвинению в контрреволюционной террористической деятельности на 10 лет исправительно-трудового лагеря, срок сокращен до 5 лет ИТЛ. Последний арест Льва Гумилева произошел в ноябре 1949 года, за антисоветскую агитацию и террористические намерения он был осужден на 10 лет исправительно- трудовой деятельности.\n\n"
            "Анна Ахматова провела 17 месяцев своей жизни в тюремных очередях, рядом с такими же матерями, женами и дочерьми.",
        ],
        "audio1": ASSETS / "loc1_audio1.ogg",
        "audio1_description": "🎧 «Реквием» Анны Ахматовой (часть 1)",
        "audio2": ASSETS / "loc1_audio2.ogg",
        "audio2_description": "🎧 «Реквием» Анны Ахматовой (часть 2)",
    },
    
    # ===== ЛОКАЦИЯ 2 =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 2]\n\n[краткое описание как добраться]",
        "nav_photo": ASSETS / "loc2_nav.jpg",  # Навигационное фото
        "photo": ASSETS / "loc2_photo.jpg",     # Фото Тамары Габбе
        "texts": [
            "Первое сообщение с информацией о точке 2...",
            "Второе сообщение с дополнительной информацией...",
        ],
        "audio": ASSETS / "loc2_audio.ogg",
        "audio_description": "🎧 История Тамары Габбе",
    },
    
    # ===== ЛОКАЦИЯ 3 (с кнопкой "узнать больше") =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 3]\n\n[краткое описание как добраться]",
        "nav_photo": ASSETS / "loc3_nav.jpg",  # Навигационное фото
        "photo": ASSETS / "loc3_photo.jpg",     # Фото Нины Маториной
        "texts": [
            "Первое сообщение с информацией о точке 3...",
            "Второе сообщение с дополнительной информацией...",
            "Третье сообщение (опционально)...",
        ],
        "audio": ASSETS / "loc3_audio.ogg",
        "audio_description": "🎧 История Нины Маториной",
    },
    
    # ===== ЛОКАЦИЯ 4 (БЕЗ АУДИО) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 4]\n\n[краткое описание как добраться]",
        "nav_photo": ASSETS / "loc4_nav.jpg",  # Навигационное фото
        "photo": ASSETS / "loc4_photo.jpg",     # Фото героини
        "texts": [
            "Первое сообщение с информацией о точке 4...",
            "Второе сообщение с дополнительной информацией...",
        ],
        "audio": None,
        "audio_description": None,
    },
    
    # ===== ЛОКАЦИЯ 5 (БЕЗ АУДИО, БЕЗ ФОТО ГЕРОИНИ) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 5]\n\n[краткое описание как добраться]",
        "nav_photo": ASSETS / "loc5_nav.jpg",  # Навигационное фото
        "photo": None,  # НЕТ фото героини!
        "texts": [
            "Первое сообщение с информацией о точке 5...",
            "Второе сообщение с дополнительной информацией...",
            "Третье сообщение (опционально)...",
        ],
        "audio": None,
        "audio_description": None,
    },
    
    # ===== ЛОКАЦИЯ 6 (с двумя аудио и кнопкой) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – [адрес точки 6]\n\n[краткое описание как добраться]",
        "nav_photo": ASSETS / "loc6_nav.jpg",  # Навигационное фото
        "photo": ASSETS / "loc6_photo.jpg",     # Фото Лидии Чуковской
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
        "audio_description": "🎧 История Лидии Чуковской",
        "extra_audio": ASSETS / "loc6_voice.ogg",
        "extra_audio_description": "🎧 Голос Лидии Чуковской",
    },
]

# ---- callback_data для кнопок ----
CB_START_TOUR = "start_tour"
CB_SHOW_MAP = "show_map"
CB_ABOUT = "about"
CB_FEEDBACK = "feedback"

CB_IM_HERE = "im_here"
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

FEEDBACK_URL = "https://t.me/lisaleksa"

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
        context.user_data["visited"] = set()
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

# ---- ЭТАП 1: Показываем адрес + навигационное фото + кнопка "Я тут" ----
async def send_point_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    """Отправляет адрес точки, навигационное фото (если есть) и кнопку 'Я тут'"""
    if not (0 <= idx < len(POINTS)):
        return
    
    st = _state(context)
    st["idx"] = idx

    point = POINTS[idx]
    chat = update.effective_chat
    
    progress = f"\n\n_Точка {idx + 1} из {len(POINTS)}_"
    
    # Если есть навигационное фото — отправляем его с текстом
    nav_photo = point.get("nav_photo")
    if nav_photo and nav_photo.exists():
        with open(nav_photo, "rb") as f:
            await chat.send_photo(
                photo=f,
                caption=point["navigation"] + progress,
                parse_mode="Markdown",
                reply_markup=im_here_button()
            )
    else:
        # Если нет навигационного фото — просто текст
        await chat.send_message(
            text=point["navigation"] + progress,
            parse_mode="Markdown",
            reply_markup=im_here_button()
        )

# ---- ЭТАП 2: После "Я тут" показываем всю информацию ----
async def send_point_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет контент точки после нажатия "Я тут":
    - Для локации 1: фото → текст1 → аудио1 → текст2 → аудио2 → навигация
    - Для остальных: стандартная логика
    """
    st = _state(context)
    idx = int(st.get("idx", 0))
    
    if not (0 <= idx < len(POINTS)):
        return
    
    visited: Set[int] = st["visited"]
    visited.add(idx)

    point = POINTS[idx]
    chat = update.effective_chat
    
    # ===== СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ЛОКАЦИИ 1 (индекс 0) =====
    if idx == 0:
        # 1. Фото героини
        photo_path = point.get("photo")
        if photo_path and photo_path.exists():
            with open(photo_path, "rb") as f:
                await chat.send_photo(photo=f)
        
        # 2. Текст 1
        texts = point.get("texts", [])
        if len(texts) > 0:
            await chat.send_message(text=texts[0], parse_mode="Markdown")
        
        # 3. Аудио 1
        audio1 = point.get("audio1")
        audio1_desc = point.get("audio1_description")
        if audio1 and audio1.exists():
            with open(audio1, "rb") as f:
                await chat.send_voice(voice=f)
            if audio1_desc:
                await chat.send_message(text=audio1_desc, parse_mode="Markdown")
        
        # 4. Текст 2
        if len(texts) > 1:
            await chat.send_message(text=texts[1], parse_mode="Markdown")
        
        # 5. Аудио 2
        audio2 = point.get("audio2")
        audio2_desc = point.get("audio2_description")
        if audio2 and audio2.exists():
            with open(audio2, "rb") as f:
                await chat.send_voice(voice=f)
            if audio2_desc:
                await chat.send_message(text=audio2_desc, parse_mode="Markdown")
        
        # 6. Навигация
        await chat.send_message(
            "👇 Навигация:",
            reply_markup=point_nav_inline(is_last=False)
        )
        return
    
    # ===== СТАНДАРТНАЯ ЛОГИКА ДЛЯ ОСТАЛЬНЫХ ЛОКАЦИЙ =====
    
    # 1. Отправляем фото героини (если есть)
    photo_path = point.get("photo")
    if photo_path and photo_path.exists():
        with open(photo_path, "rb") as f:
            await chat.send_photo(photo=f)
    elif photo_path:
        await chat.send_message(f"⚠️ Фото не найдено: {photo_path}")
    
    # 2. Отправляем текстовые сообщения
    texts: List[str] = point.get("texts", [])
    for text in texts:
        await chat.send_message(text=text, parse_mode="Markdown")
    
    # 3. СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ТОЧКИ 3 (индекс 2)
    if idx == 2:
        await chat.send_message(
            "❓ Узнать больше о этом месте?",
            reply_markup=want_more_buttons()
        )
        return
    
    # 3. СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ТОЧКИ 6 (индекс 5)
    if idx == 5:
        # Отправляем основное аудио
        audio_path = point.get("audio")
        audio_desc = point.get("audio_description")
        
        if audio_path and audio_path.exists():
            with open(audio_path, "rb") as f:
                await chat.send_voice(voice=f)
            if audio_desc:
                await chat.send_message(text=audio_desc, parse_mode="Markdown")
        
        # Спрашиваем про голос Лидии
        await chat.send_message(
            "❓ Хотите услышать её голос?",
            reply_markup=hear_voice_buttons()
        )
        return
    
    # 3. Для всех остальных точек — отправляем аудио как обычно
    audio_path = point.get("audio")
    audio_desc = point.get("audio_description")
    
    if audio_path and audio_path.exists():
        with open(audio_path, "rb") as f:
            await chat.send_voice(voice=f)
        
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
    point = POINTS[2]
    
    audio_path = point.get("audio")
    audio_desc = point.get("audio_description")
    
    if audio_path and audio_path.exists():
        with open(audio_path, "rb") as f:
            await chat.send_voice(voice=f)
        
        if audio_desc:
            await chat.send_message(text=audio_desc, parse_mode="Markdown")
    else:
        await chat.send_message(f"⚠️ Аудио не найдено: {audio_path}")
    
    await chat.send_message(
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last=False)
    )

# ---- Отправка дополнительного аудио для точки 6 после "Да" ----
async def send_point6_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет дополнительное аудио (голос) для точки 6"""
    chat = update.effective_chat
    point = POINTS[5]
    
    extra_audio = point.get("extra_audio")
    extra_desc = point.get("extra_audio_description")
    
    if extra_audio and extra_audio.exists():
        with open(extra_audio, "rb") as f:
            await chat.send_voice(voice=f)
        
        if extra_desc:
            await chat.send_message(text=extra_desc, parse_mode="Markdown")
    else:
        await chat.send_message(f"⚠️ Аудио не найдено: {extra_audio}")
    
    await chat.send_message(
        FINAL_MESSAGE,
        parse_mode="Markdown",
        reply_markup=final_menu_inline()
    )

# ---- хэндлеры команд ----
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем 2 аудио + приветственный текст + меню"""
    chat = update.effective_chat
    
    if AUDIO1.exists():
        with open(AUDIO1, "rb") as f:
            await chat.send_voice(voice=f)
    else:
        await chat.send_message("⚠️ Аудио 1 не найдено (assets/audio1.ogg)")
    
    if AUDIO2.exists():
        with open(AUDIO2, "rb") as f:
            await chat.send_voice(voice=f)
    else:
        await chat.send_message("⚠️ Аудио 2 не найдено (assets/audio2.ogg)")
    
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

    if data == CB_START_TOUR:
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
    
    elif data == CB_IM_HERE:
        await send_point_content(update, context)
    
    elif data == CB_WANT_MORE:
        await send_point3_audio(update, context)
    
    elif data == CB_SKIP_AUDIO:
        st = _state(context)
        idx = int(st.get("idx", 0))
        await send_point_navigation(update, context, idx + 1)
    
    elif data == CB_HEAR_VOICE_YES:
        await send_point6_voice(update, context)
    
    elif data == CB_HEAR_VOICE_NO:
        await q.message.reply_text(
            FINAL_MESSAGE,
            parse_mode="Markdown",
            reply_markup=final_menu_inline()
        )
    
    elif data == CB_NEXT:
        st = _state(context)
        idx = int(st.get("idx", 0))
        if idx >= len(POINTS) - 1:
            await q.message.reply_text(
                FINAL_MESSAGE,
                parse_mode="Markdown",
                reply_markup=final_menu_inline()
            )
        else:
            await send_point_navigation(update, context, idx + 1)
    
    elif data == CB_RESTART:
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
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    main()
