# TZ: AI Core Operating Protocol — cross-agent tayyorgarlik va GitHub relizi

Hujjat versiyasi: 1.0. Sana: 2026-08-31.
Boshlang'ich kod: 2.0.0-rc1. Holat: implementatsiyadan oldingi texnik topshiriq.
Keyingi candidate nomi sifatida 2.0.0-rc2 taklif qilinadi; kod versiyasi hozir o'zgartirilmaydi.

## 1. Kelishilgan ish tartibi

Uchta bosqich bir-biridan ajratiladi:

1. **A — hozir:** RC1ni o'qish, TZ va bajaruvchi promptni yozish, source ZIPning
   yangi nusxasiga planning hujjatlarini qo'shish. Original kod va arxiv saqlanadi.
2. **B — keyingi foydalanuvchi topshirig'i bilan:** TZ bo'yicha kod/skill/adapterlarni
   takomillashtirish, xavfsiz lokal va ruxsat etilgan runtime sinovlarini bajarish.
3. **C — alohida tasdiq bilan:** aniq GitHub owner/repository/visibility/branch/tag
   bo'yicha nashr. B bosqichi tugashi o'zi push yoki public releasega ruxsat emas.

Bu hujjatdagi buyruq va yo'llar B/C bosqichlar uchun loyiha talablari, hozir
bajarilgan ish yoki allaqachon mavjud funksiya sifatida talqin qilinmasin.

## 2. Mahsulot maqsadi

Foydalanuvchi natijani oddiy tilda so'raydi. Agent mavjud mos skill/tool/source'ni
nomini foydalanuvchidan talab qilmasdan tanlaydi, kerakli instruktsiyalarnigina
yuklaydi, topshiriqni vakolat doirasida bajaradi va natijani tekshiradi.

Bu bitta vendor-neutral operating skill va uning distribution/lifecycle vositalari.
U minglab skilllar kutubxonasi, universal tool runtime, model, credential broker
yoki doimo ishlaydigan daemon emas. Boshqa capabilitylarning mavjudligi hostga bog'liq.

Asosiy tamoyil: bitta canonical xulq-atvor, kichik host adapterlari, aniq moslik
chegaralari va qayta tekshiriladigan dalillar. "Barcha agentlarda 100% auto" degan
kafolat berilmaydi. Maqsad — nomma-nom va versiyama-versiya tekshirilgan moslik.

## 3. Boshlang'ich audit va ustuvorlik

To'liq dalillar: [RC1 tahlili](RC1-BASELINE-REVIEW.md).
Manba 58 ta fayl, 120 ta golden ssenariy va 15 ta namunaviy capability yozuvini o'z ichiga oladi.

Relizdan oldingi majburiy ishlar:

- **P0, ma'lumotni saqlash:** B01–B03 — manifest path tekshiruvi, ko'p install
  ownership, foydalanuvchi o'zgarishlari, idempotent install va recoverable uninstall.
- **P1, to'g'rilik:** B04–B07 — missing registry, aralash vazifalar, benchmark gate
  va xatti-harakatga asoslangan xavfsizlik testlari.
- **P1, tarqatish:** B08–B10 — toza CI, yagona build metadata, source drift va
  runtime compatibility dalillari.
- **P2, qulaylik:** diagnostika, ko'p tilli misollar, install yo'riqnomasi va
  qo'shimcha adapterlar. P0/P1 yopilmasdan reklama uchun platformalar soni oshirilmasin.

## 4. Platformalar va qo'llab-quvvatlash modeli

Manbalar va hozirgi hujjatlashtirilgan mexanizmlar:
[PLATFORM-SOURCES.md](PLATFORM-SOURCES.md). Quyidagi bandlar reja, live success emas.

### 4.1 Asosiy qamrov

- **Claude web/desktop:** alohida custom skill ZIP/import yo'li, enabled holat,
  account/organization cheklovi. Claude Code pluginini bu upload bilan tenglashtirmaslik.
- **Claude mobile:** alohida surface; ayni hisobda skill mavjudligi va real mobil
  yangi chatda activation dalili bo'lsa tasdiqlash, aks holda UNVERIFIED/BLOCKED.
