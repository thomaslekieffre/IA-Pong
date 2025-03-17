import pygame
import math
import random
from typing import Tuple

class Paddle:
    def __init__(self, x: int, y: int, width: int = 15, height: int = 90):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 5
        self.score = 0
        self.movement = 0  # Pour tracker le mouvement de la raquette

    def move(self, up: bool = True):
        previous_y = self.rect.y
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        elif not up and self.rect.bottom < 600:
            self.rect.y += self.speed
        self.movement = self.rect.y - previous_y

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

class Ball:
    def __init__(self, x: int, y: int, size: int = 15):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = 6  # Vitesse de base augmentée
        self.speed_x = self.base_speed
        self.speed_y = 0
        self.size = size
        self.max_speed = 12  # Vitesse max augmentée
        self.min_angle = 15  # Angle minimum en degrés
        self.hits = 0

    def move(self):
        # Assure une vitesse minimale en X
        if abs(self.speed_x) < self.base_speed:
            self.speed_x = math.copysign(self.base_speed, self.speed_x)
        
        # Limite la vitesse Y pour éviter les angles trop verticaux
        max_speed_y = abs(self.speed_x) * math.tan(math.radians(75))  # Max 75 degrés
        self.speed_y = max(min(self.speed_y, max_speed_y), -max_speed_y)
        
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def bounce(self, axis: str = "y", paddle: Paddle = None):
        if axis == "y":
            self.speed_y *= -1
            # Ajoute une petite perturbation aléatoire sur rebond mur
            self.speed_y += random.uniform(-0.5, 0.5)
        else:
            # Inverse la direction X
            self.speed_x *= -1
            
            if paddle:
                # Calcul de l'angle de rebond basé sur le point d'impact
                relative_intersect_y = (paddle.rect.centery - self.rect.centery)
                normalized_intersect = relative_intersect_y / (paddle.rect.height / 2)
                
                # Assure un angle minimum
                if abs(normalized_intersect) < math.sin(math.radians(self.min_angle)):
                    normalized_intersect = math.copysign(math.sin(math.radians(self.min_angle)), normalized_intersect)
                
                bounce_angle = normalized_intersect * 60  # Max 60 degrés
                
                # Ajout de l'effet de la raquette en mouvement
                paddle_effect = paddle.movement * 0.3  # Effet augmenté
                
                # Conversion en vélocités avec accélération plus importante
                speed = min(abs(self.speed_x) + 0.4, self.max_speed)
                self.speed_x = math.copysign(speed * math.cos(math.radians(bounce_angle)), self.speed_x)
                self.speed_y = speed * -math.sin(math.radians(bounce_angle)) + paddle_effect
                
                self.hits += 1

    def reset(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
        # Réinitialisation avec angle minimum garanti
        angle = random.uniform(self.min_angle, 45)
        if random.random() < 0.5:
            angle = -angle
        
        self.speed_x = self.base_speed * random.choice([-1, 1])
        self.speed_y = self.base_speed * math.tan(math.radians(angle))
        self.hits = 0

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.size // 2) 