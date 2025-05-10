---
 * Daha iyi erişim için sadece son sürüm dosyalar yüklenmiştir (version4).
 * Only the latest version files have been uploaded for better access (version4).
---
 * Bu proje deneysel amaçlıdır (Geliştirici ZAYN)
 * This project is experimental (Developer: ZAYN)
---

# SwarmMind: Belirme, Adaptasyon ve Ko-Evrim Simülasyonu

# SwarmMind: Emergence, Adaptation, and Co-evolution Simulation

---

## Proje Özeti (Türkçe)

SwarmMind, kolektif davranışların (sürü zekası), basit kurallardan karmaşık düzenlerin doğuşunun (belirme), yapay sinir ağlarının evrimi yoluyla çevresel adaptasyonun (NEAT - NöroEvrim) ve rekabet ortamında stratejilerin karşılıklı evrimleşmesinin (ko-evrim) incelendiği, Python tabanlı bir simülasyon projesidir. Proje, temel sürüklenme (flocking) davranışından başlayarak, yem toplama ve dolaylı iletişim (stigmergy) gibi görevlere, ardından tek bir sürünün adaptif evrimine ve nihayetinde iki rakip sürünün ko-evrimsel mücadelesine kadar uzanan, giderek artan karmaşıklıkta dört ana sürümden oluşmaktadır. SwarmMind, Yapay Yaşam (ALife), karmaşık sistemler ve yapay zeka prensiplerini görsel ve etkileşimli bir şekilde keşfetmek için eğitici bir araç ve bir deney platformu sunar. Görselleştirme için Pygame, evrimsel hesaplama için NEAT-Python kütüphaneleri kullanılmıştır. Bu proje, basit bireylerin etkileşiminden nasıl karmaşık ve "akıllı" görünen kolektif sonuçlar doğabileceğini merak eden herkes için ilginç bir keşif sunmaktadır.



## Project Summary (English)

SwarmMind is a Python-based simulation project exploring the fascinating concepts of collective behavior (swarm intelligence), the emergence of complex patterns from simple rules (emergence), environmental adaptation through the evolution of artificial neural networks (NEAT - NeuroEvolution), and the reciprocal evolution of strategies in a competitive setting (co-evolution). The project consists of four main versions of increasing complexity, starting from basic flocking behavior, moving through foraging and indirect communication (stigmergy), then to the adaptive evolution of a single swarm, and finally culminating in the co-evolutionary struggle between two competing swarms. SwarmMind offers an educational tool and an experimental platform for visually and interactively exploring principles of Artificial Life (ALife), complex systems, and artificial intelligence. It utilizes Pygame for visualization and the NEAT-Python library for evolutionary computation. This project provides an interesting exploration for anyone curious about how complex and seemingly "intelligent" collective outcomes can arise from the interactions of simple individuals.



---

## Sürümler ve Özellikler (Türkçe)

Depo, her biri bir öncekinin üzerine inşa edilen birden fazla SwarmMind sürümünü içerir:

### Sürüm 1: Belirme (Emergence) (Klasör: `swarm_mind_v1`)

* **Konsept:** Temel kurulum ve basit yerel kurallardan doğan kolektif düzen. Bireylerin sadece komşularına bakarak nasıl tüm sürünün koordine hareket etmesini sağladığını gösterir.
* **Özellikler:**
    * Temel fizik motoru (pozisyon, hız, ivme) ve 2D vektör matematiği (`vector.py`).
    * Craig Reynolds'ın klasik Boids algoritması: Ayrılma (çok yaklaşma), Hizalanma (aynı yöne git), Bütünleşme (merkeze yaklaş).
    * Ajan sayısı, hız limitleri, algılama mesafeleri, kuralların etki gücü gibi birçok parametrenin `settings.py` üzerinden ayarlanabilmesi.
    * Basit Pygame görselleştirmesi: Ajanlar 2D ekranda gezinir, kenarlardan dönerler.
* **Amaç:** Simülasyon altyapısını kurmak ve merkezi bir kontrol olmadan kendi kendine organize olabilen sürü davranışını görselleştirmek.

### Sürüm 2: Yem Toplama ve Stigmergy (Klasör: `swarm_mind_v2`)