- **Claude Code:** user/workspace native skill hamda mavjud plugin/marketplace
  distributivi. `disable-model-invocation` va boshqa host cheklovlarini saqlash.
- **Codex CLI/IDE/desktop:** aniq klient uchun hujjatlashtirilgan discovery yo'li,
  OpenAI metadata va implicit eligibility; discovery precedence/collision testi.
- **Codex cloud hamda ChatGPT web/mobile:** local install ularga avtomatik
  tarqalmaydi. Import/distribution va hisob huquqi alohida tekshirilsin. Mos
  standalone importer bo'lmasa, uning borligi taxmin qilinmasin; package varianti
  va foydalanuvchi tanlovi ochiq belgilanadi.
- **Gemini CLI:** native skill, user/workspace aliaslar, trust, disabled state va
  activation consent. Avtomatik tanlash foydalanuvchining majburiy ruxsatini chetlab o'tmaydi.
- **Google Antigravity IDE:** native skill; workspace/global joylashuvi alohida.
  Gemini CLI yo'llari shunchaki ko'chirilmaydi. SDK yoki boshqa surfacega moslik
  IDE testidan chiqarib olinmaydi.

"Gemini" nomining default ma'nosi ushbu RC1da CLI. Gemini web/mobile/Gems uchun
native importer dalili topilmasa, faqat cheklangan instructions fallbackni
taklif qilish mumkin; uni native skill deb belgilash mumkin emas.

### 4.2 Qo'shimcha agentlar

**Cursor**, **GitHub Copilot (CLI/IDE/cloud alohida)** va **OpenCode** uchun native
adapterlarni B bosqichining kengaytirilgan qamroviga kiritish. Minimal qo'llab-quvvatlangan
versiya taxmin bilan yozilmasin: real test/hujjat asosida qayd qilinsin.

Yangi boshqa agent bitta adapter registratsiyasi orqali qo'shila olsin. Ammo har
yangi nom uchun source, package test va runtime dalili talab qilinadi. Native skill
imkoniyati bo'lmagan hostda generic instructions bridge faqat opt-in, alohida
`instructions-only` maqomida beriladi. Barcha hostga `.agents/skills` yozish universal
moslik testi hisoblanmaydi.

### 4.3 Dalil darajalari

Har `host × surface × version × OS × scope` kombinatsiyasi uchun mustaqil yozuv:

- DOCUMENTED — rasmiy mexanizm topilgan.
- GENERATED — adapter artifacti yaratilgan.
- STATIC_TESTED — schema/layout/integrity testlari o'tgan.
- DISCOVERED — haqiqiy klient uni ro'yxatga olgan.
- ACTIVATION_TESTED — nomini aytmagan yangi so'rovdan host activation dalili olingan.
- OUTCOME_TESTED — tanlangan skill bilan vazifa natijasi tekshirilgan.
- BLOCKED, UNVERIFIED yoki UNSUPPORTED — aniq sabab bilan.

Evidence darajasi test natijasidan alohida: PASS/FAIL/NOT_RUN/BLOCKED. Fayl mavjudligi
activation bo'lib hisoblanmaydi; modelning "ishlatdim" degan gapi yagona dalil emas.

## 5. Arxitektura talablari

### FR-01 — Canonical source

`skills/ai-core-operating-protocol/` umumiy xulq-atvorning yagona manbasi bo'lib qolsin.
Adapterlar uni generatsiya qilsin, qo'lda nusxalangan turli versiyalar yaratmasin.
Hostga xos frontmatter va manifestda faqat kerakli farqlar bo'lsin. Versiya yagona
metadata manbasidan o'qilsin; generated nusxalar hash/semantic drift bilan tekshirilsin.

### FR-02 — Adapter contract

Loyiha ichida deklarativ adapter registry yaratiladi. Bu vendorning yangi API'si emas.
Unda runtime id, surface, distribution kind, supported scopes, safe destination
resolver, dokument URL/sana, metadata transform, capability flags, build validator,
discovery probe va activation-evidence talabi bo'lsin. Schema version qo'yilsin.
Noma'lum runtime/scope uchun yozish boshlanishidan oldin aniq xato qaytarilsin.

