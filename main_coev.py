# swarm_mind_v4/main_coev.py
import pygame
import sys
import os
import neat # NEAT kütüphanesi
import numpy as np
import pickle # Genomları kaydetmek/yüklemek için
import random
import time # Zaman ölçümü için
import settings as s
from environment import Environment # V4 Environment
from agent_coev import AgentCoEv # V4 Agent

# --- Tek Bir Eşleşmeyi Simüle Etme Fonksiyonu ---
def eval_simulation(genome_red, config_red, genome_blue, config_blue):
    """
    Bir kırmızı ve bir mavi genom arasındaki tek bir maçı simüle eder.
    Her iki koloninin topladığı yem miktarını döndürür.
    """
    # Ağları oluştur
    net_red = neat.nn.FeedForwardNetwork.create(genome_red, config_red)
    net_blue = neat.nn.FeedForwardNetwork.create(genome_blue, config_blue)

    # Ortamı oluştur
    environment = Environment(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)

    # Ajanları oluştur (her koloni kendi ağını kullanır)
    agents_red = [AgentCoEv(genome_red, config_red, environment, s.COLONY_ID_RED) for _ in range(s.NUM_AGENTS_PER_COLONY)]
    agents_blue = [AgentCoEv(genome_blue, config_blue, environment, s.COLONY_ID_BLUE) for _ in range(s.NUM_AGENTS_PER_COLONY)]
    all_agents = agents_red + agents_blue

    # --- Simülasyon Döngüsü (Görselleştirmesiz) ---
    for step in range(s.SIMULATION_STEPS_PER_GEN):
        environment.update()
        # Ajanları rastgele sırada güncellemek yanlılığı azaltabilir
        random.shuffle(all_agents)
        for agent in all_agents:
            # update metodu artık tüm ajan listesini alıyor
            agent.update(all_agents)

    # --- Sonuçları Hesapla ---
    food_red = sum(agent.food_collected_count for agent in agents_red)
    food_blue = sum(agent.food_collected_count for agent in agents_blue)

    return food_red, food_blue

