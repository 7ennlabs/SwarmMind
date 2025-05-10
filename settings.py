# swarm_mind_v4/settings.py
import pygame
import numpy as np
import random

# --- Temel Ekran ve Simülasyon Ayarları ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60 # Görselleştirme FPS'i
WINDOW_TITLE = "SwarmMind V4.0 - Co-evolutionary Competition"
SIMULATION_STEPS_PER_GEN = 800 # Her eşli değerlendirme için adım sayısı (Hız için düşük)
NUM_GENERATIONS = 100 # Toplam evrimleştirilecek nesil sayısı

# --- Koloni Ayarları ---
COLONY_ID_RED = 0
COLONY_ID_BLUE = 1
NUM_AGENTS_PER_COLONY = 15 # Koloni başına ajan sayısı (Hız için düşük)
TOTAL_AGENTS = NUM_AGENTS_PER_COLONY * 2

# --- Renkler ---
COLOR_BACKGROUND = (10, 10, 30)
# Kırmızı Koloni
COLOR_AGENT_RED_SEEKING = (255, 100, 100)
COLOR_AGENT_RED_RETURNING = (255, 180, 180)
COLOR_PHEROMONE_HOME_RED = (200, 0, 0, 150) # Kırmızı yuva izi
# Mavi Koloni
COLOR_AGENT_BLUE_SEEKING = (100, 100, 255)
COLOR_AGENT_BLUE_RETURNING = (180, 180, 255)
COLOR_PHEROMONE_HOME_BLUE = (0, 0, 200, 150) # Mavi yuva izi
# Ortak Renkler
COLOR_NEST_RED = (255, 50, 0)   # Kırmızı yuva
COLOR_NEST_BLUE = (0, 50, 255)  # Mavi yuva
COLOR_FOOD = (50, 255, 50)      # Yem rengi (Yeşil)
COLOR_OBSTACLE = (100, 100, 100)

# --- Ajan Ayarları (Temel Fizik) ---
AGENT_SIZE = 7
MAX_SPEED = 3.5
MAX_FORCE = 0.2

# --- Ortam Ayarları (V4 - İki Yuva, Dinamik Yem) ---
# Yuvaları ekranın iki yanına yerleştirelim
NEST_POS_RED = np.array([100, SCREEN_HEIGHT / 2], dtype=np.float32)
NEST_POS_BLUE = np.array([SCREEN_WIDTH - 100, SCREEN_HEIGHT / 2], dtype=np.float32)
NEST_RADIUS = 30

# Yem Kaynakları (Dinamik)
MAX_FOOD_SOURCES = 10
FOOD_RADIUS = 10
FOOD_INITIAL_AMOUNT = 40
FOOD_SPAWN_RATE = 0.015
# Yem bitince kaynak ortamdan silinsin mi?
FOOD_DEPLETION_REMOVAL = True  # <--- EKLENEN SATIR

# Engeller
NUM_OBSTACLES = 6
OBSTACLE_MIN_RADIUS = 15
OBSTACLE_MAX_RADIUS = 45

# Feromon Ayarları
PHEROMONE_RESOLUTION = 15
GRID_WIDTH = SCREEN_WIDTH // PHEROMONE_RESOLUTION
GRID_HEIGHT = SCREEN_HEIGHT // PHEROMONE_RESOLUTION
PHEROMONE_MAX_STRENGTH = 1.0
PHEROMONE_DEPOSIT_VALUE = 0.9
PHEROMONE_EVAPORATION_RATE = 0.010
PHEROMONE_DIFFUSION_RATE = 0.05

# --- NN Girdi/Çıktı Ayarları (V3 ile aynı, şimdilik) ---
# Dikkat: Bu değerler neat_config_v4.txt içindeki num_inputs ile eşleşmeli!
# Şu anki girdiler: Home Pher (3), Food Pher (3), Bias (1), Carrying (1), Vel (2), Nest Dir (2), Food Dir (2), Food Dist (1), Agent Density (1) = 16
num_inputs = 16 # Config dosyasıyla tutarlılık için buraya da ekleyelim (assert'te kullanılabilir)
NN_PHEROMONE_SENSE_DIST = AGENT_SIZE * 4
NN_PHEROMONE_SENSE_ANGLES = [-np.pi / 3, 0, np.pi / 3] # Sol, Orta, Sağ
NN_FOOD_SENSE_RADIUS = 150
NN_AGENT_SENSE_RADIUS = 60
NN_OUTPUT_DEPOSIT_THRESHOLD = 0.6

# --- Ko-evrim Ayarları ---
# Fitness Hesaplama Yöntemi: 'absolute' (sadece kendi yemi), 'competitive' (kendi - rakip)
FITNESS_METHOD = 'competitive'
# Her genomu kaç rakip genoma karşı test edelim?
NUM_OPPONENTS_PER_EVAL = 5

# --- Görselleştirme ve Debug ---
VISUALIZE_BEST_GENOMES = True
VISUALIZATION_FPS = 30
DEBUG_DRAW_PHEROMONES = False
DEBUG_DRAW_FOOD_LOCATIONS = True
DEBUG_DRAW_NESTS = True
DEBUG_DRAW_OBSTACLES = True