Mahsulot nomi va model nomi chalkashtirilmasin. Cloud uchun local home fallback
berilmasin. Kodni ishlata olmaydigan chat uchun Python router talab qilinmasin.

### FR-03 — Native router birinchi

Hostning metadata-first selection mexanizmi asosiy yo'l. Python reference router
test/reference komponenti bo'lib qolsin; undan runtime fallback sifatida foydalanish
uchun haqiqiy integration alohida yozilishi va test qilinishi shart. U shunchaki
ZIPga qo'shilgani uchun host uni ishlatadi deb yozilmasin.

### FR-04 — Reference routing contract

Natija kamida: task intent, source needs, tanlangan capability identitylari,
qisqa tanlash sababi, unmet requirement, clarification ehtiyoji, action risk va
verification needs. Bu qisqa diagnostic bo'lsin, private chain-of-thought emas.

Registryda unique identity, description, supported action/source, availability,
enabled/explicit-only holati va zarur dependency metadata aniqlansin. Runtime
ko'rsatmagan credential/auth ma'lumoti o'ylab topilmasin. Routing read-only bo'lsin;
hech qanday install, auth, fayl o'chirish, xabar yuborish yoki to'lov qilmasin.

Bo'sh/qisman/malformed registry, duplicate id, unknown layer, teng score va no-match
holatlari deterministik hal qilinsin. Yo'q capability chaqirilmasin. Keyword risk
classifier yakuniy authorization qarori bo'lmasin; host permissionlari ustun.

Bir layerda bir nechta zarur capability bo'lishi mumkin: PDF -> DOCX, fayl + web,
inbox -> calendar. Task-step/dependency asosida minimal qamrov va identity dedup
ishlatilsin. Katalog tartibi tasodifan natijani o'zgartirmasin.

### FR-05 — Til va triggerlar

O'zbekcha lotin hamda inglizcha asosiy tillar. Apostrof variantlari (`'`, `’`, `‘`,
`ʻ`, `ʼ`), Uzbek qo'shimchalari va Unicode matn sinovga kiritilsin. Ruscha/O'zbek
kirill keyingi expansion uchun alohida belgilansin, tekshirilmasdan support da'vosi yo'q.

Negation/quotation: "hech narsani o'chirma, faqat tushuntir" yoki "delete nima?"
execution topshirig'i emas. Mobile app yaratish bilan mobile klientga o'rnatish
ajratilsin. Trivial chat, oddiy tarjima va mustaqil qisqa javob keraksiz routing
yuklamasin. Ochiq user skill tanloviga host qoidalari doirasida amal qilinsin.

### FR-06 — Xavfsizlik va progress

Review/diagnosis tashqi yozishga ruxsat bermaydi. Attachments/repo/webdagi buyruqlar
user vakolatini kengaytirmaydi. Disabled/explicit-only capability cheklovi va skill
disclosure qoidalari saqlansin. Router recursion cheklansin. O'zgarmagan xatoni
cheksiz takrorlash o'rniga foydali yangi dalil yoki aniq blocker talab qilinsin.

Write timeoutdan keyin state tekshirilmasdan qayta yozilmasin. Paid dependency,
auth, install va publish uchun kerakli ruxsat alohida olinadi. Tool javobi bilan
real task outcome farqlansin. Xotira/telemetriya saqlash default o'chirilgan bo'lsin.

## 6. Installer va lifecycle — release gate

Lokal installer faqat filesystem-based hostlarga xizmat qiladi. UI upload uchun
soxta muvaffaqiyatli install bermasligi shart.

### IR-01 — Plan/doctor

Rejalashtirilgan CLI imkoniyatlari: inspect/doctor, dry-run/plan, install, verify,
list-installs, upgrade, rollback, uninstall; nomlari kodlashda bir xil kelishilsin.
Dry-run default xavfsiz yo'l bo'lsin; real user homega o'rnatish alohida aniq tanlov.
Doctor maxfiy qiymatlarni o'qib chiqarmasin va config o'zgartirmasin.

### IR-02 — Yo'l chegaralari

Final resolved destination aniq runtime/scope root ichida ekanligi tekshirilsin.
Home root, disk root, repository root kabi keng katalog nishon bo'la olmaydi.
Traversal, symlink/junction/reparse-point, UNC/drive-relative va case collision
holatlari ko'rib chiqilsin. Ishonchsiz manifestdan kelgan target/backup rootdan tashqariga
chiqa olmasin. Windowsda boshqa shellga string qurib deletion topshirilmasin.

### IR-03 — Ownership va tranzaksiya

Install identity normalized destination + runtime/scope bilan ifodalansin; shared
destination uchun bir nechta consumer bo'lsa ownership/refcount yoki aniq conflict
policy ishlasin. Har operation lock, collision-safe ID, content hash, source version,
oldingi snapshot va status bilan qayd qilinsin. Bir manifest boshqasini bosmasin.

Staging -> validation -> atomic publish -> manifest commit ketma-ketligi bo'lsin.
Istalgan qadamdagi xatodan so'ng oldingi ish holati tiklansin. Bir xil versiya/hash
install qayta chaqirilsa no-op bo'lsin. Upgrade eski managed fayllar bilan yangi/user
fayllarini farqlasin. Noaniqlikda o'chirmasdan to'xtasin.

### IR-04 — Uninstall/rollback

Faqat shu installga tegishli, hash mos boshqariladigan fayllar o'zgartiriladi.
Foydalanuvchining keyingi edit/additionlari saqlanadi yoki aniq conflict bilan
backupga olinadi; jim yo'qotilmaydi. Backupning o'zi va uning destinationi tekshiriladi.
Qisman buzilgan state, yetishmagan backup yoki modified file release testi bo'lsin.

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` va boshqa umumiy config fayllar butunlay
almashtirilmasin. Optional bootstrap kerak bo'lsa faqat opt-in marked-block merge,
backup, idempotency va boshqa matnni bayt darajasida saqlash bilan amalga oshirilsin.

