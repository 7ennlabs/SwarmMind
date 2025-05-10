# swarm_mind_v4/environment.py
import pygame
import numpy as np
import random
import settings as s # Ayarları 's' takma adıyla içeri aktar

class FoodSource:
    """Basit bir yem kaynağı sınıfı (V3'ten aynı)."""
    def __init__(self, position, initial_amount, radius):
        self.position = np.array(position, dtype=np.float32)
        self.amount = initial_amount
        self.radius = radius
        self.color = s.COLOR_FOOD

    def take(self) -> bool:
        if self.amount > 0:
            self.amount -= 1
            return True
        return False

    def is_empty(self) -> bool:
        return self.amount <= 0

    def draw(self, screen):
        if self.amount > 0: # Sadece içinde yem varsa çiz
            brightness = max(0.2, min(1.0, self.amount / s.FOOD_INITIAL_AMOUNT)) # Min parlaklık ekle
            color = (int(self.color[0] * brightness),
                     int(self.color[1] * brightness),
                     int(self.color[2] * brightness))
            pygame.draw.circle(screen, color, self.position.astype(int), self.radius)

# V3/V4: Engel Sınıfı
class Obstacle:
    """Basit dairesel bir engeli temsil eder."""
    def __init__(self, position, radius):
        self.position = np.array(position, dtype=np.float32)
        self.radius = radius
        self.color = s.COLOR_OBSTACLE

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position.astype(int), int(self.radius))

