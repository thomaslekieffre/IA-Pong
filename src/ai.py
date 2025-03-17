import random
import pygame

class SimpleAI:
    def __init__(self, paddle, difficulty=0.2):  # Difficulté réduite = plus précis
        self.paddle = paddle
        self.difficulty = difficulty
        self.reaction_delay = 0.02  # Délai réduit = plus rapide
        self.last_move_time = 0
        self.prediction_range = 200  # Distance de prédiction en pixels
        
    def update(self, ball, current_time):
        actual_delay = self.reaction_delay * (1 + self.difficulty)
        
        if current_time - self.last_move_time < actual_delay:
            return
            
        # Prédiction basique de la position future de la balle
        predicted_y = ball.rect.centery + (ball.speed_y * self.prediction_range / abs(ball.speed_x) if ball.speed_x != 0 else 0)
        
        # Position cible avec prédiction
        target_y = predicted_y
        
        # Erreur réduite et proportionnelle à la distance
        distance_to_ball = abs(ball.rect.x - self.paddle.rect.x)
        error_factor = min(1.0, distance_to_ball / 400)  # Plus précis quand la balle est proche
        error = random.uniform(-20, 20) * self.difficulty * error_factor
        target_y += error
        
        # Limite la position cible aux bords de l'écran
        target_y = max(self.paddle.rect.height/2, min(target_y, pygame.display.get_surface().get_height() - self.paddle.rect.height/2))
        
        # Déplace la raquette vers la cible avec une marge de tolérance plus petite
        if self.paddle.rect.centery < target_y - 2:
            self.paddle.move(up=False)
        elif self.paddle.rect.centery > target_y + 2:
            self.paddle.move(up=True)
            
        self.last_move_time = current_time 