# --- Ko-evrim Sürecini Başlatma Fonksiyonu ---
def run_coev(config_file):
    """
    İki popülasyon için NEAT ko-evrim sürecini yönetir.
    """
    # NEAT yapılandırmasını yükle
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # --- Popülasyonları Oluştur veya Yükle ---
    checkpoint_dir_red = 'swarm_mind_v4/checkpoints_red'
    checkpoint_dir_blue = 'swarm_mind_v4/checkpoints_blue'
    os.makedirs(checkpoint_dir_red, exist_ok=True)
    os.makedirs(checkpoint_dir_blue, exist_ok=True)

    try:
        p_red = neat.Checkpointer.restore_checkpoint(os.path.join(checkpoint_dir_red, 'neat-checkpoint-'))
        print("Kırmızı popülasyon checkpoint'ten yüklendi.")
    except Exception:
        print("Kırmızı popülasyon checkpoint bulunamadı, yeni oluşturuluyor.")
        p_red = neat.Population(config)

    try:
        p_blue = neat.Checkpointer.restore_checkpoint(os.path.join(checkpoint_dir_blue, 'neat-checkpoint-'))
        print("Mavi popülasyon checkpoint'ten yüklendi.")
    except Exception:
        print("Mavi popülasyon checkpoint bulunamadı, yeni oluşturuluyor.")
        p_blue = neat.Population(config)

    # --- Raporlayıcıları Ekle ---
    # Kırmızı Popülasyon
    p_red.add_reporter(neat.StdOutReporter(True))
    stats_red = neat.StatisticsReporter()
    p_red.add_reporter(stats_red)
    p_red.add_reporter(neat.Checkpointer(generation_interval=5, filename_prefix=os.path.join(checkpoint_dir_red, 'neat-checkpoint-')))
    # Mavi Popülasyon
    # İkinci StdOutReporter'ı eklemeyebiliriz, çıktılar karışmasın diye
    # p_blue.add_reporter(neat.StdOutReporter(True)) # Veya sadece mavi için ayrı bir prefix ile
    stats_blue = neat.StatisticsReporter()
    p_blue.add_reporter(stats_blue)
    p_blue.add_reporter(neat.Checkpointer(generation_interval=5, filename_prefix=os.path.join(checkpoint_dir_blue, 'neat-checkpoint-')))

    # --- Özel Nesil Döngüsü ---
    for generation in range(s.NUM_GENERATIONS):
        start_time = time.time()
        print(f"\n****** Ko-Evrim Nesil {generation} Başladı ******")

        # Mevcut neslin genomlarını al (sözlük olarak: {genome_id: genome})
        genomes_red_dict = p_red.population
        genomes_blue_dict = p_blue.population
        # Liste olarak da alabiliriz (eşleşme için daha kolay olabilir)
        genomes_red_list = list(genomes_red_dict.items())
        genomes_blue_list = list(genomes_blue_dict.items())

        # Her genomun bu nesildeki maç skorlarını saklamak için
        # Anahtar: genome_id, Değer: [(kendi_skoru, rakip_skoru), ...] listesi
        genome_scores_red = {gid: [] for gid, _ in genomes_red_list}
        genome_scores_blue = {gid: [] for gid, _ in genomes_blue_list}

        # --- Eşleştirme ve Değerlendirme ---
        eval_count = 0
        # Her kırmızı genomu, rastgele K mavi genoma karşı test et
        for gid_r, genome_r in genomes_red_list:
            # Rastgele K rakip seç (eğer mavi popülasyon K'dan küçükse hepsiyle eşleşir)
            num_opponents = min(s.NUM_OPPONENTS_PER_EVAL, len(genomes_blue_list))
            opponents = random.sample(genomes_blue_list, num_opponents)

            for gid_b, genome_b in opponents:
                # Simülasyonu çalıştır
                food_r, food_b = eval_simulation(genome_r, config, genome_b, config)
                eval_count += 1

                # Sonuçları her iki genom için de kaydet
                genome_scores_red[gid_r].append((food_r, food_b))
                genome_scores_blue[gid_b].append((food_b, food_r)) # Rakibin skorunu kendi skoru olarak kaydet

        print(f"Nesil {generation}: {eval_count} eşleşme değerlendirildi.")

        # --- Fitness Hesaplama ve Atama ---
        # Kırmızı genomlar için
        for gid, genome in genomes_red_dict.items():
            scores = genome_scores_red[gid]
            if not scores: # Eğer hiç maç yapmadıysa (popülasyon çok küçükse olabilir)
                genome.fitness = 0.0
                continue
            avg_my_food = np.mean([s[0] for s in scores])
            avg_opp_food = np.mean([s[1] for s in scores])

            if s.FITNESS_METHOD == 'competitive':
                genome.fitness = avg_my_food - avg_opp_food
            else: # 'absolute'
                genome.fitness = avg_my_food

        # Mavi genomlar için
        for gid, genome in genomes_blue_dict.items():
            scores = genome_scores_blue[gid]
            if not scores:
                genome.fitness = 0.0
                continue
            avg_my_food = np.mean([s[0] for s in scores])
            avg_opp_food = np.mean([s[1] for s in scores])

            if s.FITNESS_METHOD == 'competitive':
                genome.fitness = avg_my_food - avg_opp_food
            else: # 'absolute'
                genome.fitness = avg_my_food

        # --- NEAT Üreme ve Raporlama Adımları (Manuel) ---
        # Raporlayıcıları bilgilendir ve sonraki nesli oluştur
        best_genome_red = max(genomes_red_dict.values(), key=lambda g: g.fitness)
        best_genome_blue = max(genomes_blue_dict.values(), key=lambda g: g.fitness)

        p_red.reporters.post_evaluate(config, genomes_red_dict, p_red.species, best_genome_red)
        p_blue.reporters.post_evaluate(config, genomes_blue_dict, p_blue.species, best_genome_blue)

        p_red.reporters.end_generation(config, genomes_red_dict, p_red.species)
        p_blue.reporters.end_generation(config, genomes_blue_dict, p_blue.species)

        # Sonraki nesilleri oluştur
        p_red.population = p_red.reproduction.reproduce(config, p_red.species, config.pop_size, generation)
        p_blue.population = p_blue.reproduction.reproduce(config, p_blue.species, config.pop_size, generation)

        # Yeni nesil için türleri ayarla (checkpoint'ten sonra gerekli olabilir)
        if not p_red.species or not p_blue.species:
             p_red.species = config.species_set_type(config, p_red.reporters)
             p_blue.species = config.species_set_type(config, p_blue.reporters)
        p_red.species.speciate(config, p_red.population, generation)
        p_blue.species.speciate(config, p_blue.population, generation)

        # Raporlayıcıları yeni nesil için başlat
        p_red.reporters.start_generation(generation + 1)
        p_blue.reporters.start_generation(generation + 1)

        end_time = time.time()
        print(f"Nesil {generation} tamamlandı. Süre: {end_time - start_time:.2f} saniye")


    # --- Evrim Sonrası ---
    print('\nKo-Evrim tamamlandı.')

    # En iyi genomları bul (popülasyonlar artık bir sonraki nesli içeriyor olabilir,
    # istatistiklerden veya kaydedilenlerden almak daha güvenli olabilir)
    # Şimdilik popülasyon içindeki en iyiyi varsayalım (dikkatli olunmalı)
    try:
         winner_red = max(p_red.population.values(), key=lambda g: g.fitness if g.fitness is not None else -float('inf'))
         winner_blue = max(p_blue.population.values(), key=lambda g: g.fitness if g.fitness is not None else -float('inf'))

         print('\nEn İyi Kırmızı Genom:')
         print(winner_red)
         print('\nEn İyi Mavi Genom:')
         print(winner_blue)

         # En iyi genomları kaydet
         os.makedirs('swarm_mind_v4/best_genomes', exist_ok=True)
         with open('swarm_mind_v4/best_genomes/winner_red.pkl', 'wb') as f:
             pickle.dump(winner_red, f)
         with open('swarm_mind_v4/best_genomes/winner_blue.pkl', 'wb') as f:
             pickle.dump(winner_blue, f)
         print("En iyi genomlar 'best_genomes' klasörüne kaydedildi.")

         # İsteğe bağlı görselleştirme
         if s.VISUALIZE_BEST_GENOMES:
             visualize_simulation(winner_red, config, winner_blue, config)

    except Exception as e:
         print(f"\nEvrim sonrası hata (En iyi genom bulunamadı veya kaydedilemedi): {e}")


