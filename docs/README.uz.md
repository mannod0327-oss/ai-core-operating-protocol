# O'zbekcha yo'riqnoma

## Bu nima?

Bu **bitta operating skill**. U agentga vazifaga mos, o'sha hostda mavjud skill va
vositalarni tanlash, kerakli ko'rsatmalarni o'qish va natijani tekshirishni o'rgatadi.
Ichidagi 15 ta catalog yozuvi test namunasi; 15 ta ishlaydigan integratsiya emas.

RC2da xavfsiz installer, 8 ta filesystem adapter, alohida skill/upload/plugin paketlari,
testlar va GitHub CI konfiguratsiyasi bor. To'liq cross-agent ishlashi hali tasdiqlanmagan.

## Qaysi fayl kerak?

- `*-skill-v2.0.0-rc2.zip`: standalone skill importer uchun.
- `*-claude-upload-v2.0.0-rc2.zip`: Claude custom skill upload uchun.
- `*-openai-v2.0.0-rc2.zip`: OpenAI plugin importer uchun, standalone skill emas.
- `*-claude-plugin-v2.0.0-rc2.zip`: Claude Code plugin distributivi.
- `*-codex-*`, `*-gemini-*` va boshqa runtime nomli ZIPlar: workspace joylashuvi.
- `*-source-v2.0.0-rc2.zip`: kod, TZ, testlar va hujjatlar; GitHub uchun shu manba.
- `*-marketplace-*`: mahalliy marketplace tuzilmasi; hali hech qayerda nashr qilinmagan.

Har bir skill nusxasida bir xil avtomatik tanlash ko'rsatmalari bor. Hammasini bir
vaqtning o'zida o'rnatish kerak emas: takroriy nusxalar hostda ustuvorlik nizosi tug'dirishi mumkin.

## Avtomatik rejim qanday?

Mos importerdan o'rnatib, skillni yoqish kerak. Keyin yangi chatda oddiy vazifa beriladi:
masalan, “PDFni Word hujjatga aylantir”. Host mos skillni tanlashi mumkin.
Majburiy ruxsat so'ralishi normal. Disabled yoki explicit-only sozlama chetlab o'tilmaydi.

Bu barcha chatda majburiy faollashadigan servis emas. Oddiy ZIP attachment o'rnatish
bilan teng emas. ChatGPT web va haqiqiy mobile ilovada alohida sinov kerak.
Hozir foydalanuvchi hisobida import/activation kuzatilmagan; “ishlayapti” deb da'vo qilinmaydi.

## Xavfsiz foydalanish

[Install qo'llanmasi](install.md) bo'yicha avval plan, keyin install.
Original skill/configlar saqlanadi. Keyingi edit aniqlansa uninstall to'xtaydi.
Backup/snapshotlar avtomatik o'chirilmaydi. Python router pul sarflamaydi va
tashqi vositalarni chaqirmaydi.

[Readiness](RC2-READINESS.md) bajarilgan va ochiq tekshiruvlarni ajratadi.
GitHub nashri keyingi, alohida ruxsat talab qiladigan bosqich.