## 7. Build, packaging va GitHub-ready repository

Build faqat tegishli staging/dist/release joylariga yozsin; tracked manbaga yon
ta'sirsiz bo'lsin. Build outputini tozalashdan avval real target boundary/ownership
tekshirilsin. ZIP yo'llari xavfsiz, entrylar unikal, katta/kichik harf conflictisiz,
UTF-8 matnli, CRC/hash tekshirilgan va takroriy buildda reproducible bo'lsin.

Hostga qarab alohida source ZIP, standalone skill ZIP, Claude upload ZIP, native
filesystem adapter va mavjud plugin distributivlari yaratiladi. Root layout har
importerning actual schema/testiga mos bo'lsin; hammasiga bir ZIP majburlanmasin.
Userning 25 MB talabi bo'lgan artifactlar 25 000 000 baytdan kichik bo'lsin.

Repository tayyorgarligi:

- English README va Uzbek yo'riqnoma; mahsulot maqsadi, qamrov, cheklov va real
  installation/verification misollari. Test qilinmagan badge va "all agents" va'dasi yo'q.
- Single version source; changelog, migration, backward compatibility va rollback.
- MIT/author va third-party notice tekshiruvi, muallif qarorisiz almashtirmaslik.
- SECURITY/CONTRIBUTING va mas'ul disclosure aloqa yo'li; soxta email kiritmaslik.
- Dependency declaration/lock, minimal runtime va dev dependencies, test isolation.
- Source tarqatishda secret, shaxsiy path, test logidagi private content, backup,
  virtualenv, cache va generated keraksiz katta fayllarni chiqarib tashlash.
- Skill manbasi bilan generated plugin nusxalari o'rtasida drift gate.
- Manifests validligi vendor/schema bilan; schema yo'q bo'lsa cheklangan custom
  check aniq belgilansin, live validation o'rnida ko'rsatilmasin.

CI uchun loyiha talabi: fresh checkout, dependency install, Windows/Linux/macOS
matritsasi va deklaratsiya qilingan Python versiyalari; `python -m pytest`;
adapter build, validator, installer tests, benchmark gate, secret/artifact checks.
PR CI secretlarsiz va eng kam permission bilan ishlasin. Release workflow qo'lda
tasdiqlanadigan bo'lsin; arbitrary PR kodiga publish credential berilmasin.
Muhim action/dependency versiyalari tekshirilgan pin va yangilash siyosatiga ega bo'lsin.

