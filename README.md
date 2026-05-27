WSN Hava Savunma Radar Simülasyonu
Bu proje, Python üzerinde pygame ve simpy kütüphaneleri kullanılarak geliştirilmiş, Kablosuz Sensör Ağları (WSN - Wireless Sensor Networks) tabanlı bir hava savunma radar simülasyonudur.

Simülasyon, düşman hava araçlarını tespit etmek üzere konumlandırılmış süpersonik radar sensörlerinden oluşur. Ağ yapısı, sensör düğümleri, Küme Başları (Cluster Heads) ve bir Merkezi Komuta (Central Command) birimi ile hiyerarşik olarak tasarlanmıştır.

Sistemin Temel Özellikleri
Süpersonik Radar Ağı: Yüksek hızda veri taraması ve algılama yaptığı varsayılan radar düğümleri, kapsama alanlarına giren hedeflerin koordinatlarını anlık olarak hesaplar.

Modüler ve Hata Toleranslı (Fault-Tolerant) Mimari: Sistem esnek bir yapıda kurgulanmıştır. Ağı oluşturan radarlardan bir veya birkaçının bozulması, imha edilmesi ya da çevrimdışı kalması durumunda savunma ağı çökmez. Diğer aktif sensörler veri toplamaya ve bağlı oldukları Küme Başlarına sinyal göndermeye devam eder.

Merkezi Komuta ve Gerçek Zamanlı Log: Küme başlarında toplanan veriler Komuta Merkezine iletilerek sağ paneldeki canlı koordinat akışında listelenir.

Etkileşimli Saha: Radar konumları statik değildir. İhtiyaç durumunda (örneğin bozulan bir sensörün yerini doldurmak veya kör noktaları kapatmak için) sensörler harita üzerinde fare ile sürüklenerek yeniden konumlandırılabilir.

Gereksinimler ve Kurulum
Projeyi çalıştırmak için sisteminizde Python 3.x yüklü olmalıdır. Gerekli bağımlılıkları yüklemek için aşağıdaki komutu terminalinizde çalıştırın:

Bash
pip install pygame simpy
Çalıştırma
Bağımlılıkları kurduktan sonra projeyi başlatmak için:

Bash
python dosya_adi.py
(Dosya_adi.py kısmını kendi Python dosyanızın ismiyle değiştirin.)

Kontroller
Sensör Taşıma: Farenin sol tuşuna basılı tutarak herhangi bir radar sensörünü (R-1, R-2 vb.) harita üzerinde yeni bir konuma sürükleyebilirsiniz.

Duraklat / Devam Et: Simülasyonu ve zaman akışını durdurmak veya yeniden başlatmak için BOŞLUK (Space) tuşunu kullanın.

Boyutlandırma: Uygulama penceresi dinamik olarak boyutlandırılabilir; ızgara sistemi ve komuta merkezi arayüzü yeni ekran boyutuna göre otomatik olarak ölçeklenir.