* **Konsept:** Sürüye bir görev vermek (yem toplama) ve karıncaların feromon izleri gibi, ajanların çevreye bıraktıkları işaretlerle haberleşmesini (stigmergy) sağlamak.
* **Özellikler:**
    * Görev: Rastgele beliren yem kaynaklarını bul, merkezi bir yuvaya taşı.
    * Ajan durumları: `YEM_ARAMA` ve `YUVAYA_DONME` durumları arasında geçiş yaparlar.
    * Dijital Feromonlar:
        * Yemle dönen ajanlar, yuvaya giden yolu işaretleyen 'yuva' feromonları bırakır.
        * Diğer ajanlar bu feromonları algılayıp takip ederek yuvayı veya dolaylı olarak yem kaynaklarını bulabilirler.
        * Feromonlar ortamda zamanla yayılır (difüzyon) ve buharlaşır (evaporation), böylece eski izler kaybolur ve sürü yeni durumlara adapte olabilir (`environment.py`, NumPy).
    * Ayarlanabilir feromon parametreleri, yuva/yem özellikleri (`settings.py`).
    * Görselleştirmede yuva, yemler ve renk yoğunluğuyla feromon izleri gösterilir.
* **Amaç:** Sürünün dolaylı iletişimle nasıl kolektif bir problemi (yem toplama) çözebildiğini ve verimli yolların nasıl kendiliğinden oluştuğunu simüle etmek.

### Sürüm 3: NEAT Evrimi (Klasör: `swarm_mind_v3`)

* **Konsept:** Ajanların davranış kurallarını önceden kodlamak yerine, yapay sinir ağlarını kullanarak öğrenmelerini ve evrimleşmelerini sağlamak.
* **Özellikler:**
    * **NEAT Algoritması:** `neat-python` kütüphanesi ile ajanların "beyinlerini" (sinir ağlarını) evrimleştirir. Hem ağ bağlantıları hem de ağırlıkları nesiller boyunca optimize edilir.
    * **Sinir Ağı Kontrolü:** Her ajan, çevreden aldığı girdilere (feromon yoğunlukları, hedefe yön, hız, durum vb.) göre hareket kararlarını (yönlendirme kuvveti, feromon bırakma) veren kendi sinir ağı tarafından yönetilir.
    * **Evrim Süreci:** Popülasyondaki her ağ (genom) bir simülasyonda test edilir. Başarısı (fitness - örn. toplanan yem) ölçülür. En başarılılar seçilir, çaprazlanır ve mutasyona uğratılarak yeni nesil ağlar oluşturulur.
    * **Dinamik Ortam:** Yem kaynakları rastgele belirip tükendiği ve engeller olduğu için, ağların sürekli adapte olabilen stratejiler geliştirmesi gerekir.
    * NEAT parametreleri (`neat_config.txt`) ve simülasyon ayarları (`settings.py`) değiştirilerek evrim süreci etkilenebilir.
    * Evrim sürecini çalıştıran ve isteğe bağlı olarak en iyi genomun davranışını görselleştiren ana betik (`main.py`).
* **Amaç:** Karmaşık ve adaptif sürü davranışlarının, stratejileri açıkça kodlamadan, sadece performans başarısına dayalı bir evrim süreciyle nasıl ortaya çıkabileceğini göstermek.

### Sürüm 4: Ko-Evrimsel Rekabet (Klasör: `swarm_mind_v4`)

* **Konsept:** Evrimsel süreci bir adım ileri taşıyarak, aynı ortamdaki kaynaklar için rekabet eden iki farklı sürünün (koloninin) birbirlerine karşı stratejiler geliştirerek birlikte evrimleşmesini (ko-evrim) incelemek.
* **Özellikler:**
    * **İki Rakip Koloni:** Kırmızı ve Mavi koloniler, kendi yuvaları ve kendi renkleriyle simüle edilir.
    * **Ayrı NEAT Popülasyonları:** Her koloni, kendi NEAT popülasyonu tarafından evrimleştirilen sinir ağları tarafından kontrol edilir.
    * **Rekabet:** Koloniler, ortamdaki aynı dinamik yem kaynakları için yarışır.
    * **Ayrı Feromon İzleri:** Her koloni kendi 'yuva' ve 'yem' feromon izlerini bırakır ve algılar (`environment.py`).
    * **Ko-Evrimsel Fitness:** Bir genomun başarısı, sadece kendi topladığı yeme değil, aynı zamanda eşleştiği rakip genomun performansına göre de hesaplanır (rekabetçi fitness).
    * **Özel Evrim Döngüsü:** `main_coev.py`, iki popülasyonu yönetir, genomları eşleştirip simülasyonları çalıştırır, rekabetçi fitness'ı hesaplar ve her iki popülasyon için üreme adımlarını manuel olarak tetikler.
* **Amaç:** İki adaptif sürünün rekabetinden doğan ko-evrimsel "silahlanma yarışını", ortaya çıkan karmaşık saldırı/savunma/işbirliği stratejilerini modellemek ve gözlemlemek.

---

