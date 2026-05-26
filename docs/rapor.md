# Akıllı Site Yönetim Sistemi — Dönem Projesi Raporu

**Üniversite:** Gazi Üniversitesi  
**Bölüm:** Bilişim Güvenliği Teknolojisi  
**Ders:** İnternet Programcılığı  
**Proje Adı:** Site Management Flask  
**Geliştirici:** Begüm Düger  
**Tarih:** Mayıs 2026  
**Repository:** https://github.com/begumduger371-a11y/site_management_flask

---

## 1. Projenin Amacı ve Sistem Tanımı

Bu proje, çok katlı konut sitelerinin yönetim süreçlerini dijitalleştirmek ve yapay zeka destekli analiz araçlarıyla güçlendirmek amacıyla geliştirilmiştir. Geleneksel site yönetiminde arıza bildirimleri, aidat takibi ve duyuru yönetimi kağıt ortamında ya da dağınık dijital kanallar üzerinden yürütülmektedir; bu durum hem yöneticiler hem de sakinler açısından ciddi iletişim ve izlenebilirlik sorunlarına yol açmaktadır.

Geliştirilen **Akıllı Site Yönetim Sistemi**, bu sorunları tek bir merkezi web platformunda çözmektedir. Sistem; sakinlerin arıza bildirimlerini dijital olarak iletmesine, yöneticilerin aidat tahsilatlarını gerçek zamanlı takip etmesine ve duyuruları tüm sakine anlık olarak ulaştırmasına olanak tanımaktadır. Bunlara ek olarak, platforma entegre edilen **Akıllı Asistan** modülü, Google Gemini büyük dil modeli aracılığıyla İş Sağlığı ve Güvenliği (İSG) ile siber güvenlik konularında otomatik analiz raporları üretmektedir. Böylece sistem yalnızca idari bir araç olmaktan çıkarak, yöneticilere karar destek hizmeti de sunan proaktif bir platform hâline gelmektedir.

---

## 2. Mimari Özet

### Application Factory Pattern

Proje, Flask ekosisteminin önerdiği **Application Factory (Uygulama Fabrikası)** tasarım kalıbı üzerine inşa edilmiştir. Bu yaklaşımda Flask uygulama nesnesi (`app`) global düzeyde değil, `create_app()` adlı bir fabrika fonksiyonu içinde oluşturulmaktadır. Bu yapı sayesinde farklı ortamlar (geliştirme, test, üretim) için bağımsız konfigürasyonlar yüklenebilmekte; eklenti döngüsel bağımlılık sorunları ortadan kalkmakta ve birim testleri izole şekilde çalıştırılabilmektedir.

```
site_management_flask/
├── app/
│   ├── __init__.py       ← create_app() fabrika fonksiyonu
│   ├── models.py         ← SQLAlchemy 2.x veri modelleri
│   ├── routes.py         ← Blueprint tabanlı yönlendirmeler
│   ├── templates/        ← Jinja2 HTML şablonları
│   └── static/           ← CSS, JS varlık dosyaları
├── config.py             ← Ortam bazlı konfigürasyon sınıfları
├── run.py                ← Geliştirme sunucusu giriş noktası
└── init_db.py            ← Veritabanı başlatma scripti
```

### SQLAlchemy 2.x Mapped Standartları

Veri katmanı, SQLAlchemy'nin güncel **2.x Mapped** arayüzü ile yazılmıştır. Eski `Column(String)` söz dizimi yerine `Mapped[str]` tür ipuçleri tercih edilmiş, bu sayede hem tip güvenliği sağlanmış hem de modern Python statik analiz araçlarıyla tam uyumluluk elde edilmiştir.

```python
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default="resident")
```

Güvenlik katmanında Flask-Login oturum yönetimi ve Werkzeug'un `generate_password_hash` / `check_password_hash` fonksiyonları kullanılmıştır. Yapay zeka modülünde ise Google Gemini API'ye asenkron olmayan doğrudan HTTP çağrıları yapılmaktadır.

---

## 3. Vibe Coding Deneyimi

Bu proje, **Antigravity** yapay zeka kodlama asistanı eşliğinde *vibe coding* yöntemiyle geliştirilmiştir. Vibe coding; geliştiricinin geleneksel "satır satır kod yaz" rolünden çıkarak **mimar** konumuna geçtiği, yüksek seviyeli niyet bildirimlerinin ajana iletildiği ve ajanın bu niyetleri uygulanabilir koda dönüştürdüğü bir süreçtir.

Geliştirme sürecinde sabit kod yazmak yerine ajana şu türde talimatlar verildi:

> *"Flask 3.x ve SQLAlchemy 2.x kullanarak Application Factory pattern ile proje iskeletini oluştur. Kullanıcı rolleri yönetici ve sakin olarak ayrılsın."*

> *"Bootstrap 5 ve glassmorphism tasarım diliyle premium görünümlü bir login sayfası oluştur."*

Bu yaklaşım, geliştirme hızını dramatik biçimde artırırken mimari kararların insan tarafında kalmasını sağladı. Ajan her adımda plan belgeleri (`implementation_plan.md`) üretti; onaylanmadan kod yazımına geçmedi. Bu döngü, yazılım geliştirmede insan-AI iş birliğinin somut bir örneğini ortaya koydu.

---

## 4. Antigravity'de En Faydalı İki Özellik

### Plan Modu (Planning Mode)

