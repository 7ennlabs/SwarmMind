# swarm_mind_v1/vector.py
import math
import random

class Vector2D:
    """2 Boyutlu Vektör Sınıfı."""
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __str__(self):
        """Vektörün string temsilini döndürür."""
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def __add__(self, other):
        """Vektör toplama (+) operatörü."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Vektör çıkarma (-) operatörü."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Skaler ile çarpma (*) operatörü."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        """Skaler ile bölme (/) operatörü."""
        if scalar == 0:
            return Vector2D() # Sıfıra bölme hatasını önle
        return Vector2D(self.x / scalar, self.y / scalar)

    def magnitude_squared(self):
        """Vektörün büyüklüğünün karesini döndürür (sqrt daha yavaştır)."""
        return self.x * self.x + self.y * self.y

    def magnitude(self):
        """Vektörün büyüklüğünü (uzunluğunu) döndürür."""
        mag_sq = self.magnitude_squared()
        if mag_sq == 0:
            return 0.0
        return math.sqrt(mag_sq)

    def normalize(self):
        """Vektörü birim vektöre dönüştürür (büyüklüğü 1 yapar)."""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
        return self # Zincirleme için kendini döndür

    def get_normalized(self):
        """Vektörün normalize edilmiş bir kopyasını döndürür."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D()
        return Vector2D(self.x / mag, self.y / mag)

    def limit(self, max_magnitude):
        """Vektörün büyüklüğünü verilen maksimum değerle sınırlar."""
        if self.magnitude_squared() > max_magnitude * max_magnitude:
            self.normalize()
            self.x *= max_magnitude
            self.y *= max_magnitude
        return self # Zincirleme için kendini döndür

    def distance_squared(self, other):
        """İki vektör arasındaki mesafenin karesini döndürür."""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def distance(self, other):
        """İki vektör arasındaki mesafeyi döndürür."""
        return math.sqrt(self.distance_squared(other))

    def set_magnitude(self, magnitude):
        """Vektörün büyüklüğünü ayarlar."""
        self.normalize()
        self.x *= magnitude
        self.y *= magnitude
        return self

    def heading(self):
        """Vektörün açısını (radyan cinsinden) döndürür."""
        return math.atan2(self.y, self.x)

    @staticmethod
    def random_vector():
        """Rastgele bir yönü olan birim vektör oluşturur."""
        angle = random.uniform(0, 2 * math.pi)
        return Vector2D(math.cos(angle), math.sin(angle))