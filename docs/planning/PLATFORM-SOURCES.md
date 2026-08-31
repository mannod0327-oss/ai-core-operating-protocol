# Platforma manbalari va tekshirish chegarasi

Tekshirilgan sana: 2026-08-31. Quyidagilar rasmiy sahifalarga asoslangan boshlang'ich
yo'nalish; ayni hisob yoki o'rnatilgan klientda live test o'tkazilgan degani emas.
Implementatsiyada aniq host/version/OS va ko'rilgan hujjat sanasi qayta qayd qilinsin.

## Claude web/desktop va Claude Code — alohida adapterlar

Claude custom skill uchun skill katalogini ZIP qilib importerga yuklash yo'lini
hujjatlaydi. Hisob/organization huquqlari import imkoniga ta'sir qilishi mumkin.
Mobil mavjudlik va faollashuv alohida hisob/klientda tekshirilsin.
[Claude custom skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

Claude Code skillni mos so'rovda o'zi tanlashi mumkin; explicit-only sozlamasini
chetlab o'tmaslik kerak. Local skill va plugin distribution alohida sinovdan o'tadi.
[Claude Code skills](https://code.claude.com/docs/en/skills).

## Codex va ChatGPT

Canonical skill bilan UI/platform metadata alohida saqlansin. O'qilgan OpenAI
hujjati standalone uchun desktop/CLI/IDE, plugin tarkibidagi skill uchun web/mobile
yo'lini ko'rsatadi. Boshqa importer ko'rinsa, actual UI dalili bilan alohida tekshirilsin.
Local katalogga nusxalash web hisobga upload emas.
[OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills).

## Gemini CLI

User `.gemini/skills` yoki `.agents/skills`, workspace uchun ham tegishli aliaslar
hujjatlangan. Discovery, enabled state, workspace trust va activation consent
alohida tekshiriladi. Avtomatik tanlash consentni bekor qilmaydi.
[Managing Agent Skills](https://geminicli.com/docs/cli/using-agent-skills/),
[Getting started](https://geminicli.com/docs/cli/tutorials/skills-getting-started/).

Bu dalil Gemini web/mobile chat yoki Gems uchun native skill kafolati emas.

## Google Antigravity

Hozirgi IDE hujjatida workspace `.agents/skills`, global `~/.gemini/config/skills`
ko'rsatilgan. Gemini CLI global joylashuvi bilan bir deb olinmasin. Agentning IDE,
SDK va boshqa sirtlari bir xil dalil bilan tasdiqlanmaydi.
[Antigravity Skills](https://antigravity.google/docs/skills?app=antigravity-ide).

## Qo'shimcha adapter nomzodlari

Cursor `.cursor/skills` va `.agents/skills` kabi yo'llarni hujjatlaydi. Lokal global
skill remote/cloud muhitga o'z-o'zidan ko'chishini taxmin qilmaslik kerak.
[Cursor Skills](https://cursor.com/docs/skills).

GitHub Copilot uchun repository va personal skill yo'llari bor; CLI, IDE agent
mode va cloud sirtlari version/permission bilan alohida tekshirilsin.
[Copilot Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).

OpenCode native hamda agent-compatible kataloglarni hujjatlaydi. Skill tool
permission va discovery holati real klientda tekshirilsin.
[OpenCode Skills](https://opencode.ai/docs/skills).

Generic adapter bu mahsulotlar uchun cheksiz kafolat bermaydi. Native skillni
tushunmaydigan agent uchun optional instructions bridge bo'lishi mumkin; u
"native auto skill" deb belgilanmasin. Noma'lum yangi runtime konfiguratsiyasi
hujjat yoki live dalilsiz avtomatik yaratilmasin.

## Yangilash qoidasi

Har adapter yozuvi quyidagilarni saqlasin: host oilasi, surface, aniq sinov versiyasi,
OS, discovery scope/path, package layout, enable/consent shartlari, manba URL/sana,
dalil turi va cheklov. Sahifa o'zgarishi sabab oldingi dalilni o'chirmasdan yangi
snapshot natijasi qo'shilsin. Soxta minimal versiya va taxminiy CLI flag yozilmasin.