Antigravity'nin **Plan Modu**, büyük veya karmaşık görevlerde doğrudan kod yazmak yerine önce kapsamlı bir `implementation_plan.md` belgesi oluşturmasını sağladı. Bu belge; değiştirilecek dosyaların listesini, benimsenen mimari kararları ve doğrulama adımlarını içermekteydi. Kullanıcı onayı alınmadan hiçbir değişiklik uygulanmadı. Bu yaklaşım, "ajanın tahmin edilemez değişiklikler yapması" riskini ortadan kaldırdı ve geliştirme sürecini şeffaf, izlenebilir ve geri alınabilir kıldı.

### Sandbox Güvenlik Duvarı (Permission Sandbox)

Ajan, komut çalıştırmadan önce kullanıcıdan açık izin talep etti. `pip install`, `python init_db.py` veya `git push` gibi kritik komutlar hiçbir zaman sessizce yürütülmedi; her biri önce kullanıcıya gösterildi ve onaylandıktan sonra çalıştırıldı. Bu güvenlik duvarı, özellikle sistem ortamını etkileyen komutlarda kontrol hissini tamamen kullanıcıda bıraktı ve yanlışlıkla yapılabilecek geri dönüşü zor değişikliklerin önüne geçti.

---

## 5. Ajanın Yakaladığı ve Birlikte Düzelttirdiğimiz Üç Kritik Hata

### 5.1 Windows PATH Ortam Değişkeninde Python Bulunamaması

Proje kurulumunun başında ajan, `python` komutunu çalıştırmayı denediğinde komut bulunamadı hatası aldı. Bunun nedeni, Python kurulumunun Windows sistem `PATH` değişkenine eklenmemiş olmasıydı. Sorun, Python Installer'ın "Add Python to PATH" seçeneği işaretli hâlde yeniden çalıştırılmasıyla ve ardından PowerShell oturumunun yenilenmesiyle çözüldü. Ajan bu sorunu tespit ederek alternatif çözüm yollarını sıralı biçimde önerdi.

### 5.2 Giriş Formunda `email-validator` Paketinin Eksik Olması

Flask-WTF'nin e-posta doğrulama alanı (`EmailField`), arka planda `email-validator` adlı harici bir Python paketine ihtiyaç duymaktadır. Bu bağımlılık `requirements.txt` dosyasına başlangıçta eklenmemişti; dolayısıyla kullanıcı kayıt ve giriş formları `ImportError` fırlatarak çöküyordu. Hata, `pip install email-validator` komutuyla ve `requirements.txt` dosyasına bu bağımlılığın eklenmesiyle kalıcı olarak giderildi.

### 5.3 SQLAlchemy 1.x Eski Söz Diziminin Önerilmesi

Ajanın veri modellerini ilk oluşturduğunda `db.Column(db.String(120))` biçimindeki SQLAlchemy 1.x söz dizimini kullandığı görüldü. Oysa proje başından itibaren SQLAlchemy 2.x standardı hedeflenmekteydi. Kullanıcının bu uyumsuzluğu fark ederek belirtmesi üzerine ajan tüm modelleri `Mapped[str]` ve `mapped_column()` arayüzüne yeniden dönüştürdü. Bu düzeltme hem ileriye dönük uyumluluğu hem de tip güvenliğini güvence altına aldı.

---

## 6. Yapay Zeka Olmadan Tahmini Geliştirme Süresi

Bu projenin yapay zeka desteği olmaksızın tek bir geliştirici tarafından sıfırdan yazılması durumunda tahmini süre şu şekilde hesaplanmaktadır:

| Bileşen | Tahmini Süre |
|---|---|
| Proje mimarisi ve iskelet kurulumu | 4–6 saat |
| SQLAlchemy model tasarımı | 3–4 saat |
| Flask-Login / güvenlik entegrasyonu | 4–5 saat |
| HTML şablonları ve CSS tasarımı | 8–12 saat |
| Gemini API entegrasyonu | 3–5 saat |
| Veritabanı başlatma ve test | 2–3 saat |
| Git kurulumu ve GitHub yükleme | 1–2 saat |
| **Toplam** | **~25–37 saat** |

Antigravity ile gerçekleştirilen geliştirme süreci ise bir iş günü içinde tamamlandı. Bu karşılaştırma, yapay zeka destekli geliştirmenin tekrar eden ve kalıp tabanlı kodlama görevlerinde sağladığı verimlilik artışını somut biçimde ortaya koymaktadır.

---

## 7. Projenin Bir Sonraki Adımı

Projenin sürdürülmesi hâlinde öncelikli geliştirme hedefi, **aidat ödeme modülüne gerçek bir ödeme altyapısı entegre etmektir.** Bu hedef kapsamında Stripe veya İyzico gibi bir ödeme geçidi API'si sisteme bağlanacak; sakinler aidat borçlarını platform üzerinden kredi kartıyla ödeyebilecek ve yöneticiler anlık tahsilat raporlarına erişebilecektir.

Buna paralel olarak, arıza bildirim modülüne **görüntü yükleme** ve **durum takip** (beklemede / işlemde / çözüldü) özellikleri eklenerek sistemin pratik kullanımı güçlendirilecektir. Son olarak, üretim ortamına geçiş için SQLite yerine PostgreSQL, geliştirme sunucusu yerine Gunicorn ve bir bulut platformu (Render veya Railway) kullanılması planlanmaktadır.

---

*Bu rapor, Bahar 2026 dönemi internet programcılığı projesinin akademik değerlendirmesi amacıyla hazırlanmıştır.*