## Gösterilen Temel Kavramlar (Türkçe)

* **Sürü Zekası:** Merkezi bir kontrol olmadan, bireylerin yerel etkileşimleriyle ortaya çıkan kolektif "akıllı" davranışlar.
* **Belirme (Emergence):** Basit kurallara uyan çok sayıda bileşenin etkileşiminden, öngörülemeyen karmaşık ve yeni özelliklerin/düzenlerin doğması.
* **Ajan Tabanlı Modelleme (ABM):** Bir sistemi, otonom ajanların (bireylerin) davranışlarını ve etkileşimlerini modelleyerek anlama ve simüle etme yaklaşımı.
* **Stigmergy:** Ajanların çevrelerinde bıraktıkları izler veya yaptıkları değişiklikler yoluyla dolaylı olarak iletişim kurması (örn. karınca feromonları).
* **Nöroevrim (NEAT):** Yapay sinir ağlarının yapısını ve ağırlıklarını evrimsel algoritmalar kullanarak optimize etme tekniği.
* **Adaptasyon:** Sistemlerin veya ajanların, değişen çevre koşullarına veya deneyimlerine göre davranışlarını ayarlama yeteneği.
* **Ko-evrim:** İki veya daha fazla popülasyonun, birbirlerinin evrimsel baskıları altında karşılıklı olarak evrimleşmesi süreci.

## Core Concepts Demonstrated (English)

* **Swarm Intelligence:** Collective "intelligent" behavior emerging from local interactions of individuals without central control.
* **Emergence:** The arising of novel and complex properties/patterns from the interactions of multiple simple components following simple rules.
* **Agent-Based Modeling (ABM):** An approach to understanding and simulating systems by modeling the behaviors and interactions of autonomous agents (individuals).
* **Stigmergy:** Indirect communication between agents mediated by modifications made to their environment (e.g., ant pheromone trails).
* **Neuroevolution (NEAT):** A technique for optimizing the structure and weights of artificial neural networks using evolutionary algorithms.
* **Adaptation:** The ability of systems or agents to adjust their behavior in response to changing environmental conditions or experiences.
* **Co-evolution:** The process where two or more populations evolve in tandem, under the influence of the evolutionary pressures they exert on each other.

---

## Teknoloji Yığını (Türkçe & English)

* **Dil / Language:** Python 3
* **Görselleştirme / Visualization:** Pygame
* **Sayısal İşlemler / Numerical Operations:** NumPy
* **Nöroevrim / Neuroevolution:** neat-python

---

## Nasıl Çalıştırılır (Türkçe)

1.  **Depoyu Klonlayın:** Proje dosyalarını bilgisayarınıza indirin.
2.  **Bağımlılıkları Yükleyin:** Komut istemcisini (terminal) açın ve şunu çalıştırın:
    ```bash
    pip install pygame numpy neat-python
    ```
3.  **Sürüm Klasörüne Gidin:** Çalıştırmak istediğiniz sürümün klasörüne `cd` komutu ile girin (örn: `cd swarm_mind_v4`).
4.  **Ana Betiği Çalıştırın:**
    * V1, V2 için: `python main.py` (Simülasyon doğrudan başlar)
    * V3 (Evrim) için: `python main.py` (Bu komut NEAT evrim/eğitim sürecini başlatır)
    * V4 (Ko-evrim) için: `python main_coev.py` (Bu komut iki popülasyonun ko-evrim/eğitim sürecini başlatır)
5.  **V3/V4 İçin Not:** Bu sürümlerin ana betikleri varsayılan olarak evrim/eğitim sürecini çalıştırır. Bu süreç uzun sürebilir. Süreç tamamlandıktan sonra (veya `settings.py` içindeki `VISUALIZE_BEST_GENOME`/`VISUALIZE_BEST_GENOMES` `True` ise), en iyi genom(lar)ın davranışını gösteren bir görselleştirme penceresi açılabilir. Kaydedilmiş belirli bir genomu (`.pkl` dosyası) görselleştirmek için betiklerde küçük değişiklikler yapmanız gerekebilir. V4 için `checkpoints_red` ve `checkpoints_blue` klasörlerinin mevcut olduğundan emin olun.

## How to Run (English)

1.  **Clone the Repository:** Download the project files to your computer.
2.  **Install Dependencies:** Open your terminal or command prompt and run:
    ```bash
    pip install pygame numpy neat-python
    ```
3.  **Navigate to the Version Folder:** Change directory (`cd`) into the folder of the version you want to run (e.g., `cd swarm_mind_v4`).
4.  **Run the Main Script:**
    * For V1, V2: `python main.py` (Simulation starts directly)
    * For V3 (Evolution): `python main.py` (This starts the NEAT evolution/training process)
    * For V4 (Co-evolution): `python main_coev.py` (This starts the co-evolution/training process for two populations)
