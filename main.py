from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "7113984877:AAEydlvWVX0rwUy8ZLkrFXSEg4sjO-dGuO4"
ADMIN_USER_ID = 6651180345
CHANNEL_ID = "@GoatBall_ir"

teams = {}
TEAM_CAPACITY = 1  # هر تیم فقط یک نفر می‌تواند داشته باشد
waiting_for_interview = set()  # مجموعه کاربرانی که منتظر ارسال مصاحبه هستند
waiting_for_lineup = set()  # مجموعه کاربرانی که منتظر ارسال ترکیب هستند
pending_interviews = {}  # مصاحبه‌های منتظر تایید {message_id: {user_id, team_name, interview_text}}
waiting_for_team_message = set()  # کاربرانی که منتظر ارسال پیام به تیم هستند
pending_match_requests = {}  # درخواست‌های بازی منتظر تایید {message_id: {sender_user_id, target_team, sender_team}}
friendly_match_messages = {}  # پیام‌های درخواست بازی دوستانه {sender_user_id: [list of (chat_id, message_id)]}

COUNTRIES = [
    {"code": "BR", "name": "🇧🇷 Brazil"},
    {"code": "DE", "name": "🇩🇪 Germany"},
    {"code": "FR", "name": "🇫🇷 France"},
    {"code": "AR", "name": "🇦🇷 Argentina"},
    {"code": "ES", "name": "🇪🇸 Spain"},
    {"code": "IT", "name": "🇮🇹 Italy"},
    {"code": "GB", "name": "🇬🇧 England"},
    {"code": "NL", "name": "🇳🇱 Netherlands"},
    {"code": "PT", "name": "🇵🇹 Portugal"},
    {"code": "BE", "name": "🇧🇪 Belgium"},
    {"code": "US", "name": "🇺🇸 USA"},
    {"code": "MX", "name": "🇲🇽 Mexico"},
    {"code": "CO", "name": "🇨🇴 Colombia"},
    {"code": "SE", "name": "🇸🇪 Sweden"},
    {"code": "CH", "name": "🇨🇭 Switzerland"},
    {"code": "DK", "name": "🇩🇰 Denmark"},
    {"code": "HR", "name": "🇭🇷 Croatia"},
    {"code": "NG", "name": "🇳🇬 Nigeria"},
    {"code": "JP", "name": "🇯🇵 Japan"},
    {"code": "KR", "name": "🇰🇷 South Korea"},
    {"code": "MA", "name": "🇲🇦 Morocco"},
    {"code": "AU", "name": "🇦🇺 Australia"},
    {"code": "CA", "name": "🇨🇦 Canada"},
    {"code": "IR", "name": "🇮🇷 Iran"},
    {"code": "SA", "name": "🇸🇦 Saudi Arabia"},
    {"code": "GH", "name": "🇬🇭 Ghana"},
    {"code": "UY", "name": "🇺🇾 Uruguay"},
    {"code": "PL", "name": "🇵🇱 Poland"},
    {"code": "RS", "name": "🇷🇸 Serbia"},
    {"code": "SN", "name": "🇸🇳 Senegal"},
    {"code": "TN", "name": "🇹🇳 Tunisia"},
    {"code": "QA", "name": "🇶🇦 Qatar"},
]

