# RC1 boshlang'ich tahlili

Sana: 2026-08-31. Usul: ZIP yaxlitligi, fayl tarkibi va kodni statik o'qish.
Repo kodi, installer, testlar va CI bu bosqichda ishga tushirilmadi.

## Aniq boshlang'ich nusxa

- Fayl: `ai-core-operating-protocol-v2.0.0-rc1-source.zip`.
- Hajm: 45 849 bayt.
- SHA-256: `db74c974aa3cf93da0d8821477d064c494a4fa9ccb217f10542462e0ad40cf5a`.
- 58 ta haqiqiy fayl va 30 ta katalog entry. Katalogni fayl deb hisoblamaslik kerak.
- Golden datasetda 120 ta yozuv va 120 ta turli request matni.
- `core/schemas/capabilities.json` ichida 15 ta namunaviy capability yozuvi.
- ZIP CRC o'tdi; yo'l traversal, symlink va takroriy entry topilmadi.

Bu sonlar skill soni emas. 120 ta ssenariy 120 ta bajarilgan live sinov degani emas.

## Saqlanishi kerak bo'lgan asos

Canonical skill, reference router, generated adapterlar, release skriptlari va
testlar alohida joylashtirilgan. README reference benchmark real dunyodagi universal
aniqlik isboti emasligini to'g'ri aytadi. Ushbu ajratish qayta ishlashda saqlansin.
MIT va muallif yozuvi o'zboshimcha almashtirilmasin; nashrdan oldin egasi tasdiqlasin.

## Tuzatishlar uchun dalillar

### B01 — Uninstall yo'liga ishonish: release blocker

`installers/install.py:40-43`: destination JSONdan olinib, canonical containment,
ownership yoki reparse-point tekshiruvisiz `shutil.rmtree(dest)` ga berilgan.
O'zgartirilgan manifest boshqa katalogni ko'rsatsa, funksiya o'sha joyni o'chirishga
urinadi. Buni real foydalanuvchi katalogida sinash mumkin emas.

Qabul testi: vaqtinchalik sandbox ichidagi tashqi sentinel katalogga yo'naltirilgan
soxta manifest rad etilsin; sentinel baytlari o'zgarmasin. Symlink/junction va
manifestdagi backup yo'li ham alohida tekshirilsin.

### B02 — Bitta manifest bir necha o'rnatishni yo'qotadi: release blocker

`installers/install.py:32-33,62`: runtime/scope/workspace farqiga qaramasdan default
state ichida bitta `install-manifest.json` yoziladi. Keyingi o'rnatish oldingi
hisobni almashtiradi. Codex/Gemini kabi umumiy destination ishlatadigan runtime'lar
bir-birining fayllariga egalik da'vo qilishi mumkin.

Talab: normalized destination asosida ownership, ko'p install yozuvi, collision
policy, parallel install lock va har install uchun mustaqil rollback.

### B03 — Foydalanuvchi keyingi o'zgarishlari saqlanmaydi: release blocker

`installers/install.py:30,43-46`: copy merge qiladi, uninstall esa butun destinationni
olib tashlaydi. O'rnatishdan keyin qo'shilgan/o'zgartirilgan fayl hash tekshiruvisiz
yo'qolishi mumkin. Eski fayllar upgrade paytida keraksiz holda qolishi ham mumkin.
`installers/install.py:26-29` da backup nomi sekund aniqligida; bir sekunddagi
takroriy urinish collision berishi mumkin.

Talab: content manifest, idempotency, staging va atomik commit, collisionga chidamli
backup ID, changed-user-file preservation, uzilgan install/rollback testlari.

### B04 — Qisman registry uchun StopIteration

`core/router/router.py:119-130`: maxsus id qidiruvlari `next(...)` defaultisiz.
Masalan, bo'sh registry + Gmail so'rovi istisnoga olib keladi. Hostda Gmail mavjud
bo'lmasligi normal holat. `Capability` modelida installed/enabled/permission holati
ham yo'q (`:9-15`).

Talab: mavjud nomlar bilangina ishlash, missing/unavailable natijasini aniq qaytarish,
permission qarorini hostga qoldirish; bo'sh, qisman va disabled registry testlari.

### B05 — Har layerga faqat bitta capability aralash vazifani kesadi