class Environment:
    """
    Simülasyon ortamını yönetir (V4: İki Koloni, Ayrı Feromonlar, Dinamik Yem, Engeller).
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_res = s.PHEROMONE_RESOLUTION
        self.grid_width = width // self.grid_res
        self.grid_height = height // self.grid_res

        # V4: Koloniye özel feromon ızgaraları
        self.home_pheromone_grids = {
            s.COLONY_ID_RED: np.zeros((self.grid_width, self.grid_height), dtype=np.float32),
            s.COLONY_ID_BLUE: np.zeros((self.grid_width, self.grid_height), dtype=np.float32)
        }
        self.food_pheromone_grids = {
             s.COLONY_ID_RED: np.zeros((self.grid_width, self.grid_height), dtype=np.float32),
             s.COLONY_ID_BLUE: np.zeros((self.grid_width, self.grid_height), dtype=np.float32)
        }

        # V4: İki Yuva
        self.nest_positions = {
            s.COLONY_ID_RED: s.NEST_POS_RED.astype(np.float32),
            s.COLONY_ID_BLUE: s.NEST_POS_BLUE.astype(np.float32)
        }
        self.nest_radius = s.NEST_RADIUS
        self.nest_colors = {
             s.COLONY_ID_RED: s.COLOR_NEST_RED,
             s.COLONY_ID_BLUE: s.COLOR_NEST_BLUE
        }

        # Dinamik Yem Kaynakları
        self.food_sources = []

        # Engeller
        self.obstacles = self._create_obstacles()

        # Başlangıç yemleri
        for _ in range(s.MAX_FOOD_SOURCES // 2):
              self._try_spawn_food()

        # Feromonları çizmek için yüzey
        self.pheromone_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def _create_obstacles(self):
        """Ortama rastgele engeller yerleştirir."""
        obstacles = []
        attempts = 0
        max_attempts = s.NUM_OBSTACLES * 15

        while len(obstacles) < s.NUM_OBSTACLES and attempts < max_attempts:
            attempts += 1
            radius = random.uniform(s.OBSTACLE_MIN_RADIUS, s.OBSTACLE_MAX_RADIUS)
            margin = radius + 20
            pos = np.array([random.uniform(margin, self.width - margin),
                            random.uniform(margin, self.height - margin)], dtype=np.float32)

            # Yuvalarla çarpışıyor mu?
            nest_collision = False
            for nest_pos in self.nest_positions.values():
                 if np.linalg.norm(pos - nest_pos) < self.nest_radius + radius + 15:
                      nest_collision = True
                      break
            if nest_collision: continue

            # Diğer engellerle çarpışıyor mu?
            obstacle_collision = False
            for obs in obstacles:
                if np.linalg.norm(pos - obs.position) < obs.radius + radius + 10:
                    obstacle_collision = True
                    break
            if not obstacle_collision:
                obstacles.append(Obstacle(pos, radius))

        print(f"Created {len(obstacles)} obstacles.")
        return obstacles

    def _try_spawn_food(self):
        """Ortama yeni bir yem kaynağı eklemeyi dener."""
        if len(self.food_sources) >= s.MAX_FOOD_SOURCES: return

        attempts = 0
        max_attempts = 30
        while attempts < max_attempts:
            attempts += 1
            margin = s.FOOD_RADIUS + 15
            pos = np.array([random.uniform(margin, self.width - margin),
                            random.uniform(margin, self.height - margin)], dtype=np.float32)

            # Yuvalarla çarpışıyor mu?
            nest_collision = False
            for nest_pos in self.nest_positions.values():
                 if np.linalg.norm(pos - nest_pos) < self.nest_radius + s.FOOD_RADIUS + 25:
                      nest_collision = True
                      break
            if nest_collision: continue

            # Engellerle çarpışıyor mu?
            obstacle_collision = False
            for obs in self.obstacles:
                if np.linalg.norm(pos - obs.position) < obs.radius + s.FOOD_RADIUS + 15:
                    obstacle_collision = True
                    break
            if obstacle_collision: continue

             # Diğer yem kaynaklarına çok yakın mı?
            food_collision = False
            for fs in self.food_sources:
                 if np.linalg.norm(pos - fs.position) < s.FOOD_RADIUS * 5:
                      food_collision = True
                      break
            if food_collision: continue

            # Uygun yer bulundu
            self.food_sources.append(FoodSource(pos, s.FOOD_INITIAL_AMOUNT, s.FOOD_RADIUS))
            return

    def update(self):
        """Ortamı her adımda günceller."""
        self._update_pheromones()

        # Yem Kaynaklarını Yönet
        if s.FOOD_DEPLETION_REMOVAL:
            self.food_sources = [fs for fs in self.food_sources if not fs.is_empty()]
        if random.random() < s.FOOD_SPAWN_RATE:
            self._try_spawn_food()

    def world_to_grid(self, world_pos: np.ndarray) -> tuple[int, int]:
        """Dünya koordinatlarını ızgara indekslerine dönüştürür."""
        gx = int(world_pos[0] / self.grid_res)
        gy = int(world_pos[1] / self.grid_res)
        gx = np.clip(gx, 0, self.grid_width - 1)
        gy = np.clip(gy, 0, self.grid_height - 1)
        return gx, gy

    def deposit_pheromone(self, colony_id: int, pheromone_type: str, world_pos: np.ndarray, amount: float):
        """Belirtilen konuma, belirtilen koloninin feromonunu bırakır."""
        gx, gy = self.world_to_grid(world_pos)
        # Doğru ızgarayı seç
        if pheromone_type == 'home':
            grid = self.home_pheromone_grids.get(colony_id) # .get() ile None dönebilir
        elif pheromone_type == 'food':
             grid = self.food_pheromone_grids.get(colony_id)
        else:
            grid = None # Bilinmeyen tür veya hatalı colony_id

        if grid is not None:
            grid[gx, gy] += amount
            grid[gx, gy] = np.clip(grid[gx, gy], 0, s.PHEROMONE_MAX_STRENGTH)

    def _diffuse_and_evaporate(self, grid: np.ndarray) -> np.ndarray:
        """Tek bir feromon ızgarasını günceller."""
        padded_grid = np.pad(grid, 1, mode='constant')
        center_weight = 1.0 - (s.PHEROMONE_DIFFUSION_RATE * 8)
        neighbor_weight = s.PHEROMONE_DIFFUSION_RATE
        # Komşuların ağırlıklı toplamı (daha okunabilir)
        neighbors_sum = (padded_grid[:-2, 1:-1] + padded_grid[2:, 1:-1] +   # Yukarı/Aşağı
                         padded_grid[1:-1, :-2] + padded_grid[1:-1, 2:] +   # Sol/Sağ
                         padded_grid[:-2, :-2] + padded_grid[:-2, 2:] +     # SolÜst/SağÜst
                         padded_grid[2:, :-2] + padded_grid[2:, 2:])        # SolAlt/SağAlt
        diffused = (padded_grid[1:-1, 1:-1] * center_weight + neighbors_sum * neighbor_weight)
        evaporated = diffused * (1.0 - s.PHEROMONE_EVAPORATION_RATE)
        return np.clip(evaporated, 0, s.PHEROMONE_MAX_STRENGTH)

    def _update_pheromones(self):
        """Tüm feromon ızgaralarını günceller."""
        for colony_id in self.home_pheromone_grids:
            self.home_pheromone_grids[colony_id] = self._diffuse_and_evaporate(self.home_pheromone_grids[colony_id])
            self.food_pheromone_grids[colony_id] = self._diffuse_and_evaporate(self.food_pheromone_grids[colony_id])

    def get_pheromone_strength(self, colony_id: int, pheromone_type: str, world_pos: np.ndarray) -> float:
        """Belirtilen koloninin, belirtilen türdeki feromon gücünü alır."""
        gx, gy = self.world_to_grid(world_pos)
        if pheromone_type == 'home':
            grid = self.home_pheromone_grids.get(colony_id)
        elif pheromone_type == 'food':
             grid = self.food_pheromone_grids.get(colony_id)
        else: return 0.0

        return grid[gx, gy] if grid is not None else 0.0

    def sense_pheromones_at(self, colony_id: int, pheromone_type: str, sample_points: list[np.ndarray]) -> np.ndarray:
        """Verilen noktalardaki belirtilen koloniye ait feromon yoğunluklarını döndürür."""
        strengths = []
        # Doğru ızgarayı seç
        if pheromone_type == 'home':
            grid = self.home_pheromone_grids.get(colony_id)
        elif pheromone_type == 'food':
             grid = self.food_pheromone_grids.get(colony_id)
        else: grid = None

        if grid is None: return np.zeros(len(sample_points), dtype=np.float32)

        for point in sample_points:
            gx, gy = self.world_to_grid(point)
            strengths.append(grid[gx, gy])
        return np.array(strengths, dtype=np.float32)

    def get_food_sources(self) -> list[FoodSource]:
        """Aktif yem kaynaklarının listesi."""
        return [fs for fs in self.food_sources if not fs.is_empty()]

    # === Bu metot environment.py içinde olmalı ===
    def get_closest_food(self, world_pos: np.ndarray) -> tuple[np.ndarray | None, float, np.ndarray]:
        """Verilen konuma en yakın aktif yem kaynağını bulur.
           Döndürülenler: (kaynak_pozisyonu, uzaklık_karesi, yön_vektörü_normalize)
           Eğer kaynak yoksa: (None, float('inf'), np.zeros(2))
        """
        closest_fs = None
        min_dist_sq = float('inf')
        active_foods = self.get_food_sources() # Aktif olanları al

        for fs in active_foods:
            dist_sq = np.sum((fs.position - world_pos)**2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_fs = fs

        if closest_fs:
            direction_vec = closest_fs.position - world_pos
            dist = np.sqrt(min_dist_sq)
            if dist > 1e-6:
                normalized_direction = direction_vec / dist
            else:
                normalized_direction = np.zeros(2, dtype=np.float32)
            return closest_fs.position, min_dist_sq, normalized_direction
        else:
            return None, float('inf'), np.zeros(2, dtype=np.float32)
    # ============================================

    def get_nest_position(self, colony_id: int) -> np.ndarray:
        """Belirtilen koloninin yuva pozisyonunu döndürür."""
        return self.nest_positions.get(colony_id) # .get() ile None dönebilir

    def is_at_nest(self, colony_id: int, world_pos: np.ndarray) -> bool:
        """Pozisyonun belirtilen koloninin yuvasında olup olmadığını kontrol eder."""
        nest_pos = self.nest_positions.get(colony_id)
        if nest_pos is None: return False
        return np.linalg.norm(world_pos - nest_pos) < self.nest_radius

    def check_obstacle_collision(self, world_pos: np.ndarray, radius: float) -> bool:
        """Engelle çarpışma kontrolü."""
        for obs in self.obstacles:
            if np.linalg.norm(world_pos - obs.position) < obs.radius + radius:
                return True
        return False

    def draw(self, screen):
        """Ortamın tüm bileşenlerini çizer."""
        if s.DEBUG_DRAW_PHEROMONES:
            self._draw_pheromones(screen)
        if s.DEBUG_DRAW_NESTS:
            self._draw_nests(screen)
        if s.DEBUG_DRAW_FOOD_LOCATIONS:
            self._draw_food_sources(screen)
        if s.DEBUG_DRAW_OBSTACLES:
            self._draw_obstacles(screen)

    def _draw_pheromones(self, screen):
        """Her iki koloninin feromonlarını ayrı renklerle çizer."""
        self.pheromone_surface.fill((0, 0, 0, 0))
        res = self.grid_res
        pheromone_colors = {
            'home_red': s.COLOR_PHEROMONE_HOME_RED,
            'home_blue': s.COLOR_PHEROMONE_HOME_BLUE,
            'food_red': (*s.COLOR_PHEROMONE_HOME_RED[:3], s.COLOR_PHEROMONE_HOME_RED[3] // 2), # Daha soluk
            'food_blue': (*s.COLOR_PHEROMONE_HOME_BLUE[:3], s.COLOR_PHEROMONE_HOME_BLUE[3] // 2) # Daha soluk
        }
        grids_to_draw = {
            'home_red': self.home_pheromone_grids.get(s.COLONY_ID_RED),
            'home_blue': self.home_pheromone_grids.get(s.COLONY_ID_BLUE),
            'food_red': self.food_pheromone_grids.get(s.COLONY_ID_RED),
            'food_blue': self.food_pheromone_grids.get(s.COLONY_ID_BLUE)
        }

        for p_type, grid in grids_to_draw.items():
            if grid is None: continue # Izgara yoksa atla
            color_info = pheromone_colors[p_type]
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    strength = grid[x, y]
                    if strength > 0.01:
                        alpha = int(np.clip(strength / s.PHEROMONE_MAX_STRENGTH, 0, 1) * color_info[3])
                        color = (*color_info[:3], alpha)
                        rect = pygame.Rect(x * res, y * res, res, res)
                        pygame.draw.rect(self.pheromone_surface, color, rect)

        screen.blit(self.pheromone_surface, (0, 0))


    def _draw_nests(self, screen):
        """Her iki yuvayı da çizer."""
        for colony_id, nest_pos in self.nest_positions.items():
            color = self.nest_colors.get(colony_id, (128,128,128)) # Hata durumunda gri
            pygame.draw.circle(screen, color, nest_pos.astype(int), self.nest_radius)
            pygame.draw.circle(screen, (color[0]//2, color[1]//2, color[2]//2),
                               nest_pos.astype(int), self.nest_radius - 3)

    def _draw_food_sources(self, screen):
        """Aktif yem kaynaklarını çizer."""
        for fs in self.food_sources:
            fs.draw(screen)

    def _draw_obstacles(self, screen):
        """Engelleri çizer."""
        for obs in self.obstacles:
            obs.draw(screen)