# Persian names mapping for display in contact teams
PERSIAN_NAMES = {
    "🇧🇷 Brazil": "برزیل",
    "🇩🇪 Germany": "آلمان",
    "🇫🇷 France": "فرانسه",
    "🇦🇷 Argentina": "آرژانتین",
    "🇪🇸 Spain": "اسپانیا",
    "🇮🇹 Italy": "ایتالیا",
    "🇬🇧 England": "انگلیس",
    "🇳🇱 Netherlands": "هلند",
    "🇵🇹 Portugal": "پرتغال",
    "🇧🇪 Belgium": "بلژیک",
    "🇺🇸 USA": "آمریکا",
    "🇲🇽 Mexico": "مکزیک",
    "🇨🇴 Colombia": "کلمبیا",
    "🇸🇪 Sweden": "سوئد",
    "🇨🇭 Switzerland": "سوئیس",
    "🇩🇰 Denmark": "دانمارک",
    "🇭🇷 Croatia": "کرواسی",
    "🇳🇬 Nigeria": "نیجریه",
    "🇯🇵 Japan": "ژاپن",
    "🇰🇷 South Korea": "کره جنوبی",
    "🇲🇦 Morocco": "مراکش",
    "🇦🇺 Australia": "استرالیا",
    "🇨🇦 Canada": "کانادا",
    "🇮🇷 Iran": "ایران",
    "🇸🇦 Saudi Arabia": "عربستان",
    "🇬🇭 Ghana": "غنا",
    "🇺🇾 Uruguay": "اروگوئه",
    "🇵🇱 Poland": "لهستان",
    "🇷🇸 Serbia": "صربستان",
    "🇸🇳 Senegal": "سنگال",
    "🇹🇳 Tunisia": "تونس",
    "🇶🇦 Qatar": "قطر",
}

async def send_to_admin(context: ContextTypes.DEFAULT_TYPE, text: str):
    try:
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=text)
    except Exception as e:
        print(f"خطا در ارسال پیام به ادمین: {e}")

