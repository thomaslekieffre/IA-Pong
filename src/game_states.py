from enum import Enum, auto
import pygame

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Jouer", "Quitter"]
        self.selected = 0
        self.font = pygame.font.Font(None, 74)

    def draw(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("AI PONG BATTLE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title, title_rect)

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen.get_width()//2, 300 + i * 100))
            self.screen.blit(text, rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:  # Jouer
                    return GameState.PLAYING
                else:  # Quitter
                    return None
        return GameState.MENU

class PauseScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(128)

    def draw(self, game_screen):
        # Garde l'écran de jeu en arrière-plan
        self.screen.blit(game_screen, (0, 0))
        self.screen.blit(self.overlay, (0, 0))
        
        text = self.font.render("PAUSE", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, rect)
        
        sub_font = pygame.font.Font(None, 36)
        sub_text = sub_font.render("Appuyez sur ESPACE pour continuer", True, (255, 255, 255))
        sub_rect = sub_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
        self.screen.blit(sub_text, sub_rect)

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(180)

    def draw(self, game_screen, winner_score, loser_score):
        self.screen.blit(game_screen, (0, 0))
        self.screen.blit(self.overlay, (0, 0))
        
        text = self.font.render(f"GAME OVER", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        self.screen.blit(text, rect)
        
        score_text = self.font.render(f"{winner_score} - {loser_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        sub_font = pygame.font.Font(None, 36)
        sub_text = sub_font.render("Appuyez sur ESPACE pour rejouer", True, (255, 255, 255))
        sub_rect = sub_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 80))
        self.screen.blit(sub_text, sub_rect) 