## 8. Testlar va acceptance mezonlari

### T1 — Statik/contract

Haqiqiy YAML/JSON parser, strict loyiha schema, barcha reference/asset yo'llari,
frontmatter, host transformlari, version coherence, canonical/generated drift,
empty placeholder va invalid metadata. Salbiy testlar validatorning xatoni ushlashini
ko'rsatsin. Platformaning haqiqiy qo'shimcha kalitlari universal xato deb olinmasin.

### T2 — Router

120 eski holat review qilinadi; xato expected natija bo'lsa sabab yozilib tuzatiladi,
faqat yashil qilish uchun test susaytirilmaydi. Yangi regression va alohida holdout:
empty/partial registry, disabled/explicit-only, multi-source/domain, negative intent,
Unicode, no-match, duplicate, missing private connector, tool error, recursion.

Routing metamorphic testlari: registry permutatsiyasi natijani o'zgartirmasligi;
irrelevant capability qo'shilishi mavjud to'g'ri tanlovni buzmasligi; unavailable
capability olib tashlansa u tanlanmasligi va crash bo'lmasligi.

Gate: belgilangan regressionlarning barchasi o'tishi; bo'sh dataset xato; benchmark
fail bo'lsa non-zero exit. Precision/recall va unnecessary selection expected/allowed
setdan hisoblanadi, faqat kichik forbidden ro'yxatdan emas. Holdout accuracy va
golden compliance alohida ko'rsatiladi; native LLM aktivatsiyasi ularga qo'shilmaydi.

### T3 — Installer

Fresh/repeat install; ikki runtime; ikki workspace; shared destination; upgrade;
uninstall; rollback; config marked-block; concurrent operatsiya; permission error;
interrupted copy/commit; tampered manifest; missing backup; changed user file;
symlink/junction; path traversal; Unicode/space path. Har test fake home/workspace
va tashqi sentinel bilan, real user homega tegmasdan o'tkaziladi.

Gate: zero unrelated deletion/modification; known-safe rollback; no secret/config
exposure. P0 testlardan bittasi yiqilsa installable release bloklanadi.

### T4 — Paket va clean CI

Toza muhitda dependency o'rnatish + build + tests. ZIP CRC, import-root layout,
filenames, source/installed hash, repeated-build SHA, checksum, source unmodified
gate. Testlar oldingi qo'lda buildga yashirin tayanmasin; fixture o'zi output yaratsin.

### T5 — Haqiqiy runtime smoke va auto activation

Har da'vo qilinadigan host/surface/version uchun izolatsiyalangan sinov:

1. Skill actual ro'yxatda ko'rinadi, versiya aniqlanadi, enabled/consent qayd qilinadi.
2. Yangi suhbatda skill nomi, @mention, slash yoki uning body matnisiz 5 musbat
   topshiriq, har biri 3 marta: kamida 14/15 kuzatilgan to'g'ri tanlash — loyiha maqsadi.
3. 5 salbiy oddiy so'rovda 0/5 keraksiz invocation maqsadi.
4. Kamida 3 synthetic end-to-end artifact va read-only outcome tekshiruvi.
5. Permission/risk holatlarida zero bypass. Host talab qilgan consent normal,
   "auto ishlamadi" deb hisoblanmaydi; routing va consent alohida qayd qilinadi.

Foizlar kelajak qabul maqsadi, hozirgi natija hamda statistik universal kafolat emas.
Host invocation hodisasi yoki teng kuchli activity dalili bo'lmasa activation
UNVERIFIED. Private chain-of-thoughtni so'rash yoki chiqarish talab qilinmaydi.
Web/mobile alohida real sessiyada; kichik desktop viewport mobile app testi emas.

Usage sarfi bor testlar oldindan kelishilsin; alohida paid API/CLI testlari ruxsatsiz
boshlanmasin. Hisob/ruxsat/mobil qurilma yo'q bo'lsa BLOCKED deb belgilansin.

