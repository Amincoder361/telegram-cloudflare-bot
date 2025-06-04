const TOKEN = "7113984877:AAEydlvWVX0rwUy8ZLkrFXSEg4sjO-dGuO4";
const ADMIN_USERNAME = "Aminw_xd";

const API_URL = `https://api.telegram.org/bot${TOKEN}`;
const TEAM_KV_NAMESPACE = TEAM_KV; // این نامی هست که توی تنظیمات KV باید بزاری

// لیست 32 کشور جام جهانی با پرچم
const COUNTRIES = [
  { code: "BR", name: "🇧🇷 Brazil" },
  { code: "DE", name: "🇩🇪 Germany" },
  { code: "FR", name: "🇫🇷 France" },
  { code: "AR", name: "🇦🇷 Argentina" },
  { code: "ES", name: "🇪🇸 Spain" },
  { code: "IT", name: "🇮🇹 Italy" },
  { code: "GB", name: "🇬🇧 England" },
  { code: "NL", name: "🇳🇱 Netherlands" },
  { code: "PT", name: "🇵🇹 Portugal" },
  { code: "BE", name: "🇧🇪 Belgium" },
  { code: "RU", name: "🇷🇺 Russia" },
  { code: "US", name: "🇺🇸 USA" },
  { code: "MX", name: "🇲🇽 Mexico" },
  { code: "CO", name: "🇨🇴 Colombia" },
  { code: "CL", name: "🇨🇱 Chile" },
  { code: "SE", name: "🇸🇪 Sweden" },
  { code: "CH", name: "🇨🇭 Switzerland" },
  { code: "DK", name: "🇩🇰 Denmark" },
  { code: "HR", name: "🇭🇷 Croatia" },
  { code: "NG", name: "🇳🇬 Nigeria" },
  { code: "JP", name: "🇯🇵 Japan" },
  { code: "KR", name: "🇰🇷 South Korea" },
  { code: "EG", name: "🇪🇬 Egypt" },
  { code: "TN", name: "🇹🇳 Tunisia" },
  { code: "MA", name: "🇲🇦 Morocco" },
  { code: "AU", name: "🇦🇺 Australia" },
  { code: "CA", name: "🇨🇦 Canada" },
  { code: "IR", name: "🇮🇷 Iran" },
  { code: "SA", name: "🇸🇦 Saudi Arabia" },
  { code: "GH", name: "🇬🇭 Ghana" },
  { code: "UY", name: "🇺🇾 Uruguay" },
  { code: "PL", name: "🇵🇱 Poland" },
];

// ارسال پیام به تلگرام
async function sendMessage(chat_id, text, reply_markup = null) {
  const body = {
    chat_id,
    text,
    parse_mode: "Markdown",
  };
  if (reply_markup) {
    body.reply_markup = reply_markup;
  }
  await fetch(`${API_URL}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// دریافت اطلاعات از KV (ثبت تیم‌ها)
async function getTeam(userId) {
  return await TEAM_KV_NAMESPACE.get(`team_${userId}`);
}

// ذخیره تیم در KV
async function setTeam(userId, team) {
  await TEAM_KV_NAMESPACE.put(`team_${userId}`, team);
}

// ارسال پیام به ادمین
async function sendToAdmin(text) {
  await fetch(`${API_URL}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: `@${ADMIN_USERNAME}`,
      text,
    }),
  });
}

// ساخت کیبورد برای انتخاب کشورها (32 تا دکمه در چند ردیف)
function buildCountryKeyboard() {
  const buttons = COUNTRIES.map((c) => ({
    text: c.name,
    callback_data: `select_${c.code}`,
  }));
  const chunkSize = 4;
  const keyboard = [];
  for (let i = 0; i < buttons.length; i += chunkSize) {
    keyboard.push(buttons.slice(i, i + chunkSize));
  }
  return { inline_keyboard: keyboard };
}

addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  if (request.method !== "POST") {
    return new Response("Not Allowed", { status: 405 });
  }
  const update = await request.json();

  // پیام متنی
  if (update.message) {
    const chat_id = update.message.chat.id;
    const text = update.message.text;
    const userId = update.message.from.id;
    const username = update.message.from.username || "";

    if (text === "/start") {
      const welcomeText = `سلام خیلی خوش اومدی به ربات ما🛸\nخب انتخاب کن :`;
      const keyboard = {
        inline_keyboard: [
          [{ text: "ثبت تیم🏟", callback_data: "register_team" }],
          [{ text: "دیدن وضعیت لیگ👤", url: "http://t.me/GoatBall_Bot/GoatBall" }],
        ],
      };
      await sendMessage(chat_id, welcomeText, keyboard);
      return new Response("ok");
    }
  }

  // کال‌بک‌ها (دکمه‌های شیشه‌ای)
  if (update.callback_query) {
    const chat_id = update.callback_query.message.chat.id;
    const userId = update.callback_query.from.id;
    const username = update.callback_query.from.username || "";
    const data = update.callback_query.data;

    // ثبت تیم
    if (data === "register_team") {
      // چک ثبت تیم قبلی
      const team = await getTeam(userId);
      if (team) {
        await sendMessage(chat_id, "❌️شما یکبار تیم ثبت کرده اید❌️");
      } else {
        await sendMessage(
          chat_id,
          "بین کشور های زیر یک کشور انتخاب کنید برای مسابقات :",
          buildCountryKeyboard()
        );
      }
      return new Response("ok");
    }

    // انتخاب کشور
    if (data.startsWith("select_")) {
      const countryCode = data.split("_")[1];
      const team = await getTeam(userId);
      if (team) {
        await sendMessage(chat_id, "❌️شما یکبار تیم ثبت کرده اید❌️");
      } else {
        const country = COUNTRIES.find((c) => c.code === countryCode);
        if (country) {
          await setTeam(userId, country.name);
          await sendToAdmin(`${country.name}\n@${username || "ندارد"}`);
          await sendMessage(chat_id, `تیم شما با موفقیت ثبت شد: ${country.name}`);
        } else {
          await sendMessage(chat_id, "کشور انتخاب شده معتبر نیست.");
        }
      }
      return new Response("ok");
    }
  }

  return new Response("ok");
}
