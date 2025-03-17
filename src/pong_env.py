import gymnasium as gym
import numpy as np
from gymnasium import spaces
import pygame
from elements import Ball, Paddle

class PongEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, opponent_difficulty=0.2):
        super().__init__()
        
        # Espace d'observation : [ball_x, ball_y, ball_vx, ball_vy, paddle_y, opponent_y]
        # Normalisé entre -1 et 1
        self.observation_space = spaces.Box(
            low=-1, high=1,
            shape=(6,),
            dtype=np.float32
        )
        
        # Actions : 0 = ne bouge pas, 1 = monte, 2 = descend
        self.action_space = spaces.Discrete(3)
        
        # Setup du jeu
        self.window_width = 800
        self.window_height = 600
        self.paddle_speed = 5
        self.opponent_difficulty = opponent_difficulty
        
        # Initialisation de pygame si pas déjà fait
        if not pygame.get_init():
            pygame.init()
        
        self.reset()
        
    def reset(self, seed=None):
        super().reset(seed=seed)
        
        # Reset des éléments du jeu
        self.paddle = Paddle(50, self.window_height//2 - 45)
        self.opponent = Paddle(self.window_width - 65, self.window_height//2 - 45)
        self.ball = Ball(self.window_width//2, self.window_height//2)
        
        # Stats pour la récompense
        self.hits = 0
        self.missed = False
        self.opponent_missed = False
        self.last_distance = self._get_paddle_ball_distance()
        
        return self._get_observation(), {}
    
    def step(self, action):
        # Action de l'agent
        if action == 1:  # Monter
            self.paddle.move(up=True)
        elif action == 2:  # Descendre
            self.paddle.move(up=False)
            
        # IA simple pour l'adversaire
        target_y = self.ball.rect.centery
        error = np.random.uniform(-50, 50) * self.opponent_difficulty
        target_y += error
        
        if self.opponent.rect.centery < target_y - 2:
            self.opponent.move(up=False)
        elif self.opponent.rect.centery > target_y + 2:
            self.opponent.move(up=True)
            
        # Mouvement de la balle
        self.ball.move()
        
        # Collisions avec les murs
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= self.window_height:
            self.ball.bounce("y")
            
        # Collisions avec les raquettes
        if self.ball.rect.colliderect(self.paddle.rect):
            self.ball.bounce("x", self.paddle)
            self.hits += 1
        elif self.ball.rect.colliderect(self.opponent.rect):
            self.ball.bounce("x", self.opponent)
            
        # Points et fin d'épisode
        terminated = False
        if self.ball.rect.left <= 0:
            self.missed = True
            terminated = True
        elif self.ball.rect.right >= self.window_width:
            self.opponent_missed = True
            terminated = True
            
        # Calcul de la récompense
        reward = self._calculate_reward()
        
        # Mise à jour de la distance pour la prochaine frame
        self.last_distance = self._get_paddle_ball_distance()
        
        return self._get_observation(), reward, terminated, False, {}
    
    def _get_observation(self):
        # Normalisation des observations entre -1 et 1
        return np.array([
            self.ball.rect.centerx / (self.window_width/2) - 1,  # x position
            self.ball.rect.centery / (self.window_height/2) - 1,  # y position
            self.ball.speed_x / self.ball.max_speed,  # x velocity
            self.ball.speed_y / self.ball.max_speed,  # y velocity
            self.paddle.rect.centery / (self.window_height/2) - 1,  # paddle y
            self.opponent.rect.centery / (self.window_height/2) - 1  # opponent y
        ], dtype=np.float32)
    
    def _get_paddle_ball_distance(self):
        """Calcule la distance entre la raquette et la balle"""
        return abs(self.paddle.rect.centery - self.ball.rect.centery)
    
    def _calculate_reward(self):
        """Calcule la récompense basée sur plusieurs facteurs"""
        reward = 0
        
        # Récompense/pénalité pour le résultat
        if self.missed:
            reward -= 2.0  # Grosse pénalité si on rate la balle
        elif self.opponent_missed:
            reward += 2.0  # Grosse récompense si l'adversaire rate
            
        # Récompense pour les hits
        if self.ball.rect.colliderect(self.paddle.rect):
            reward += 0.5  # Récompense pour toucher la balle
            
            # Bonus pour la précision
            accuracy = abs(self.ball.rect.centery - self.paddle.rect.centery) / (self.paddle.rect.height / 2)
            accuracy = max(0, 1 - accuracy)
            reward += accuracy * 0.3
            
        # Récompense pour se rapprocher de la balle quand elle vient vers nous
        if self.ball.speed_x < 0:  # Si la balle vient vers nous
            current_distance = self._get_paddle_ball_distance()
            if current_distance < self.last_distance:
                reward += 0.1  # Petit bonus pour se rapprocher de la balle
                
        return reward
    
    def render(self):
        pass  # On utilise déjà le rendu de main.py
        
    def close(self):
        pass 