async def send_to_channel_async(context: ContextTypes.DEFAULT_TYPE, text: str):
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    except Exception as e:
        print(f"خطا در ارسال پیام به کانال: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ثبت تیم🏟", callback_data='register_team')],
        [InlineKeyboardButton("مصاحبه کردن🎙", callback_data='interview')],
        [InlineKeyboardButton("ثبت ترکیب برای مسابقه بعدی⚽️", callback_data='lineup')],
        [InlineKeyboardButton("درخواست بازی دوستانه🥅", callback_data='friendly_match_request')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('سلام خوش آمدید! انتخاب کنید:', reply_markup=reply_markup)

async def channel_formats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message formats to admin when /Channel command is used"""
    user_id = update.effective_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        return

    formats_text = """🏳V🏴 = T ( END )
🏳V🏴 = S ( START )
🏳=2 🏴=7 ( MATCH RESULT )
🏴 = NAME ( GOAL SCORER )
🏳 VS 🏴 = 22:00"""

    await update.message.reply_text(formats_text)

async def interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Check if user has registered a team
    if user_id not in teams:
        await query.answer()
        await query.edit_message_text(text="❌ شما تیم پر نکردید ❌", parse_mode='HTML')
        return

    # Add user to waiting list for interview
    waiting_for_interview.add(user_id)

    await query.answer()
    await query.edit_message_text(text="مصاحبه خود را ارسال کنید :")

async def lineup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Check if user has registered a team
    if user_id not in teams:
        await query.answer()
        await query.edit_message_text(text="❌ شما تیم پر نکردید ❌", parse_mode='HTML')
        return

    # Add user to waiting list for lineup
    waiting_for_lineup.add(user_id)

    await query.answer()
    await query.edit_message_text(text="تصویر ترکیب خودتان را برای مسابقه بعد ارسال کنید :")

async def register_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in teams:
        await query.answer()
        await query.edit_message_text(text="❌ شما قبلا تیم ثبت کرده‌اید ❌")
        return

    # Filter out full teams
    available_countries = []
    for c in COUNTRIES:
        team_count = sum(1 for team_name in teams.values() if team_name == c['name'])
        if team_count < TEAM_CAPACITY:
            available_countries.append(c)

    if not available_countries:
        await query.answer()
        await query.edit_message_text(text="❌ هیچ تیمی در دسترس نیست! همه تیم‌ها پر هستند.")
        return

    buttons = []
    row = []
    for idx, c in enumerate(available_countries):
        row.append(InlineKeyboardButton(c['name'], callback_data=f"select_{c['code']}"))
        if (idx + 1) % 4 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    keyboard = InlineKeyboardMarkup(buttons)

    await query.answer()
    try:
        await query.edit_message_text(text="یک کشور برای تیم انتخاب کن:", reply_markup=keyboard)
    except Exception as e:
        # If editing fails, send a new message instead
        await context.bot.send_message(
            chat_id=user_id,
            text="یک کشور برای تیم انتخاب کن:",
            reply_markup=keyboard
        )

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if user_id in teams:
        await query.answer()
        await query.edit_message_text(text="❌ شما قبلا تیم ثبت کرده‌اید ❌")
        return

    country_code = data.split("_")[1]
    country = next((c for c in COUNTRIES if c['code'] == country_code), None)
    if country:
        # Check if team is already full
        team_count = sum(1 for team_name in teams.values() if team_name == country['name'])
        if team_count >= TEAM_CAPACITY:
            await query.answer()
            await query.edit_message_text(text=f"❌ تیم {country['name']} پر است! لطفا تیم دیگری انتخاب کنید.")
            return

        # Register the team
        teams[user_id] = country['name']

        # Notify admin
        username = query.from_user.username or "ندارد"
        text = f"{country['name']} / @{username}"
        await send_to_admin(context, text)

        await query.answer()
        await query.edit_message_text(text=f"✅ تیم شما ثبت شد: {country['name']}")
        print(f"تیم ثبت شد: {username} - {country['name']}")
    else:
        await query.answer()
        await query.edit_message_text(text="کشور انتخاب شده معتبر نیست.")

async def handle_interview_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from users"""
    user_id = update.effective_user.id

    # Check if admin is sending a message
    if user_id == ADMIN_USER_ID:
        handled = await handle_admin_messages(update, context)
        if handled:
            return

    # Handle interview messages
    if user_id in waiting_for_interview:
        if update.message.text:
            team_name = teams.get(user_id, "نامشخص")
            username = update.effective_user.username or "ندارد"

            # Send to admin for approval
            keyboard = [
                [
                    InlineKeyboardButton("✅ تایید", callback_data=f'approve_{user_id}'),
                    InlineKeyboardButton("❌ رد", callback_data=f'reject_{user_id}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message_text = f"مصاحبه جدید:\n\nتیم: {team_name}\nکاربر: @{username}\n\nمتن مصاحبه:\n{update.message.text}"

            admin_message = await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=message_text,
                reply_markup=reply_markup
            )

            # Store pending interview
            pending_interviews[admin_message.message_id] = {
                'user_id': user_id,
                'team_name': team_name,
                'interview_text': update.message.text
            }

            waiting_for_interview.remove(user_id)
            await update.message.reply_text("مصاحبه شما ارسال شد و منتظر تایید ادمین است.")

    # Handle lineup messages
    elif user_id in waiting_for_lineup:
        if update.message.photo:
            team_name = teams.get(user_id, "نامشخص")
            username = update.effective_user.username or "ندارد"

            # Forward photo to admin
            try:
                await context.bot.send_photo(
                    chat_id=ADMIN_USER_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=f"ترکیب جدید:\n\nتیم: {team_name}\nکاربر: @{username}"
                )
                waiting_for_lineup.remove(user_id)
                await update.message.reply_text("✅ ترکیب شما ارسال شد و به ادمین فرستاده شد.")
            except Exception as e:
                print(f"خطا در ارسال عکس ترکیب: {e}")
                await update.message.reply_text("❌ خطا در ارسال ترکیب. لطفا دوباره تلاش کنید.")
        else:
            await update.message.reply_text("لطفا یک عکس ارسال کنید.")

    elif user_id in waiting_for_team_message:
        if update.message.text:
            target_team = context.user_data.get('target_team')
            if not target_team:
                await update.message.reply_text("تیم مقصد مشخص نیست. لطفا دوباره تلاش کنید.")
                waiting_for_team_message.remove(user_id)
                return

            sender_team = teams.get(user_id, "نامشخص")
            username = update.effective_user.username or "ندارد"

            # Find the user who registered the target team
            team_user_id = next((uid for uid, team_name in teams.items() if team_name == target_team), None)

            if team_user_id:
                # Send to team owner
                try:
                    await context.bot.send_message(
                        chat_id=team_user_id,
                        text=f"پیام از طرف تیم: {sender_team}\n\n{update.message.text}"
                    )

                    # Send to admin
                    admin_message = f"تیم {target_team} از طرف تیم {sender_team} پیام دریافت کرد:\n{update.message.text}"
                    await send_to_admin(context, admin_message)

                    await update.message.reply_text(f"پیام شما به تیم {target_team} ارسال شد.")
                except Exception as e:
                    await update.message.reply_text(f"❌ خطا در ارسال پیام به تیم {target_team}: {e}")
            else:
                await update.message.reply_text(f"❌ تیمی با نام {target_team} پیدا نشد.")

            waiting_for_team_message.remove(user_id)
            context.user_data.pop('target_team', None)

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin approval/rejection responses"""
    query = update.callback_query
    user_id = query.from_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        await query.answer("شما مجاز نیستید!")
        return

    data = query.data
    action, target_user_id = data.split('_', 1)
    target_user_id = int(target_user_id)

    # Find the pending interview
    message_id = query.message.message_id
    if message_id not in pending_interviews:
        await query.answer("مصاحبه پیدا نشد!")
        return

    interview_data = pending_interviews[message_id]

    if action == 'approve':
        # Send to channel
        channel_text = f"🎙 مصاحبه تیم {interview_data['team_name']} 🎙\n\n{interview_data['interview_text']}"
        await send_to_channel_async(context, channel_text)

        # Notify user
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="✅ مصاحبه شما تایید و در کانال منتشر شد!"
            )
        except:
            pass

        await query.edit_message_text(text=f"✅ مصاحبه تایید شد و در کانال منتشر شد.\n\n{query.message.text}")

    elif action == 'reject':
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ مصاحبه شما رد شد. لطفا دوباره تلاش کنید."
            )
        except:
            pass

        await query.edit_message_text(text=f"❌ مصاحبه رد شد.\n\n{query.message.text}")

    # Remove from pending
    del pending_interviews[message_id]
    await query.answer()

async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle various admin message types"""
    user_id = update.effective_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        return False

    message_text = update.message.text
    if not message_text:
        return False

    message_text = message_text.strip()
    processed_messages = []

    # Process each line separately and collect messages
    lines = message_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle match schedule format: 🇮🇷 VS 🇦🇷 = 20:30
        result = handle_match_schedule_collect(line)
        if result:
            processed_messages.append(result)
            continue

        # Handle score format: 🇮🇷=2 🇦🇷=1
        result = handle_score_message_collect(line)
        if result:
            processed_messages.append(result)
            continue

        # Handle goal scorer format: 🇦🇷 = لیونل مسی
        result = handle_goal_scorer_message_collect(line)
        if result:
            processed_messages.append(result)
            continue

        # Handle match status format: 🇦🇷V🇮🇷 = T or S
        result = handle_match_status_message_collect(line)
        if result:
            processed_messages.append(result)
            continue

    # Send all processed messages as one combined message
    if processed_messages:
        final_message = '\n\n'.join(processed_messages)
        await send_to_channel_async(context, final_message)
        print(f"پیام مخلوط ارسال شد: {len(processed_messages)} بخش")
        return True

    return False

def handle_score_message_collect(message_text):
    """Handle score format and return formatted message"""
    try:
        # Split by spaces and look for = signs
        parts = message_text.split()
        if len(parts) >= 2:
            team1_part = None
            team2_part = None

            for part in parts:
                if '=' in part:
                    if team1_part is None:
                        team1_part = part
                    elif team2_part is None:
                        team2_part = part
                        break

            if team1_part and team2_part:
                # Extract country and score
                team1_country, team1_score = team1_part.split('=')
                team2_country, team2_score = team2_part.split('=')

                return f"⚽️ نتیجه بازی ⚽️\n\n{team1_country} {team1_score} - {team2_score} {team2_country}"
    except:
        pass
    return None

def handle_match_schedule_collect(message_text):
    """Handle match schedule format and return formatted message"""
    try:
        if ' VS ' in message_text and '=' in message_text:
            teams_part, time_part = message_text.split('=', 1)
            teams_part = teams_part.strip()
            time_part = time_part.strip()

            if ' VS ' in teams_part:
                team1, team2 = teams_part.split(' VS ')
                return f"📅 برنامه بازی 📅\n\n{team1.strip()} VS {team2.strip()}\n🕐 ساعت: {time_part}"
    except:
        pass
    return None

def handle_goal_scorer_message_collect(message_text):
    """Handle goal scorer format and return formatted message"""
    try:
        if '=' in message_text and len(message_text.split('=')) == 2:
            country, scorer = message_text.split('=', 1)
            country = country.strip()
            scorer = scorer.strip()

            # Check if it's a goal scorer (not a score)
            if not scorer.isdigit():
                return f"⚽️ گل زن ⚽️\n\n{country}\n👤 {scorer}"
    except:
        pass
    return None

def handle_match_status_message_collect(message_text):
    """Handle match status format and return formatted message"""
    try:
        if 'V' in message_text and '=' in message_text:
            teams_part, status_part = message_text.split('=', 1)
            status_part = status_part.strip().upper()

            if 'V' in teams_part:
                teams = teams_part.split('V')
                if len(teams) == 2:
                    team1 = teams[0].strip()
                    team2 = teams[1].strip()

                    if status_part == 'S':
                        return f"🚀 شروع بازی 🚀\n\n{team1} VS {team2}\n\n⏰ بازی آغاز شد!"
                    elif status_part == 'T':
                        return f"🏁 پایان بازی 🏁\n\n{team1} VS {team2}\n\n⏱ بازی به پایان رسید!"
    except:
        pass
    return None

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset command to clear teams and waiting lists."""
    user_id = update.effective_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("شما مجاز به استفاده از این دستور نیستید!")
        return

    # Clear teams and waiting lists
    teams.clear()
    waiting_for_interview.clear()
    waiting_for_lineup.clear()
    pending_interviews.clear()  # Clear any pending interviews
    waiting_for_team_message.clear()
    pending_match_requests.clear()  # Clear pending match requests
    friendly_match_messages.clear()  # Clear friendly match message tracking

    await update.message.reply_text("📋 تمامی اطلاعات ربات ریست شد!")

async def contact_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Check if user has registered a team
    if user_id not in teams:
        await query.answer()
        await query.edit_message_text("❌ شما هنوز تیمی ثبت نکرده‌اید! ابتدا تیم ثبت کنید ❌")
        return

    # Get user's own team
    user_team = teams.get(user_id)

    # Show full teams (teams that have reached capacity) except user's own team
    full_teams = []
    for team_name in set(teams.values()):  # Use set to get unique team names
        team_count = sum(1 for t in teams.values() if t == team_name)
        if team_count >= TEAM_CAPACITY and team_name != user_team:
            full_teams.append(team_name)

    if not full_teams:
        await query.answer()
        await query.edit_message_text("تیمی برای تماس وجود ندارد.")
        return

    keyboard = []
    for team_name in full_teams:
        # Get Persian name for display, fallback to original if not found
        display_name = PERSIAN_NAMES.get(team_name, team_name)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f'select_team_{team_name}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()
    await query.edit_message_text("انتخاب کنید با چه تیمی میخواهید تماس بگیرید:", reply_markup=reply_markup)

async def select_team_to_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Extract team name properly - everything after "select_team_"
    team_name = query.data[12:]  # Remove "select_team_" prefix

    keyboard = [
        [InlineKeyboardButton("ارسال پیام به تیم ✉️", callback_data=f'send_message_{team_name}')],
        [InlineKeyboardButton("درخواست بازی دوستانه 🎮", callback_data=f'request_match_{team_name}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.edit_message_text(f"شما تیم {team_name} را انتخاب کردید.\n\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_match_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle match request approval/rejection"""
    query = update.callback_query
    user_id = query.from_user.id

    data = query.data
    if data.startswith('approve_match_'):
        # Parse data: approve_match_{sender_user_id}_{target_team}
        parts = data.split('_', 3)
        sender_user_id = int(parts[2])
        target_team = parts[3] if len(parts) > 3 else ""

        # Find the pending match request
        message_id = query.message.message_id
        if message_id not in pending_match_requests:
            await query.answer("درخواست پیدا نشد!")
            return

        match_data = pending_match_requests[message_id]
        sender_team = match_data['sender_team']

        # Send confirmation to admin
        admin_message = f"✅ درخواست بازی دوستانه تایید شد:\nتیم {sender_team} و تیم {target_team} قبول کردند"
        await send_to_admin(context, admin_message)

        # Notify sender
        try:
            await context.bot.send_message(
                chat_id=sender_user_id,
                text=f"✅ تیم {target_team} درخواست بازی دوستانه شما را قبول کرد!"
            )
        except:
            pass

        await query.edit_message_text(f"✅ درخواست بازی دوستانه با تیم {sender_team} تایید شد.")

        # Remove from pending
        del pending_match_requests[message_id]

    elif data.startswith('reject_match_'):
        # Parse data: reject_match_{sender_user_id}_{target_team}
        parts = data.split('_', 3)
        sender_user_id = int(parts[2])
        target_team = parts[3] if len(parts) > 3 else ""

        # Find the pending match request
        message_id = query.message.message_id
        if message_id not in pending_match_requests:
            await query.answer("درخواست پیدا نشد!")
            return

        match_data = pending_match_requests[message_id]
        sender_team = match_data['sender_team']

        # Notify sender
        try:
            await context.bot.send_message(
                chat_id=sender_user_id,
                text=f"❌ تیم {target_team} درخواست بازی دوستانه شما را رد کرد."
            )
        except:
            pass

        await query.edit_message_text(f"❌ درخواست بازی دوستانه با تیم {sender_team} رد شد.")

        # Remove from pending
        del pending_match_requests[message_id]

    await query.answer()

async def send_message_to_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Extract team name properly - everything after "send_message_"
    team_name = query.data[13:]  # Remove "send_message_" prefix

    waiting_for_team_message.add(user_id)
    context.user_data['target_team'] = team_name # Store the target team name in user_data
    await query.answer()
    await query.edit_message_text(f"لطفا پیام خود را برای تیم {team_name} ارسال کنید:")

async def request_friendly_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Extract team name properly - everything after "request_match_"
    target_team = query.data[14:]  # Remove "request_match_" prefix
    sender_team = teams.get(user_id, "نامشخص")

    # Find the user who registered the target team
    team_user_id = next((uid for uid, team_name in teams.items() if team_name == target_team), None)

    if team_user_id:
        # Send approval request to target team
        keyboard = [
            [
                InlineKeyboardButton("✅", callback_data=f'approve_match_{user_id}_{target_team}'),
                InlineKeyboardButton("❌", callback_data=f'reject_match_{user_id}_{target_team}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        match_request_message = await context.bot.send_message(
            chat_id=team_user_id,
            text=f"تیم {sender_team} از تیم {target_team} درخواست مسابقه دوستانه دریافت کرد.\nآیا تایید میشود؟",
            reply_markup=reply_markup
        )

        # Store pending match request
        pending_match_requests[match_request_message.message_id] = {
            'sender_user_id': user_id,
            'target_team': target_team,
            'sender_team': sender_team
        }

        await query.answer()
        await query.edit_message_text(f"درخواست بازی دوستانه به تیم {target_team} ارسال شد.")
    else:
        await query.answer()
        await query.edit_message_text(f"❌ تیمی با نام {target_team} پیدا نشد.")

async def friendly_match_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send friendly match request to users who have registered teams"""
    query = update.callback_query
    user_id = query.from_user.id

    # Check if user has registered a team
    if user_id not in teams:
        await query.answer()
        await query.edit_message_text("❌ شما هنوز تیمی ثبت نکرده‌اید! ابتدا تیم ثبت کنید ❌")
        return

    sender_team = teams.get(user_id)

    # Initialize message tracking for this sender
    friendly_match_messages[user_id] = []

    # Send request only to users who have registered teams (excluding the sender)
    sent_count = 0
    for other_user_id in teams.keys():
        if other_user_id != user_id:
            try:
                keyboard = [
                    [
                        InlineKeyboardButton("✅", callback_data=f'accept_friendly_{user_id}'),
                        InlineKeyboardButton("❌", callback_data=f'decline_friendly_{user_id}')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                sent_message = await context.bot.send_message(
                    chat_id=other_user_id,
                    text=f"آیا مسابقه دوستانه با تیم {sender_team} قبول می‌کنید؟",
                    reply_markup=reply_markup
                )
                
                # Track this message
                friendly_match_messages[user_id].append((other_user_id, sent_message.message_id))
                sent_count += 1
            except Exception as e:
                print(f"خطا در ارسال درخواست به کاربر {other_user_id}: {e}")

    await query.answer()
    if sent_count > 0:
        await query.edit_message_text(f"درخواست بازی دوستانه به {sent_count} تیم ارسال شد.")
    else:
        await query.edit_message_text("هیچ تیم دیگری برای ارسال درخواست پیدا نشد.")

async def handle_friendly_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle friendly match acceptance or decline"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data.startswith('accept_friendly_'):
        sender_user_id = int(data.split('_')[2])
        
        sender_team = teams.get(sender_user_id, "نامشخص")
        accepter_team = teams.get(user_id, "نامشخص")

        # Delete all other pending friendly match messages from this sender
        if sender_user_id in friendly_match_messages:
            for chat_id, message_id in friendly_match_messages[sender_user_id]:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    print(f"خطا در حذف پیام: {e}")
            
            # Clear the tracking for this sender
            del friendly_match_messages[sender_user_id]

        # Send notification to admin and both teams
        match_message = f"مسابقه دوستانه بین دو تیم {sender_team} و {accepter_team} شکل گرفت."
        
        # Send to admin
        await send_to_admin(context, match_message)
        
        # Send to sender
        try:
            await context.bot.send_message(
                chat_id=sender_user_id,
                text=match_message
            )
        except:
            pass
        
        # Send to accepter (current user)
        await query.edit_message_text(f"✅ شما درخواست بازی دوستانه تیم {sender_team} را قبول کردید.\n\n{match_message}")

    elif data.startswith('decline_friendly_'):
        sender_user_id = int(data.split('_')[2])
        sender_team = teams.get(sender_user_id, "نامشخص")
        
        await query.edit_message_text(f"❌ شما درخواست بازی دوستانه تیم {sender_team} را رد کردید.")

    await query.answer()

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("Channel", channel_formats))
    application.add_handler(CommandHandler("reset", reset))  # Add reset command handler
    application.add_handler(CallbackQueryHandler(register_team, pattern='^register_team$'))
    application.add_handler(CallbackQueryHandler(interview, pattern='^interview$'))
    application.add_handler(CallbackQueryHandler(lineup, pattern='^lineup$'))
    application.add_handler(CallbackQueryHandler(select_country, pattern='^select_'))
    application.add_handler(CallbackQueryHandler(handle_admin_response, pattern='^(approve|reject)_'))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_interview_message))

    # Add handlers for team contact actions
    application.add_handler(CallbackQueryHandler(contact_teams, pattern='^contact_teams$'))
    application.add_handler(CallbackQueryHandler(select_team_to_contact, pattern='^select_team_'))
    application.add_handler(CallbackQueryHandler(send_message_to_team, pattern='^send_message_'))
    application.add_handler(CallbackQueryHandler(request_friendly_match, pattern='^request_match_'))
    application.add_handler(CallbackQueryHandler(handle_match_approval, pattern='^(approve|reject)_match_'))
    application.add_handler(CallbackQueryHandler(friendly_match_request, pattern='^friendly_match_request$'))
    application.add_handler(CallbackQueryHandler(handle_friendly_response, pattern='^(accept|decline)_friendly_'))

    print("ربات شروع به کار کرد.")
    application.run_polling()

if __name__ == '__main__':
    main()