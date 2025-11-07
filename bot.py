# bot_webhook.py — версия для webhook (Render) с 9 локациями
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

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://long-time.onrender.com")
PORT = int(os.getenv("PORT", 8080))

# ---- Контент ----
PROJECT_NAME = "СПб: Женские истории репрессий"

WELCOME_TEXT = (
    "Готов ли ты услышать и сохранить в истории их голоса?"
)

ABOUT_TEXT = (
    "📍 *О проекте*\n\n"
    "Этот маршрут создан, чтобы напомнить о женщинах, чьи истории были стёрты репрессиями. "
    "Мы проходим мимо этих мест каждый день, но редко задумываемся о том, что здесь происходило.\n\n"
    "Маршрут включает 9 домов в Санкт-Петербурге.\n\n"
    "Команда проекта, это было давно!"
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

FINAL_TEXT = (
    "Спасибо большое, что были с нами, мы будем очень рады фидбеку. "
    "Также мы собрали для вас дополнительные материалы и тексты писем, которые зачитывали."
)

ASSETS = Path("assets")
MAP_IMAGE = ASSETS / "map.jpg"
MAP_CAPTION = (
    "🗺️ *Карта маршрута*\n\n"
    "9 точек памяти в Санкт-Петербурге. "
    "Вы можете начать с первой — бот проведёт вас шаг за шагом."
)

# Приветственные аудио
AUDIO1 = ASSETS / "audio1.ogg"
AUDIO2 = ASSETS / "audio2.ogg"

# Финальные файлы
FINAL_AUDIO = ASSETS / "final_audio.ogg"
FINAL_MATERIALS = ASSETS / "final_materials.pdf"

# ---- Структура точек маршрута ----
POINTS = [
    # ===== ЛОКАЦИЯ 1 (БЕЗ навигации, с двумя аудио) =====
    {
        "photo": ASSETS / "loc1_photo.jpg",
        "texts": [
            "Ленинград. Лето 1937 года. Это было давно.\n\n"
            "Историческая справка — начало «Большого террора» - приказ НКВД № 00447 — установление категорий мер наказания.\n\n"
            "Из приказа. Все репрессируемые кулаки, уголовники и др. антисоветские элементы разбиваются на две категории:\n"
            "а) к первой категории относятся все наиболее враждебные из перечисленных выше элементов. Они подлежат немедленному аресту и РАССТРЕЛУ.\n"
            "б) ко второй категории относятся все остальные менее активные, но все же враждебные элементы. Они подлежат аресту и заключению в лагеря на срок от 8 до 10 лет.",
            
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
        "nav_photo": ASSETS / "loc2_nav.jpg",
        "transition_text": "ПОКА ВЫ ИДЕТЕ НА СЛЕДУЮЩУЮ ЛОКАЦИЮ, ПРЕДЛАГАЕМ ВАМ ПОСЛУШАТЬ АУДИО",
        "transition_audio": ASSETS / "transition_1to2.ogg",
        "photo": ASSETS / "loc2_photo.jpg",
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
        "nav_photo": ASSETS / "loc3_nav.jpg",
        "photo": ASSETS / "loc3_photo.jpg",
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
        "nav_photo": ASSETS / "loc4_nav.jpg",
        "transition_text": "ПОКА ВЫ ИДЕТЕ НА СЛЕДУЮЩУЮ ЛОКАЦИЮ, ПРЕДЛАГАЕМ ВАМ ПОСЛУШАТЬ АУДИО",
        "transition_audio": ASSETS / "transition_3to4.ogg",
        "photo": ASSETS / "loc4_photo.jpg",
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
        "nav_photo": ASSETS / "loc5_nav.jpg",
        "photo": None,
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
        "nav_photo": ASSETS / "loc6_nav.jpg",
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
        "audio_description": "🎧 История Лидии Чуковской",
        "extra_audio": ASSETS / "loc6_voice.ogg",
        "extra_audio_description": "🎧 Голос Лидии Чуковской",
    },
    
    # ===== ЛОКАЦИЯ 7 (Мулло) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – Загородный проспект 24",
        "nav_photo": ASSETS / "nav_6to7.jpg",
        "photo": ASSETS / "loc7_photo.jpg",
        "texts": [
            "Мулло Елизавета Ивановна\n\n"
            "Елизавета Ивановна Мулло родилась в 1902 году в Новой деревне в большой семье финнов Анны Ивановны и Ивана Ивановича Мулло. Елизавета была старшей дочерью в семье, у нее было четыре сестры и четыре брата.\n\n"
            "Несмотря на то, что родители были крестьянами, Елизавета Ивановна получила высшее образование. Она окончила Педагогический институт им. Герцена по специальности «педагог» и с 1923 года работала в школе № 16 Володарского района Ленинграда.",
            
            "Из анкеты арестованной следует, что Елизавета Ивановна воспитывала сына Альберта, которому к моменту ее ареста было всего три года.\n\n"
            "В начале учебного года 5 сентября 1937 года Елизавета Ивановна была арестована ленинградским НКВД. Ее обвинили в «шпионаже, антисоветской пропаганде и организованной контрреволюционной деятельности». Комиссией НКВД и прокуратуры СССР 10 ноября 1937 года она была приговорена к расстрелу и 15 ноября 1937 года расстреляна в Ленинграде. Ей было 35 лет.\n\n"
            "Елизавета Ивановна Мулло была реабилитирована в 1989 году.",
        ],
        "audio": None,
    },
    
    # ===== ЛОКАЦИЯ 8 (Одинцова) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – Загородный проспект, 28",
        "nav_photo": ASSETS / "nav_7to8.jpg",
        "transition_text": "ПОКА ВЫ ИДЕТЕ НА СЛЕДУЮЩУЮ ЛОКАЦИЮ, ПРЕДЛАГАЕМ ВАМ ПОСЛУШАТЬ АУДИО",
        "transition_audio": ASSETS / "transition_7to8.ogg",
        "photo": ASSETS / "loc8_photo.jpg",
        "texts": [
            "Одинцова Елена Андреевна\n\n"
            "В квартире по этому адресу проживала большая семья Дитерихс-Одинцовых.\n\n"
            "Воспоминания Ирины Кирилловны Одинцовой, дочери Елены Андреевной: «Моя мама была домохозяйкой и воспитывала меня. Мама рисовала, сама искусно изготавливала кукол, шила им платья, мастерила им шляпки из соломки и продавала, чтобы подработать»",
            
            "Елена Андреевна Одинцова была арестована в Ленинграде 26 октября 1937 года как член Российского общевоинского союза. Эту организацию, никогда не существовавшую, придумали сотрудники НКВД.\n\n"
            "Елену Андреевну расстреляли 8 января 1938 года по так называемому списку № 2 шпионов – членов Российского общевоинского союза. В предписании на расстрел ее имя значится 41-м из 50 приговоренных к высшей мере наказания.\n\n"
            "Помимо Елены Андреевны, четыре члена семьи Дитерихс-Одинцовых были убиты во времена советского государственного террора: Андрей Павлович Дитерихс, Дмитрий Павлович Дитерихс, Павел Андреевич Дитерихс, Кирилл Сергеевич Одинцов.\n\n"
            "Дела членов семьи были пересмотрены по всем приговорам – вся семья Дитерихс (Одинцовых) была полностью реабилитирована.",
        ],
        "audio": None,
        "optional_audio": ASSETS / "loc8_audio.ogg",
        "optional_question": "ХОТЕЛИ БЫ ВЫ УСЛЫШАТЬ ВОСПОМИНАНИЯ ИРИНЫ КИРИЛЛОВНЫ, ДОЧЕРИ ЕЛЕНЫ АНДРЕЕВНЫ ОДИНЦОВОЙ, ОБ АРЕСТЕ РЕПРЕССИРОВАННОЙ?",
    },
    
    # ===== ЛОКАЦИЯ 9 (Любарская) =====
    {
        "navigation": "📍 Теперь тебе нужно добраться сюда – Набережная реки Фонтанки, 78",
        "nav_photo": ASSETS / "nav_8to9.jpg",
        "photo": ASSETS / "loc9_photo.jpg",
        "texts": [
            "Любарская Александра Иосифовна\n\n"
            "Александра Иосифовна родилась в 1908 году в Ленинграде. В 1924 году окончила Петроградскую 10-ю Единую Трудовую школу имени Лидии Даниловны Лентовской, в этот же год поступила на Высшие государственные курсы искусствоведения, которые окончила в 1930-м году и получила звание литературоведа.\n\n"
            "В Леногизе начала работать в 1930 году редактором детского отдела, возглавляемого С.Я. Маршаком. Этот отдел позднее развился в издательство – Ленинградское отделение Детгиза.\n\n"
            "В 1935-1937 годах многие сотрудники редакции были арестованы, включая Александру Любарскую и Тамару Габбе.",
            
            "Александра Иосифовна была арестована 5 сентября 1937 г. и внесена в список № 10 «Харбинцы» с ходатайством о высшей мере наказания как участнице «троцкистской шпионской группы, связанной с японской разведкой».\n\n"
            "Комиссией НКВД и Прокуратуры СССР 3 декабря 1937 г. принято решение предать Любарскую суду Военной коллегии Верховного суда СССР. Дело готовили для рассмотрения Военным трибуналом ЛВО, затем Особым совещанием при НКВД СССР. Благодаря упорству Любарской и ее заявлениям в Прокуратуру о действиях следователя П. А. Слепнева осуждение не состоялось. Благодаря заступничеству К. И. Чуковского и С. Я. Маршака в декабре 1938 г. Александара Иосифовна была освобождена 14 января 1939 г.\n\n"
            "Александра Любарская в своих воспоминаниях \"За тюремной стеной\" описала опыт нахождения в Большом Доме. Так называли здание Управления НКВД на Литейном проспекте, 4. Писательница провела в нем почти полтора года. В воспоминаниях она рассказывала не только о своем опыты, но и опыте своих сокамерниц.",
        ],
        "audio": None,
        "optional_audio": ASSETS / "loc9_audio.ogg",
        "optional_question": "ХОТЕЛИ БЫ ВЫ УСЛЫШАТЬ ОТРЫВОК ИЗ ВОСПОМИНАНИЙ АЛЕКСАНДРЫ ЛЮБАРСКОЙ?",
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

CB_WANT_MORE = "want_more_yes"
CB_SKIP_AUDIO = "skip_audio_no"

CB_HEAR_VOICE_YES = "hear_voice_yes"
CB_HEAR_VOICE_NO = "hear_voice_no"

FEEDBACK_URL = "https://t.me/lisaleksa"

# ---- Разметка кнопок ----

def main_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Начать экскурсию", callback_data=CB_START_TOUR)],
            [InlineKeyboardButton("🗺️ Карта маршрута", callback_data=CB_SHOW_MAP)],
            [InlineKeyboardButton("ℹ️ О проекте", callback_data=CB_ABOUT)],
            [InlineKeyboardButton("💬 Обратная связь", url=FEEDBACK_URL)],
        ]
    )