5.  **Note for V3/V4:** The main scripts for these versions run the evolution/training process by default, which can take a long time. After the process completes (or if `VISUALIZE_BEST_GENOME`/`VISUALIZE_BEST_GENOMES` is `True` in `settings.py`), a visualization window showing the behavior of the best genome(s) may open. To visualize a specific saved genome (`.pkl` file), you might need to make minor modifications to the scripts. For V4, ensure the `checkpoints_red` and `checkpoints_blue` folders exist.

---

## Özelleştirme ve Parametreler (Türkçe)

Simülasyonun davranışını ve evrimsel sonuçlarını büyük ölçüde değiştirmek için aşağıdaki dosyalardaki parametrelerle oynayabilirsiniz:

* **`settings.py` (Her sürüm klasöründe):**
    * Ekran boyutları, FPS (kare hızı).
    * Ajan sayısı, maksimum hız, boyut, algılama yarıçapları.
    * Boids kural ağırlıkları (V1).
    * Feromon bırakma miktarı, buharlaşma ve yayılma oranları (V2, V3, V4).
    * Yuva/Yem özellikleri, yem çıkma sıklığı/miktarı (V2, V3, V4).
    * NEAT/Ko-evrim simülasyon adım sayısı, fitness hesaplama yöntemi, rakip sayısı (V3, V4).
    * Görselleştirme ve hata ayıklama seçenekleri (DEBUG flag'leri).
* **`neat_config_v*.txt` (V3 ve V4 klasörlerinde):**
    * NEAT algoritmasının detaylı parametreleri.
    * Popülasyon büyüklüğü (`pop_size`).
    * Sinir ağı girdi ve çıktı sayısı (`num_inputs`, `num_outputs`) - **Bu sayıların `agent_*.py` dosyalarındaki uygulamayla tam olarak eşleşmesi kritik öneme sahiptir!**
    * Aktivasyon fonksiyonları, mutasyon oranları (yeni bağlantı/düğüm ekleme, ağırlık değiştirme vb.).
    * Türleşme (speciation) ve durgunluk (stagnation) parametreleri.

## Customization & Parameters (English)

You can significantly alter the simulation's behavior and evolutionary outcomes by experimenting with parameters in the following files:

* **`settings.py` (In each version folder):**
    * Screen dimensions, FPS (frames per second).
    * Agent counts, maximum speeds, sizes, perception radii.
    * Boids rule weights (V1).
    * Pheromone deposit amount, evaporation and diffusion rates (V2, V3, V4).
    * Nest/Food properties, food spawn rate/amount (V2, V3, V4).
    * NEAT/Co-evolution simulation steps, fitness calculation method, number of opponents (V3, V4).
    * Visualization and debugging options (DEBUG flags).
* **`neat_config_v*.txt` (In V3 and V4 folders):**
    * Detailed parameters for the NEAT algorithm.
    * Population size (`pop_size`).
    * Number of neural network inputs and outputs (`num_inputs`, `num_outputs`) - **It is crucial that these numbers exactly match the implementation in the `agent_*.py` files!**
    * Activation functions, mutation rates (adding connections/nodes, changing weights, etc.).
    * Speciation and stagnation parameters.

---

## Bilimsel ve Eğitsel Değer (Türkçe)

SwarmMind, aşağıdaki konularda pratik bir öğrenme ve keşif platformu sunar:

* **Belirmenin Anlaşılması:** Karmaşık kolektif davranışların, basit bireysel eylemlerden nasıl doğduğunu görsel olarak deneyimleme.
* **Sürü Zekasının Keşfi:** Doğadaki karınca kolonileri veya kuş sürüleri gibi sistemlerdeki yem bulma ve iletişim stratejilerini simüle etme.
* **Yapay Zeka Kavramlarını Öğrenme:** Nöroevrim (NEAT) gibi makine öğrenmesi tekniklerini uygulama ve sonuçlarını gözlemleme. Adaptif sistemlerin nasıl çalıştığını anlama.
* **Ko-evrimin İncelenmesi:** Evrimleşen popülasyonlar arasındaki rekabetçi dinamikleri ve strateji gelişimini inceleme.
* **Ajan Tabanlı Modelleme Pratiği:** Karmaşık sistemleri modellemek için ajan tabanlı yaklaşımın nasıl kullanılacağına dair somut bir örnek sunma.

Özellikle V3 ve V4 sürümleri, daha derinlemesine analiz ve uzun süreli evrim çalışmalarıyla, Yapay Yaşam, Karmaşık Sistemler veya Yapay Zeka Simülasyonu gibi alanlarda bilimsel yayın potansiyeli taşıyabilecek hesaplamalı deneyler için bir başlangıç noktası sunmaktadır.

## Scientific & Educational Value (English)

SwarmMind serves as a practical learning and exploration platform for:

* **Understanding Emergence:** Visually experiencing how complex collective behaviors arise from simple individual actions.
* **Exploring Swarm Intelligence:** Simulating foraging and communication strategies seen in natural systems like ant colonies or bird flocks.
* **Learning AI Concepts:** Implementing and observing machine learning techniques like neuroevolution (NEAT) and understanding how adaptive systems work.
* **Investigating Co-evolution:** Studying competitive dynamics and strategy development between evolving populations.
* **Agent-Based Modeling Practice:** Providing a concrete example of how to use the agent-based approach to model complex systems.

Versions V3 and V4, in particular, offer a starting point for computational experiments that, with further analysis and longer evolution runs, could potentially yield insights publishable in fields like Artificial Life, Complex Systems, or AI Simulation.

---

## Sınırlılıklar (Türkçe)

* **Hesaplama Maliyeti:** NEAT evrimi (V3) ve özellikle ko-evrim (V4) süreçleri oldukça fazla bilgisayar gücü gerektirir. Optimal stratejilerin evrimleşmesi önemli ölçüde zaman (saatler veya günler) ya da çok çekirdekli işlemcilerde paralel hesaplama gerektirebilir. Sağlanan varsayılan ayarlar, kavramları hızlı bir şekilde gösterebilmek için ayarlanmıştır ve mutlak en iyi stratejileri bulmayı garanti etmez.
* **Basitleştirme:** Fizik, algılama, feromonlar, sinir ağları ve evrim modelleri, gerçekliğin kaçınılmaz olarak basitleştirilmiş soyutlamalarıdır.
* **Görselleştirme:** Pygame ile yapılan görselleştirme işlevseldir ancak temel düzeydedir. Çok sayıda ajan veya yoğun feromon alanları görselleştirme sırasında performansı düşürebilir. Evrim sürecindeki fitness değerlendirmeleri hız için grafiksiz modda yapılır.
* **Parametre Ayarlama:** Hem simülasyon (`settings.py`) hem de NEAT algoritması (`config` dosyası) için en uygun parametreleri bulmak genellikle deneme-yanılma ve tecrübe gerektirir.

## Limitations (English)

* **Computational Cost:** The NEAT evolution (V3) and especially the co-evolution (V4) processes are computationally intensive. Evolving optimal strategies requires significant runtime (hours or days) or parallel processing on multi-core CPUs. The provided default settings are tuned for faster execution to demonstrate the concepts and do not guarantee finding the absolute best strategies.
* **Simplification:** The models for physics, sensing, pheromones, neural networks, and evolution are necessarily simplified abstractions of reality.
* **Visualization:** The visualization using Pygame is functional but basic. A large number of agents or dense pheromone fields can impact performance during visualization. Fitness evaluations during the evolution process are run headlessly (without graphics) for speed.
* **Parameter Tuning:** Finding the optimal parameters for both the simulation (`settings.py`) and the NEAT algorithm (`config` file) often requires experimentation and experience.

---

## Potansiyel Gelecek Çalışmalar (Türkçe & English - Optional)

* NEAT/Ko-evrim için paralel değerlendirme (`neat.ParallelEvaluator`) uygulamak / Implement parallel evaluation (`neat.ParallelEvaluator`) for NEAT/Co-evolution.
* Daha sofistike çevresel özellikler eklemek (farklı zemin türleri, hareketli engeller, kaynakların bölgesel dağılımı) / Add more sophisticated environmental features (varied terrain types, moving obstacles, resource patches).
* Daha karmaşık ajan etkileşimleri uygulamak (doğrudan iletişim, koloni içi işbirliği/görev dağılımı) / Implement more complex agent interactions (direct communication, intra-colony cooperation/task allocation).
* V4 ajan girdilerine açık düşman algılama/kaçınma mantığı eklemek / Add explicit enemy sensing/avoidance logic to V4 agent inputs.
* Evrimleşmiş sinir ağları ve stratejiler için daha gelişmiş analiz ve görselleştirme araçları entegre etmek / Integrate more advanced analysis and visualization tools for evolved networks and strategies.
* Farklı evrimsel algoritmalar veya bilişsel mimarilerle denemeler yapmak / Experiment with different evolutionary algorithms or cognitive architectures.
