# swarm_mind_v4/agent_coev.py
import pygame
import numpy as np
import random
import math
import neat # NEAT kütüphanesi
from vector import Vector2D
# V4 Environment'ı import ediyoruz
from environment import Environment, FoodSource
import settings as s

class AgentCoEv:
    """
    Ko-evrim simülasyonundaki bir ajan. NEAT tarafından evrimleştirilen bir
    sinir ağı tarafından kontrol edilir ve kendi kolonisine aittir.
    """
    def __init__(self, genome, config, environment: Environment, colony_id: int):
        """Ajanı genom, config, ortam ve koloni ID ile başlatır."""
        self.genome = genome
        self.config = config
        self.environment = environment
        self.colony_id = colony_id # Kendi kolonisi (0: Kırmızı, 1: Mavi)

        # Genomdan sinir ağını oluştur
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Fiziksel özellikler
        self.max_speed = s.MAX_SPEED
        self.max_force = s.MAX_FORCE
        self.size = s.AGENT_SIZE

        # Sensör parametreleri
        self.pheromone_sense_dist = s.NN_PHEROMONE_SENSE_DIST
        self.pheromone_sense_angles = s.NN_PHEROMONE_SENSE_ANGLES
        self.food_sense_radius = s.NN_FOOD_SENSE_RADIUS
        self.agent_sense_radius = s.NN_AGENT_SENSE_RADIUS

        # Başlangıç durumunu ayarlamak için reset() çağır
        self.reset()


    def reset(self):
        """Ajanın durumunu başlangıç koşullarına sıfırlar."""
        # Başlangıç pozisyonu (kendi yuvasının yakınında)
        my_nest_pos = self.environment.get_nest_position(self.colony_id)
        angle = random.uniform(0, 2 * math.pi)
        start_offset_np = np.array([math.cos(angle), math.sin(angle)]) * s.NEST_RADIUS * 1.2
        start_pos_np = my_nest_pos + start_offset_np
        self.position = Vector2D(np.clip(start_pos_np[0], 0, s.SCREEN_WIDTH),
                                 np.clip(start_pos_np[1], 0, s.SCREEN_HEIGHT))

        self.velocity = Vector2D.random_vector() * (self.max_speed / 2)
        self.acceleration = Vector2D(0, 0)

        # Durum
        self.has_food = False
        # Renk kolonisine göre ayarlanır
        self.color = s.COLOR_AGENT_RED_SEEKING if self.colony_id == s.COLONY_ID_RED else s.COLOR_AGENT_BLUE_SEEKING

        # Fitness takibi için sayaç
        self.food_collected_count = 0


    def _get_inputs(self, all_agents: list) -> list[float]:
        """Sinir ağı için girdileri toplar, normalize eder."""
        inputs = []
        current_pos_np = np.array([self.position.x, self.position.y])

        # --- Feromon Girdileri (Kendi Kolonisinin, Normalleştirilmiş 0-1) ---
        current_heading = self.velocity.heading()
        sample_points_v = []
        for angle_offset in self.pheromone_sense_angles:
            angle = current_heading + angle_offset
            point = self.position + Vector2D(math.cos(angle), math.sin(angle)) * self.pheromone_sense_dist
            sample_points_v.append(point)
        sample_points_np = [np.array([p.x, p.y]) for p in sample_points_v]

        # Kendi kolonisine ait 'home' ve 'food' feromonlarını al
        home_pheromones = self.environment.sense_pheromones_at(self.colony_id, 'home', sample_points_np)
        food_pheromones = self.environment.sense_pheromones_at(self.colony_id, 'food', sample_points_np)

        inputs.extend(home_pheromones / s.PHEROMONE_MAX_STRENGTH) # 3 girdi
        inputs.extend(food_pheromones / s.PHEROMONE_MAX_STRENGTH) # 3 girdi

        # --- Bias Girdisi ---
        inputs.append(1.0) # 1 girdi

        # --- Durum Girdisi ---
        inputs.append(1.0 if self.has_food else 0.0) # 1 girdi

        # --- Hız Girdisi (Normalleştirilmiş -1 ile 1 arası) ---
        norm_vel_x = np.clip(self.velocity.x / self.max_speed, -1.0, 1.0)
        norm_vel_y = np.clip(self.velocity.y / self.max_speed, -1.0, 1.0)
        inputs.extend([norm_vel_x, norm_vel_y]) # 2 girdi

        # --- Yuva Yönü Girdisi (Kendi Yuvasına, Normalleştirilmiş X, Y) ---
        my_nest_pos = self.environment.get_nest_position(self.colony_id)
        nest_vector = my_nest_pos - current_pos_np
        dist_to_nest_sq = np.sum(nest_vector**2)
        if dist_to_nest_sq > 1e-6:
            nest_direction = nest_vector / np.sqrt(dist_to_nest_sq)
        else:
            nest_direction = np.zeros(2, dtype=np.float32)
        inputs.extend(nest_direction) # 2 girdi

        # --- Yem Girdileri (Yön X, Y normalleştirilmiş; Mesafe normalleştirilmiş) ---
        # Yem kaynakları ortak olduğu için environment'dan direkt alınır
        closest_food_pos, dist_sq_to_food, food_direction = self.environment.get_closest_food(current_pos_np)
        if closest_food_pos is not None and dist_sq_to_food < self.food_sense_radius**2 :
            inputs.extend(food_direction) # 2 girdi
            normalized_dist = np.sqrt(dist_sq_to_food) / self.food_sense_radius
            inputs.append(np.clip(normalized_dist, 0.0, 1.0)) # 1 girdi
        else:
            inputs.extend([0.0, 0.0]) # Yön yok
            inputs.append(1.0)        # Mesafe maksimum

        # --- Yakındaki Ajan Yoğunluğu Girdisi (Normalleştirilmiş 0-1) ---
        # Şimdilik dost/düşman ayrımı yapmıyoruz, toplam yoğunluk
        nearby_count = 0
        for other_agent in all_agents:
            # Ajan listesi artık karışık kolonilerden oluşacak
            if other_agent is self: continue
            # Vector2D ile mesafe kontrolü
            dist_sq = self.position.distance_squared(other_agent.position)
            if dist_sq < self.agent_sense_radius**2:
                nearby_count += 1
        # Normalleştirme (örn: 15 komşu max yoğunluk)
        density = np.clip(nearby_count / (s.TOTAL_AGENTS / 3.0), 0.0, 1.0) # Toplam ajan sayısına göre oranla
        inputs.append(density) # 1 girdi

        # Toplam girdi sayısı config ile eşleşmeli (16)
        assert len(inputs) == s.num_inputs, f"Hata: Girdi sayısı ({len(inputs)}) config ile eşleşmiyor ({s.num_inputs})"
        return inputs


    def update(self, all_agents: list):
        """Ajanın durumunu sinir ağına ve ortama göre günceller."""
        # 1. Girdileri Al
        nn_inputs = self._get_inputs(all_agents)

        # 2. Sinir Ağını Aktive Et
        nn_outputs = self.net.activate(nn_inputs)

        # 3. Çıktıları Yorumla
        steer_x = nn_outputs[0] * self.max_force
        steer_y = nn_outputs[1] * self.max_force
        steering_force = Vector2D(steer_x, steer_y)
        deposit_signal = (nn_outputs[2] + 1.0) / 2.0 # tanh için (0,1) aralığı
        should_deposit_home = deposit_signal > s.NN_OUTPUT_DEPOSIT_THRESHOLD

        # 4. Yönlendirme Kuvvetini Uygula
        self.apply_force(steering_force)

        # --- Fizik Güncellemesi ---
        self.velocity += self.acceleration
        self.velocity.limit(self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

        # --- Ortamla Etkileşim ---
        current_pos_np = np.array([self.position.x, self.position.y])

        # a. Yuvada mı kontrol et (Yem bırakma - KENDİ YUVASI)
        if self.has_food and self.environment.is_at_nest(self.colony_id, current_pos_np):
            self.has_food = False
            self.food_collected_count += 1
            # Rengi güncelle
            self.color = s.COLOR_AGENT_RED_SEEKING if self.colony_id == s.COLONY_ID_RED else s.COLOR_AGENT_BLUE_SEEKING

        # b. Yemde mi kontrol et (Yem alma)
        if not self.has_food:
            active_foods = self.environment.get_food_sources()
            for food_source in active_foods:
                dist_sq = np.sum((food_source.position - current_pos_np)**2)
                if dist_sq < (food_source.radius + self.size)**2:
                    if food_source.take():
                        self.has_food = True
                        # Rengi güncelle
                        self.color = s.COLOR_AGENT_RED_RETURNING if self.colony_id == s.COLONY_ID_RED else s.COLOR_AGENT_BLUE_RETURNING
                        break # Yem alındı

        # c. Feromon Bırakma (KENDİ KOLONİSİNİN 'home' izi)
        if should_deposit_home and self.has_food:
             if random.random() < 0.8:
                 self.environment.deposit_pheromone(self.colony_id, 'home', current_pos_np, s.PHEROMONE_DEPOSIT_VALUE)

        # --- Kenarlar ve Engeller ---
        self.edges()
        self._handle_obstacle_collisions()


    def _handle_obstacle_collisions(self):
        """Engellerle çarpışmayı kontrol eder ve iter (V3'ten aynı)."""
        agent_pos_np = np.array([self.position.x, self.position.y])
        for obs in self.environment.obstacles:
            dist_vec_np = agent_pos_np - obs.position
            dist_sq = np.sum(dist_vec_np**2)
            min_dist = obs.radius + self.size * 1.5
            if dist_sq < min_dist**2 and dist_sq > 1e-6:
                distance = np.sqrt(dist_sq)
                penetration = min_dist - distance
                away_force_dir = dist_vec_np / distance
                force_magnitude = penetration * self.max_force * 5
                away_force = Vector2D(away_force_dir[0], away_force_dir[1]) * force_magnitude
                self.apply_force(away_force)
                self.velocity *= 0.95


    def apply_force(self, force: Vector2D):
        """İvmeye kuvvet ekler (Aynı)."""
        self.acceleration += force

    def edges(self):
        """Ekran kenarlarından sekme (Aynı)."""
        margin = 5
        turn_force = Vector2D(0,0)
        apply_turn = False
        pos = self.position; vel = self.velocity; max_s = self.max_speed; max_f = self.max_force * 3

        if pos.x < margin: turn_force.x = (max_s - vel.x); apply_turn=True
        elif pos.x > s.SCREEN_WIDTH - margin: turn_force.x = (-max_s - vel.x); apply_turn=True
        if pos.y < margin: turn_force.y = (max_s - vel.y); apply_turn=True
        elif pos.y > s.SCREEN_HEIGHT - margin: turn_force.y = (-max_s - vel.y); apply_turn=True

        if apply_turn:
             turn_force.limit(max_f)
             self.apply_force(turn_force)

    def draw(self, screen):
        """Ajanı kolonisine uygun renkte çizer."""
        # Rengi __init__ ve update içinde ayarladık
        current_color = self.color
        pos_int = (int(self.position.x), int(self.position.y))
        radius = int(self.size)

        # Basit daire çizimi
        pygame.draw.circle(screen, current_color, pos_int, radius)
        if self.has_food: # Yem taşıyorsa içine beyaz daire
            pygame.draw.circle(screen, (255,255,255), pos_int, int(radius * 0.5))