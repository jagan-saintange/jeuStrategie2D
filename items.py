import pygame
import math

class Tourelle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 200  # Portée de la tourelle
        self.damage = 10
        self.target = None
        self.reload_time = 1  # Temps entre les tirs (secondes)
        self.last_shot = pygame.time.get_ticks()

    def find_target(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= self.range:
                self.target = enemy
                return

    def shoot(self):
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot >= self.reload_time * 1000:
            self.target.health -= self.damage
            print(f"Tir sur l'ennemi ! Santé restante : {self.target.health}")
            self.last_shot = now

    def draw(self, screen):
        pygame.draw.circle(screen, (150, 150, 150), (self.x, self.y), 20)  # Dessine la tourelle
        if self.target:
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.target.x, self.target.y))

class MineCryogenique:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 50  # Zone d'effet
        self.damage = 0
        self.slow_effect = 0.5  # Réduction de vitesse (50 %)
        self.active = True

    def trigger(self, enemies):
        if self.active:
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance <= self.radius:
                    enemy.speed *= self.slow_effect
                    print(f"Ennemi ralenti ! Vitesse actuelle : {enemy.speed}")
            self.active = False  # Désactivation après l'explosion

    def draw(self, screen):
        color = (0, 0, 255) if self.active else (100, 100, 100)
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius, 2)

class ChampDeBrouillage:
    def __init__(self, x, y, duration=5):
        self.x = x
        self.y = y
        self.radius = 150
        self.duration = duration  # Durée en secondes
        self.start_time = None

    def activate(self):
        self.start_time = pygame.time.get_ticks()
        print("Champ de brouillage activé !")

    def is_active(self):
        if self.start_time:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            return elapsed < self.duration
        return False

    def affect_enemies(self, enemies):
        if self.is_active():
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance <= self.radius:
                    enemy.special_ability = False  # Désactive les capacités spéciales
                    print(f"Capacités désactivées pour l'ennemi à {distance} unités.")

    def draw(self, screen):
        if self.is_active():
            pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.radius, 2)