# --- Görselleştirme Fonksiyonu (V4 için güncellendi) ---
def visualize_simulation(genome_red, config_red, genome_blue, config_blue):
    """
    İki rakip genomun davranışını Pygame ile görselleştirir.
    """
    print("\nEn iyi Kırmızı ve Mavi genomların maçı görselleştiriliyor...")
    pygame.init()
    screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
    pygame.display.set_caption(f"{s.WINDOW_TITLE} - Best Genomes Match")
    clock = pygame.time.Clock()

    environment = Environment(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
    net_red = neat.nn.FeedForwardNetwork.create(genome_red, config_red)
    net_blue = neat.nn.FeedForwardNetwork.create(genome_blue, config_blue)
    agents_red = [AgentCoEv(genome_red, config_red, environment, s.COLONY_ID_RED) for _ in range(s.NUM_AGENTS_PER_COLONY)]
    agents_blue = [AgentCoEv(genome_blue, config_blue, environment, s.COLONY_ID_BLUE) for _ in range(s.NUM_AGENTS_PER_COLONY)]
    all_agents = agents_red + agents_blue

    running = True
    sim_step = 0
    max_vis_steps = s.SIMULATION_STEPS_PER_GEN * 2 # Görselleştirmeyi biraz daha uzun tutalım
    while running and sim_step < max_vis_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; break
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_p: s.DEBUG_DRAW_PHEROMONES = not s.DEBUG_DRAW_PHEROMONES
                 if event.key == pygame.K_ESCAPE: running = False; break
        if not running: break

        environment.update()
        random.shuffle(all_agents)
        for agent in all_agents:
            agent.update(all_agents)

        screen.fill(s.COLOR_BACKGROUND)
        environment.draw(screen)
        for agent in all_agents:
            agent.draw(screen)

        # Bilgi metinleri
        font = pygame.font.SysFont(None, 24)
        food_r = sum(a.food_collected_count for a in agents_red)
        food_b = sum(a.food_collected_count for a in agents_blue)
        info_text = font.render(f"Adım: {sim_step}/{max_vis_steps} | Kırmızı Yem: {food_r} | Mavi Yem: {food_b}", True, (255, 255, 255))
        screen.blit(info_text, (10, 10))

        pygame.display.flip()
        clock.tick(s.VISUALIZATION_FPS)
        sim_step += 1

    pygame.quit()
    print("Görselleştirme tamamlandı.")


# --- Ana Çalıştırma Bloğu ---
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config_v4.txt')

    if not os.path.exists(config_path):
        print(f"HATA: NEAT config dosyası bulunamadı: {config_path}")
        sys.exit(1)

    print("SwarmMind V4.0 - Co-evolutionary Competition başlatılıyor...")
    print(f"NEAT Yapılandırması: {config_path}")
    print(f"Jenerasyon Sayısı: {s.NUM_GENERATIONS}")
    print(f"Popülasyon Büyüklüğü/Koloni: (config dosyasında belirtilir)")
    print(f"Simülasyon Adım Sayısı/Eşleşme: {s.SIMULATION_STEPS_PER_GEN}")
    print(f"Ajan Sayısı/Koloni: {s.NUM_AGENTS_PER_COLONY}")
    print(f"Rakip Sayısı/Değerlendirme: {s.NUM_OPPONENTS_PER_EVAL}")
    print(f"Fitness Yöntemi: {s.FITNESS_METHOD}")

    # Gerekli klasörleri oluştur
    os.makedirs('swarm_mind_v4/checkpoints_red', exist_ok=True)
    os.makedirs('swarm_mind_v4/checkpoints_blue', exist_ok=True)
    os.makedirs('swarm_mind_v4/best_genomes', exist_ok=True)

    run_coev(config_path)