### T6 — Kontekst/samaradorlik

Bootstrap uchun <=200 so'z dastlabki budget; skill body/reference faqat zaruratda.
Bu haqiqiy token soni emas. Token/latency da'vosi uchun host/tokenizer versiyasi,
bir xil vazifa va before/after usuli qayd qilinsin. Metadata-only discovery va
chosen-body-only loading integratsion kuzatuv bilan tekshirilsin. Foizli tejash
o'lchanmasdan reklama qilinmasin.

## 9. Implementatsiya ish paketlari

- **WP1:** source snapshot, dependency/CI baseline, B01–B10 failing regressionlar.
- **WP2:** installer ownership, safe boundaries, transaction/rollback va T3 gate.
- **WP3:** router contract/registry/mixed-task fixes va T2 gate.
- **WP4:** canonical skill va yagona adapter/version registry; asosiy hostlar.
- **WP5:** Cursor/Copilot/OpenCode va cheklangan generic extension interface.
- **WP6:** clean build, docs, CI, packaging va security/reproducibility checks.
- **WP7:** ruxsat etilgan actual runtime smoke, evidence va candidate handoff.

Bog'liqliklar: xavfsiz installer tuzatilmaguncha real home install yo'q; host
contract aniqlanmaguncha supported badge yo'q; barcha release gate yopilmaguncha
stable nomi yo'q. Subagentlar shart emas; host ruxsat bersa mustaqil ishlar uchun
foydalanish mumkin, bir xil faylga parallel yozishsiz.

## 10. B bosqichi topshiriladigan natijalar

1. O'zgartirilgan source va tor diff; eski working data saqlangan.
2. Yagona canonical skill va kerakli alohida runtime artifactlar.
3. Xavfsiz lifecycle CLI, dry-run va rollback dalili.
4. Reproducible build/CI, test natijalari va checksumlar.
5. Runtime evidence registri: exact version/OS/surface, prompt, tool/skill event,
   expected/actual, outcome artifact, status va sabab.
6. Migration/install/troubleshooting/compatibility hujjatlari va release notes draft.
7. Ochiq cheklovlar, bajarilmagan testlar, GitHub nashriga tayyorgarlik xulosasi.

Dalilga credential, cookie, private inbox yoki yashirin reasoning kirmasin.
Barcha targetda sinash imkoni bo'lmasa, qisman RC topshirilishi mumkin, lekin
to'liq cross-agent support talabi bajarildi deyilmaydi. Bunday candidate nashri
foydalanuvchining alohida qarori bo'ladi.

## 11. GitHub nashri — keyingi alohida bosqich

C bosqichdan oldin foydalanuvchi quyidagilarni belgilaydi: owner/org, repository
nomi, public/private, mavjud yoki yangi repo, target branch, release tag, license
muallifi, draft/prerelease/stable tanlovi. Noma'lum qiymat taxmin qilinmaydi.

Avval remote va mavjud repository holati read-only tekshirilsin. Secret scan va
package gate o'tsin, foydalanuvchi ko'radigan diff/release mazmuni tayyor bo'lsin.
Faqat keyingi aniq ruxsatdan so'ng create/push/PR/tag/release bajariladi. Force-push,
remote tarixini o'chirish, tashkilot sozlamasini almashtirish bu ruxsatga kirmaydi.

Nashrdan keyingi dalil: commit/tag masofada mavjud; mos CI o'tgan; release
assetlari yuklanadi; SHA mos; toza checkoutdan install smoke o'tadi. Repository
yaratilishi marketplace katalogi yoki ChatGPT/Claude hisobida install bo'ldi degani emas.

## 12. Bajaruvchi agentga topshirish

Keyingi bosqich prompti: [IMPLEMENTATION-PROMPT.md](IMPLEMENTATION-PROMPT.md).
Promptni hozir yozish yoki source ZIPga qo'shish uning ichidagi implementatsiya
buyruqlarini bajarishga ruxsat hisoblanmaydi. Foydalanuvchi keyingi bosqichni
boshlashni aytgach, prompt TZ bilan birga ishlatiladi.