def help_menu_inline() -> InlineKeyboardMarkup:
    """Меню после приветствия"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Начать экскурсию", callback_data=CB_START_TOUR)],
            [InlineKeyboardButton("💬 Обратная связь", url=FEEDBACK_URL)],
        ]
    )

def im_here_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Я тут", callback_data=CB_IM_HERE)],
            [InlineKeyboardButton("🗺️ Карта", callback_data=CB_BACK_TO_MAP)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

def want_more_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Да", callback_data=CB_WANT_MORE)],
            [InlineKeyboardButton("➡️ Нет, пропустить", callback_data=CB_SKIP_AUDIO)],
        ]
    )

def hear_voice_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Да, хочу услышать", callback_data=CB_HEAR_VOICE_YES)],
            [InlineKeyboardButton("➡️ Нет, завершить", callback_data=CB_HEAR_VOICE_NO)],
        ]
    )

def point_nav_inline(is_last: bool) -> InlineKeyboardMarkup:
    first_row_text = "✅ Завершить маршрут" if is_last else "Следующая точка →"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(first_row_text, callback_data=CB_NEXT)],
            [InlineKeyboardButton("🗺️ Карта", callback_data=CB_BACK_TO_MAP)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

def final_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💬 Оставить отзыв", url=FEEDBACK_URL)],
            [InlineKeyboardButton("🔄 Пройти заново", callback_data=CB_RESTART)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=CB_BACK_TO_MENU)],
        ]
    )

def _state(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "idx" not in context.user_data:
        context.user_data["idx"] = 0
    if "visited" not in context.user_data:
        context.user_data["visited"] = set()
    if "waiting_optional" not in context.user_data:
        context.user_data["waiting_optional"] = False
    return context.user_data

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

async def send_point_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    """Отправляет адрес точки, навигационное фото (если есть) и кнопку 'Я тут'"""
    if not (0 <= idx < len(POINTS)):
        return
    
    st = _state(context)
    st["idx"] = idx
    st["waiting_optional"] = False

    point = POINTS[idx]
    chat = update.effective_chat
    
    # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ЛОКАЦИИ 1
    if idx == 0:
        await send_point_content(update, context)
        return
    
    # ДЛЯ ОСТАЛЬНЫХ ЛОКАЦИЙ
    progress = f"\n\n_Точка {idx + 1} из {len(POINTS)}_"
    
    nav_photo = point.get("nav_photo")
    navigation_text = point.get("navigation", "📍 Следующая точка")
    
    # 1. Навигационное фото с адресом
    if nav_photo and nav_photo.exists():
        with open(nav_photo, "rb") as f:
            await chat.send_photo(
                photo=f,
                caption=navigation_text + progress,
                parse_mode="Markdown"
            )
    else:
        await chat.send_message(
            text=navigation_text + progress,
            parse_mode="Markdown"
        )
    
    # 2. Переходное аудио (если есть)
    transition_text = point.get("transition_text")
    transition_audio = point.get("transition_audio")
    
    if transition_text:
        await chat.send_message(text=transition_text)
    
    if transition_audio and transition_audio.exists():
        with open(transition_audio, "rb") as f:
            await chat.send_voice(voice=f)
    
    # 3. Кнопка "Я тут"
    await chat.send_message(
        "Нажми, когда доберёшься:",
        reply_markup=im_here_button()
    )

async def send_point_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = _state(context)
    idx = int(st.get("idx", 0))
    
    if not (0 <= idx < len(POINTS)):
        return
    
    visited: Set[int] = st["visited"]
    visited.add(idx)

    point = POINTS[idx]
    chat = update.effective_chat
    
    # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ЛОКАЦИИ 1
    if idx == 0:
        photo_path = point.get("photo")
        if photo_path and photo_path.exists():
            with open(photo_path, "rb") as f:
                await chat.send_photo(photo=f)
        
        texts = point.get("texts", [])
        if len(texts) > 0:
            await chat.send_message(text=texts[0], parse_mode="Markdown")
        
        audio1 = point.get("audio1")
        audio1_desc = point.get("audio1_description")
        if audio1 and audio1.exists():
            with open(audio1, "rb") as f:
                await chat.send_voice(voice=f)
            if audio1_desc:
                await chat.send_message(text=audio1_desc, parse_mode="Markdown")
        
        if len(texts) > 1:
            await chat.send_message(text=texts[1], parse_mode="Markdown")
        
        audio2 = point.get("audio2")
        audio2_desc = point.get("audio2_description")
        if audio2 and audio2.exists():
            with open(audio2, "rb") as f:
                await chat.send_voice(voice=f)
            if audio2_desc:
                await chat.send_message(text=audio2_desc, parse_mode="Markdown")
        
        await chat.send_message(
            "👇 Навигация:",
            reply_markup=point_nav_inline(is_last=False)
        )
        return
    
    # СТАНДАРТНАЯ ЛОГИКА ДЛЯ ОСТАЛЬНЫХ ЛОКАЦИЙ
    
    photo_path = point.get("photo")
    if photo_path and photo_path.exists():
        with open(photo_path, "rb") as f:
            await chat.send_photo(photo=f)
    elif photo_path:
        await chat.send_message(f"⚠️ Фото не найдено: {photo_path}")
    
    texts: List[str] = point.get("texts", [])
    for text in texts:
        await chat.send_message(text=text, parse_mode="Markdown")
    
    # Логика для локации 3 (узнать больше)
    if idx == 2:
        await chat.send_message(
            "❓ Узнать больше о этом месте?",
            reply_markup=want_more_buttons()
        )
        return
    
    # Логика для локации 6 (голос Лидии)
    if idx == 5:
        audio_path = point.get("audio")
        audio_desc = point.get("audio_description")
        
        if audio_path and audio_path.exists():
            with open(audio_path, "rb") as f:
                await chat.send_voice(voice=f)
            if audio_desc:
                await chat.send_message(text=audio_desc, parse_mode="Markdown")
        
        await chat.send_message(
            "❓ Хотите услышать её голос?",
            reply_markup=hear_voice_buttons()
        )
        return
    
    # Обычное аудио
    audio_path = point.get("audio")
    audio_desc = point.get("audio_description")
    
    if audio_path and audio_path.exists():
        with open(audio_path, "rb") as f:
            await chat.send_voice(voice=f)
        
        if audio_desc:
            await chat.send_message(text=audio_desc, parse_mode="Markdown")
    elif audio_path:
        await chat.send_message(f"⚠️ Аудио не найдено: {audio_path}")
    
    # Проверка на опциональное аудио (для локаций 8 и 9)
    optional_audio = point.get("optional_audio")
    optional_question = point.get("optional_question")
    
    if optional_audio and optional_question:
        st["waiting_optional"] = True
        await chat.send_message(
            optional_question,
            reply_markup=want_more_buttons()
        )
        return
    
    # Навигация
    is_last = (idx == len(POINTS) - 1)
    await chat.send_message(
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last),
    )

async def send_point3_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Для локации 3 - старая логика"""
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

