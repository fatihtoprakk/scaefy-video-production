# Scaefy Video Production

[English](README.md) · **Türkçe**

**Kod ile üretilen video için bir beceri paketi — motordan bağımsız, çekirdeği ücretsiz, ve göz kararı yerine ölçümle denetlenen.**

Kodlama ajanınız filmi kod olarak yazar. Zaman çizelgesi her kareyi zamanın saf bir
fonksiyonu olarak çizer, kareler gerçek bir tarayıcıdan alınır, ffmpeg kodlar, ses
mikslanır ve teslim, sessizce geçmeyip yüksek sesle hata veren bir kalite kapısından
geçer. Zaman çizelgesi editörü yok, keyframe sürükleme yok, "bana iyi göründü" yok.

> **v0.1.0** — 10 beceri, gerçek tarayıcıda doğrulanmış bağımlılıksız 30 saniyelik bir
> örnek film ve her push'ta tüm kapıları çalıştıran bir CI hattı.
> [GitLab](https://gitlab.com/fatihtoprak/scaefy-video-production) (ana) ·
> [GitHub](https://github.com/fatihtoprakk/scaefy-video-production) (ayna)

---

## Çalıştığını görün

`example/` içinde **30 saniyelik, 1920x1080, 25 fps** tam bir film var — bu paketi
yürüten ajans için yapılmış gerçek bir film. **Sıfır bağımlılık:** `example/index.html`
dosyasını tarayıcıda açın, oynar. Derleme adımı yok, paket kurulumu yok, ağ yok.

```bash
open example/index.html

# kare al ve ölç
PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
URL="file://$PWD/example/index.html?clean=1" \
node tools/shots.mjs shots 2 6 12 18 24 28
python3 tools/check-frames.py shots/*.png --theme light
```

Filmin ekran metni Türkçe, İngilizce altyazıları yanında geliyor. Paketin kendi
metinleri İngilizcedir.

---

## Bu neden var

Çoğu "yapay zeka ile video" aracı sizi tek bir motora, tek bir sağlayıcıya veya ağır
bir çatıya bağlar. Bu paket onun yerine üç söz veriyor:

1. **Motordan bağımsız.** Bir film tek bir motorla üretilir — hızlı iterasyon gereken
   tek seferlik işler için HTML + GSAP, tekrar tekrar render edilecek veri şablonları
   için Remotion, fotogerçekçi görüntü için yapay zeka üretimi. Paket üçünü de öğretir
   ve tek bir filmde asla karıştırmaz.
2. **Çekirdeği ücretsiz ve çevrimdışı.** Varsayılan hat API anahtarı, hesap ve ağ
   gerektirmez. Yapay zeka görüntüsü, ekleyebileceğiniz, atlayabileceğiniz veya yerel
   olarak çalıştırabileceğiniz isteğe bağlı bir katmandır.
3. **Ölçümle denetlenen.** Ses seviyesi, true peak, kare bütünlüğü, güvenli alan taşması
   ve determinizm, sıfırdan farklı çıkış kodu döndüren betiklerle denetlenir — "dikkatli
   olun" diyen bir paragrafla değil.

---

## Sıfır maliyet garantisi

| Katman | Maliyet | Ağ | Kapsam |
|---|---|---|---|
| **A · Kod ile üretilen grafik** (çekirdek) | **Ücretsiz** | **Yok** | Kinetik tipografi, sayaçlar, veri barları, isim kartları, logo reveal, end card, altyazı, geçişler, tam motion-graphics filmleri |
| **B · Yapay zeka görüntüsü** (isteğe bağlı) | GPU varsa ücretsiz, yoksa ücretli | Var | Fotogerçekçi b-roll, karakterler, sahneler |

Katman B'nin üç yolu var ve seçimi siz yaparsınız:

| Yol | Maliyet | Donanım | Örnek |
|---|---|---|---|
| Yerel açık kaynak | **Ücretsiz** | GPU şart | Wan 2.1/2.2, Hunyuan Video, LTX Video, Flux |
| Ücretsiz kota | Ücretsiz (sınırlı) | Yok | Sağlayıcı deneme kredileri |
| Ücretli API | Ücretli | Yok | Seedance 2.0, Veo, Kling |

Bir brief yapay zeka görüntüsü istiyor ama ne GPU ne kotanız varsa, ajan **Katman A'ya
düşer ve bunu açıkça söyler** — sessizce ücretli bir servise bağlanmaz.

---

## Hızlı başlangıç

Gereksinimler: **Node 18+**, **Python 3.10+**, **ffmpeg**. Hepsi yerel, hepsi ücretsiz.

```bash
git clone <bu-repo>
cd scaefy-video-production

# çalışan bir ffmpeg çöz (varlığı değil, çalışmayı test eder)
FF="$(tools/ffmpeg.sh)" && echo "ffmpeg OK"

# tüm kalite kapılarını çalıştır
bash tools/verify.sh
```

DSH ajan preset'i olarak kurmak için:

```bash
mkdir -p ~/.dsh/.agent-presets
cp -R . ~/.dsh/.agent-presets/scaefy-video-production
```

[Agent Skills](https://agentskills.io) standardını destekleyen herhangi bir ajanla
kullanmak için:

```bash
npx skills add <bu-repo>
```

---

## Şu prompt'ları deneyin

Aşağıdakilerden herhangi birini ajanınıza yapıştırın. Hepsi bir insanın gerçekten
konuştuğu gibi yazıldı, bir kılavuzun okunduğu gibi değil — beceri açıklamaları tam da
bunları yakalamak için yazıldı.

**Harcamadan önce planla.** Değiştirmesi en ucuz şey kurgu kararıdır.

> Sitemiz için 30 saniyelik bir lansman videosu planla. Önce brief ve zamanlı bir
> animatik ver — tempoyu onaylamadan hiçbir şey render etme.

**Bir siteyi filme çevir.**

> Bu açılış sayfasını, sitenin kendi görsellerini kullanan 20 saniyelik bir tura çevir.

**Kırpma olmayan dikey kesit.**

> `out/` içinde bitmiş bir master var. Bana 15 saniyelik 9:16 sürümünü ver. Dikey için
> yeniden kompoze et — bir merkez kırpmanın neyi keseceğini söyleyemiyorsan,
> kontrol etmemişsin demektir.

**Karakteri tutarlı tut.**

> Burada dört ürün fotoğrafı var. Bir look bible yaz ve bunlardan video üretmeden önce
> kareleri bana göster.

**Sesi düzelt, sonra kanıtla.**

> Müzik anlatıcıyla çakışıyor. Konuşma altında müziği geri çek ve -14 LUFS integrated
> ile true peak -1 dBTP altında hedefle, sonra bana ölçümü göster.

**Sessiz akışta da okunan altyazı.**

> İngilizce altyazı ekle ve her repliğin okuma hızını söyle. Saniyede 17 karakterin
> üstüne çıkmasın.

**Sadece bu dosyada neyin bozuk olduğunu söyle.**

> `out/final.mp4` dosyasını 1080p teslim spesifikasyonuna göre denetle ve başarısız
> olanları listele.

**Birden fazla dil.**

> Türkçe filmi al ve master'a dokunmadan İngilizce altyazılı bir sürümünü ver.

### Bu prompt'ları işe yaratan ne

Paketin becerileri tam ifadeye değil **tetikleyicilere** göre yönlenir. Bir becerinin
adını söylemeniz gerekmez. Ama üç alışkanlık daha iyi sonuç verir:

- **Önce ucuz olanı isteyin.** "Render'dan önce brief ve animatik" plan yanlışsa saatler
  yerine dakikalar kaybettirir.
- **Ölçümü isteyin.** "Bana sayıyı göster" bir görüşü denetime çevirir; `qc.py` zaten
  o sayıyı üretiyor.
- **Yöntemi değil kısıtı söyleyin.** "Yeniden kompoze et, kırpma" size tasarlanmış bir
  dikey sürüm verir; "dikey yap" size merkez kırpma verir.

---

## Beceriler

### Birinci taraf

| Beceri | Ne yapar |
|---|---|
| `brand-asset-intake` | Dağınık marka varlıklarını doğrulanmış, makine-okunur token'lara çevirir: palet çıkarımı, WCAG kontrast, 16:9/9:16 için punto ölçeği ve güvenli alanlar. Eksik logoyu veya rengi **uydurmayı reddeder**. |
| `video-brief-and-storyboard` | Belirsiz bir isteği karar vermeye hazır bir brief'e, beat sheet'e, storyboard'a ve zamanlı bir animatiğe çevirir — üretimden önce bir onay kapısıyla. |
| `video-motion-graphics` | Grafik katmanını kod ile üretir: kelime inşası tipografi, portre mozaiği, veri ve sayaç barları, isim kartları, logo reveal, end card — 25 fps kare-hassas. |
| `ai-cinematic-broll` | Sağlayıcıdan bağımsız yapay zeka görüntüsü: look bible, karakter tutarlılığı, stills-first → image-to-video, kabul QC. |
| `voiceover-and-audio-mix` | Bir metni kare-hassas 25 fps anlatım repliklerine ve üç katmanlı ses tasarımına çevirir; müzik yatağı, ducking ve loudness hedefi. |
| `kinetic-captions-and-subtitles` | Altyazıları yazar, zamanlar, biçimlendirir ve teslim eder — okunabilirlik sınırları, SRT/VTT, burn-in ve çok dilli sürümler. |
| `multiformat-recomposition` | Çok-format problemini çözer: bir sahnenin yeni en-boy oranı için **yeniden kompoze mi edileceğine yoksa türetileceğine** kare kare karar verir. |
| `video-post-delivery` | Master'ları kesin teslim spesifikasyonlarına göre kodlar, normalize eder, altyazılar ve QC'ler; kısa ve dikey sürümleri türetir. Bozuk dosya teslim etmek yerine yüksek sesle başarısız olur. |

### Vendored (MIT, atıflı)

| Beceri | Kaynak |
|---|---|
| `bang-motion` | HTML + CSS + GSAP ile sinematik motion graphics — Bang Tutorial |
| `remotion-marketing-video` | Remotion + React ile pazarlama videosu iş akışı — Sourabh |

---

## Araçlar

| Araç | İş |
|---|---|
| `tools/ffmpeg.sh` | **Çalışan** bir ffmpeg çözer — varlığı değil, çalışmayı test eder |
| `tools/shots.mjs` | Tam saniyelerde kare alır; `ready` ve `seekAsync` bekler |
| `tools/export-frames.mjs` | Kodlama girdisi için tam kare dizisi üretir |
| `tools/check-frames.py` | Siyah/donmuş kare, güvenli alan taşması, mürekkep oranı, kontrast |
| `tools/contact-sheet.py` | Karelerden sayısal zaman sırasına göre inceleme sayfası kurar |
| `tools/probe-layout.mjs` | DOM'dan **gerçek harf kutularını** ölçer — punto tahmin edilmez |
| `tools/verify.sh` | Tek komutla tüm kapıları çalıştırır |

Sürüm altyapısı `ci/` altındadır: film yapmanın parçası olmadığı için `tools/` içinde
durmaz.

---

## Teslim matrisi

| Çıktı | Süre | Kare | Kodek / ayarlar |
|---|---|---|---|
| Master | 60 sn | 1920×1080 veya 3840×2160 | H.264 High, yuv420p, 25 fps CFR |
| Etkinlik yedeği | 60 sn | aynı | H.264 yuv420p + AAC, sabit kare hızı |
| Sessiz izleme | 60 sn | aynı | Master + gömülü altyazı |
| Kısa kesit | 30 sn | 16:9 | Master'dan türetilir |
| Teaser | 15 sn | 9:16 | Yeniden kompoze edilir, kırpılmaz |
| Dikey tam | 60 sn | 1080×1920 | Grafikler dikey için yeniden kompoze edilir |

Renk uzayı Rec.709 / Gamma 2.4. Ses AAC 48 kHz, 320 kbps stereo.
Ses seviyesi hedefi **-14 LUFS integrated**, true peak **≤ -1 dBTP**.

---

## İlgili çalışmalar

Bu paket bilinçli olarak hafif ve izin verici lisanslıdır. Şu projeler komşu
problemleri çözüyor ve ilginizi hak ediyor:

- [**OpenMontage**](https://github.com/calesthio/OpenMontage) — her şey dahil bir
  ajanik video üretim çatısı (Python, 100+ araç, 60+ sağlayıcı), **AGPLv3** lisanslı.
  Ücretsiz yolu — çevrimdışı Piper TTS, açık arşiv görüntüsü, yerel GPU üretimi — bu
  paketin üzerine kurulduğu mimariyi bağımsız olarak doğruluyor. Bağımlılık **değildir**
  ve hiçbir kod paylaşılmaz: AGPL ve MIT eserleri ayrı kalır.
- [**sub-level/marketing-videos**](https://github.com/sub-level/marketing-videos) — MIT
  lisanslı, mükemmel vaka analizleri olan bir Remotion + yapay zeka görüntü hattı.
- [**pexoai/pexo-skills**](https://github.com/pexoai/pexo-skills) — çok modelli bir
  bulut üretim API'sini sarmalayan MIT becerileri.

---

## Lisans

MIT — bkz. `LICENSE`. Vendored üçüncü taraf beceriler kendi MIT lisanslarını ve
atıflarını korur; bkz. `THIRD_PARTY_NOTICES.md`.

`example/` filmindeki Scaefy adı ve logosu sahiplerinin ticari markasıdır ve bu deponun
MIT lisansı kapsamında **değildir**. Fork ederseniz örnek filmin marka varlıklarını
kendi varlıklarınızla değiştirin — beceriler marka-nötrdür ve token'larınızı
`brand-asset-intake` üzerinden bekler.