`core/router/router.py:108-115,133`: domain va source uchun birgina g'olib saqlanadi.
PDF -> Word yoki inbox -> calendar kabi haqiqiy ikki bosqichli ishda ikkinchi
zarur capability yo'qolishi mumkin. `test_duplicate_layer_is_suppressed` shu cheklovni
mustahkamlaydi; distinct capability bilan haqiqiy duplicate ajratilishi kerak.

Talab: task-step asosidagi minimal qamrov, tartib/dependency, dedup by identity;
cheksiz ko'p tool tanlash bilan almashtirmaslik.

### B06 — Benchmark muvaffaqiyatsizlikni exit code orqali bermaydi

`scripts/benchmark.py:17-22`: failed_cases hisoblanadi, faqat JSON chiqariladi;
muvaffaqiyatsiz ssenariylar uchun non-zero chiqish sharti yo'q. Shu skriptga
tayanadigan CI qadamining yashil bo'lishi benchmark o'tganini bildirmaydi.
Golden tekshiruv faqat sanab berilgan forbidden idlarni hisoblaydi; boshqa ortiqcha
tanlovlar avtomatik false positive sifatida qayd qilinmaydi.

Talab: majburiy gate va exit code, explicit expected/allowed set, empty dataset
himoyasi, alohida holdout va o'lchanadigan keraksiz activation ko'rsatkichi.

### B07 — Xavfsizlik testi xavfli xatti-harakatni tekshirmaydi

`tests/security/test_security.py:18-22` faqat ikkita satr yo'qligini tekshiradi;
installerda mavjud `shutil.rmtree(dest)` bu filtrlardan o'tadi. Regex yordamchi
tekshiruv bo'lishi mumkin, lekin uninstall xavfsizligining isboti emas.

Talab: real filesystem fixture, sentinellar, invalid manifest, collision, symlink,
post-install o'zgarish va rollback xatti-harakatlarini tekshirish.

### B08 — Toza muhitdagi CI reproduktivligi kafolatlanmagan

`.github/workflows/ci.yml:7-14`: pytest chaqiriladi, ammo dependency install qadami
yo'q. Arxivda dev dependency lock/manifest ham yo'q. Hozirgi hosted image tasodifan
pytest bersa ham bu dependency deklaratsiyasi o'rnini bosa olmaydi. CI faqat Ubuntu
va Python 3.12ni ko'rsatadi; Windows/macOS mosligi bundan kelib chiqmaydi.

Talab: clean environment install, qo'llab-quvvatlanadigan OS/Python matritsasi,
test isolation, dependency declaration, minimal CI permissions va artifact dalili.

### B09 — Build va release manbaga yon ta'sir qiladi

`scripts/package_release.py` oldin `sync_marketplaces()` ni chaqiradi; u repository
ichidagi marketplace, plugin manifestlari va skill nusxasini qayta yozadi.
`build_adapters.py` va `sync_marketplaces.py` plugin metadata uchun alohida
generatorlarga ega; versiya bir necha skriptga hardcode qilingan.

Talab: yagona version/adapter registry, faqat staging/dist ga build, source drift
gate, reproduktiv ZIP, o'chirishdan avval real target tekshiruvi.

### B10 — Paket mavjudligi runtime mosligi isboti emas

Compatibility testlari ko'p joyda manifest/fayl mavjudligini tekshiradi. Claude
web upload, Claude Code plugin, Codex local/cloud, Gemini CLI, Antigravity IDE va
generic instruktsiya turli mahsulot sirtlaridir. `verified` sarlavhasi ostida
hujjatni o'qish bilan live activation alohida belgilanmagan.

Talab: documented, generated, static-tested, discovered, activation-tested va
blocked/unverified holatlarini ajratish. Native routingga ulanmagan reference
routerni universal ishlaydigan runtime deb reklama qilmaslik.

## Izoh

Bu tahlil to'liq pentest, litsenziya ekspertizasi yoki bajarilgan test hisobotining
o'rnini bosmaydi. B01–B10 implementatsiya bosqichida avval xavfsiz failing testlar
bilan tasdiqlanadi, keyin tor tuzatish va regressiya tekshiruvi bajariladi.
Eski `docs/superpowers/plans/` ichidagi agentlarga qaratilgan buyruqlar bu hujjatni
tayyorlashga yoki implementatsiyani hozir boshlashga ruxsat sifatida olinmadi.