async def send_optional_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет опциональное аудио для локаций 8 и 9"""
    st = _state(context)
    idx = int(st.get("idx", 0))
    
    if not (0 <= idx < len(POINTS)):
        return
    
    point = POINTS[idx]
    chat = update.effective_chat
    
    optional_audio = point.get("optional_audio")
    
    if optional_audio and optional_audio.exists():
        with open(optional_audio, "rb") as f:
            await chat.send_voice(voice=f)
    
    st["waiting_optional"] = False
    
    is_last = (idx == len(POINTS) - 1)
    await chat.send_message(
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last),
    )

async def send_point6_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "👇 Навигация:",
        reply_markup=point_nav_inline(is_last=False)
    )

async def send_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет финальное сообщение с аудио, текстом и файлом"""
    chat = update.effective_chat
    
    # 1. Финальное аудио
    if FINAL_AUDIO.exists():
        await chat.send_message("Наш маршрут подошел к завершению. Прослушайте финальные записи")
        with open(FINAL_AUDIO, "rb") as f:
            await chat.send_voice(voice=f)
    
    # 2. Финальный текст  
    await chat.send_message(
        FINAL_TEXT,
        parse_mode="Markdown"
    )
    
    # 3. Файл с материалами
    if FINAL_MATERIALS.exists():
        with open(FINAL_MATERIALS, "rb") as f:
            await chat.send_document(
                document=f,
                caption="📎 Дополнительные материалы и тексты писем"
            )
    
    # 4. Меню
    await chat.send_message(
        "Команда проекта, это было давно!",
        reply_markup=final_menu_inline()
    )

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    if AUDIO1.exists():
        with open(AUDIO1, "rb") as f:
            await chat.send_voice(voice=f)
    
    if AUDIO2.exists():
        with open(AUDIO2, "rb") as f:
            await chat.send_voice(voice=f)
    
    await chat.send_message(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=help_menu_inline()
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

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    
    st = _state(context)

    if data == CB_START_TOUR:
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
        idx = int(st.get("idx", 0))
        
        # Для локации 3 - старая логика
        if idx == 2:
            await send_point3_audio(update, context)
        # Для локаций 8 и 9 - новая логика
        else:
            await send_optional_audio(update, context)
    
    elif data == CB_SKIP_AUDIO:
        st = _state(context)
        idx = int(st.get("idx", 0))
        st["waiting_optional"] = False
        
        if idx >= len(POINTS) - 1:
            await send_final(update, context)
        else:
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
            await send_final(update, context)
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
