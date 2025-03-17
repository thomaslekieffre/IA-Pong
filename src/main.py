import sys
from typing import Tuple
import pygame
import math
pygame.init()  # Initialisation de pygame avant d'importer les autres modules

from elements import Paddle, Ball
from game_states import GameState, Menu, PauseScreen, GameOverScreen
from ai import SimpleAI
from stats import StatsManager

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WINNING_SCORE = 5

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AI Pong Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # États de jeu
        self.state = GameState.MENU
        self.menu = Menu(self.screen)
        self.pause_screen = PauseScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        # Gestionnaire de stats
        self.stats_manager = StatsManager()
        
        self.init_game()

    def init_game(self):
        # Création des éléments
        self.paddle1 = Paddle(50, WINDOW_HEIGHT//2 - 45)
        self.paddle2 = Paddle(WINDOW_WIDTH - 65, WINDOW_HEIGHT//2 - 45)
        self.ball = Ball(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        # Création des IA
        self.ai1 = SimpleAI(self.paddle1, difficulty=0.2)
        self.ai2 = SimpleAI(self.paddle2, difficulty=0.2)
        # Stats
        self.stats_manager.start_game()
        # Capture de l'écran pour le pause/game over
        self.game_screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.GAME_OVER:
                        self.init_game()
                        self.state = GameState.PLAYING

            if self.state == GameState.MENU:
                new_state = self.menu.handle_input(event)
                if new_state is None:
                    self.running = False
                elif new_state != self.state:
                    self.state = new_state

        # Suppression des contrôles clavier pour les raquettes

    def update(self):
        if self.state != GameState.PLAYING:
            return

        current_time = pygame.time.get_ticks() / 1000.0

        # Position des raquettes avant mise à jour
        old_pos1 = self.paddle1.rect.centery
        old_pos2 = self.paddle2.rect.centery

        # Mise à jour des IA
        self.ai1.update(self.ball, current_time)
        self.ai2.update(self.ball, current_time)

        # Calcul des temps de réaction
        reaction_time1 = abs(self.paddle1.rect.centery - old_pos1) / self.paddle1.speed if old_pos1 != self.paddle1.rect.centery else 0
        reaction_time2 = abs(self.paddle2.rect.centery - old_pos2) / self.paddle2.speed if old_pos2 != self.paddle2.rect.centery else 0

        # Mouvement de la balle
        old_speed = math.sqrt(self.ball.speed_x**2 + self.ball.speed_y**2)
        self.ball.move()

        # Collisions avec les murs
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= WINDOW_HEIGHT:
            self.ball.bounce("y")

        # Collisions avec les raquettes
        if self.ball.rect.colliderect(self.paddle1.rect):
            self.ball.bounce("x", self.paddle1)
            # Log du hit pour player 1
            ball_speed = math.sqrt(self.ball.speed_x**2 + self.ball.speed_y**2)
            accuracy = abs(self.ball.rect.centery - self.paddle1.rect.centery) / (self.paddle1.rect.height / 2)
            accuracy = max(0, 1 - accuracy)  # 1 = parfait, 0 = bord de la raquette
            self.stats_manager.log_hit("player1", ball_speed, reaction_time1, accuracy)
            
        elif self.ball.rect.colliderect(self.paddle2.rect):
            self.ball.bounce("x", self.paddle2)
            # Log du hit pour player 2
            ball_speed = math.sqrt(self.ball.speed_x**2 + self.ball.speed_y**2)
            accuracy = abs(self.ball.rect.centery - self.paddle2.rect.centery) / (self.paddle2.rect.height / 2)
            accuracy = max(0, 1 - accuracy)
            self.stats_manager.log_hit("player2", ball_speed, reaction_time2, accuracy)

        # Points
        if self.ball.rect.left <= 0:
            self.paddle2.score += 1
            self.stats_manager.log_score("player2")
            self.ball.reset(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        elif self.ball.rect.right >= WINDOW_WIDTH:
            self.paddle1.score += 1
            self.stats_manager.log_score("player1")
            self.ball.reset(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

        # Vérification de la victoire
        if self.paddle1.score >= WINNING_SCORE or self.paddle2.score >= WINNING_SCORE:
            stats = self.stats_manager.end_game()
            print(f"\nStats de la partie :")
            print(f"Durée : {stats.duration:.1f}s")
            print(f"Score : {stats.player1_score} - {stats.player2_score}")
            print(f"Nombre de hits : {stats.total_hits}")
            print(f"Longueur moyenne des échanges : {stats.avg_rally_length:.1f}")
            print(f"Plus long échange : {stats.max_rally_length}")
            print(f"Vitesse moyenne de la balle : {stats.ball_speed_avg:.1f}")
            print(f"Vitesse max de la balle : {stats.ball_speed_max:.1f}")
            print(f"Précision Joueur 1 : {stats.player1_accuracy:.1f}%")
            print(f"Précision Joueur 2 : {stats.player2_accuracy:.1f}%")
            self.state = GameState.GAME_OVER

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Dessiner les éléments
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        self.ball.draw(self.screen)

        # Afficher les scores
        font = pygame.font.Font(None, 74)
        score1 = font.render(str(self.paddle1.score), True, WHITE)
        score2 = font.render(str(self.paddle2.score), True, WHITE)
        self.screen.blit(score1, (WINDOW_WIDTH//4, 20))
        self.screen.blit(score2, (3*WINDOW_WIDTH//4, 20))

        # Afficher le nombre de rebonds
        hits_font = pygame.font.Font(None, 36)
        hits_text = hits_font.render(f"Rebonds: {self.ball.hits}", True, WHITE)
        self.screen.blit(hits_text, (WINDOW_WIDTH//2 - 50, 20))

        # Ligne centrale
        pygame.draw.aaline(self.screen, WHITE, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT))

    def draw(self):
        if self.state == GameState.MENU:
            self.menu.draw()
        elif self.state == GameState.PLAYING:
            self.draw_game()
            # Capture l'écran pour pause/game over
            self.game_screen.blit(self.screen, (0, 0))
        elif self.state == GameState.PAUSED:
            self.pause_screen.draw(self.game_screen)
        elif self.state == GameState.GAME_OVER:
            winner_score = max(self.paddle1.score, self.paddle2.score)
            loser_score = min(self.paddle1.score, self.paddle2.score)
            self.game_over_screen.draw(self.game_screen, winner_score, loser_score)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 