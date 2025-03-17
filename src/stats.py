import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict
import os
from datetime import datetime

@dataclass
class GameStats:
    timestamp: float
    duration: float
    player1_score: int
    player2_score: int
    total_hits: int
    avg_rally_length: float
    max_rally_length: int
    ball_speed_avg: float
    ball_speed_max: float
    player1_reaction_times: List[float]
    player2_reaction_times: List[float]
    player1_accuracy: float  # % de fois où la balle est touchée au bon endroit
    player2_accuracy: float

class StatsManager:
    def __init__(self, save_dir: str = "stats"):
        self.save_dir = save_dir
        self.current_game = None
        self.current_rally_hits = 0
        self.rally_lengths = []
        self.ball_speeds = []
        self.reaction_times = {"player1": [], "player2": []}
        self.paddle_positions = {"player1": [], "player2": []}
        
        # Crée le dossier de stats s'il n'existe pas
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def start_game(self):
        """Démarre une nouvelle partie"""
        self.current_game = {
            "start_time": time.time(),
            "hits": 0,
            "scores": {"player1": 0, "player2": 0}
        }
        self.current_rally_hits = 0
        self.rally_lengths = []
        self.ball_speeds = []
        self.reaction_times = {"player1": [], "player2": []}
        self.paddle_positions = {"player1": [], "player2": []}
    
    def log_hit(self, player: str, ball_speed: float, reaction_time: float, accuracy: float):
        """Enregistre un hit de balle"""
        if not self.current_game:
            return
            
        self.current_game["hits"] += 1
        self.current_rally_hits += 1
        self.ball_speeds.append(ball_speed)
        self.reaction_times[player].append(reaction_time)
        
    def log_score(self, scorer: str):
        """Enregistre un point marqué"""
        if not self.current_game:
            return
            
        self.current_game["scores"][scorer] += 1
        self.rally_lengths.append(self.current_rally_hits)
        self.current_rally_hits = 0
    
    def end_game(self) -> GameStats:
        """Termine la partie et retourne les stats"""
        if not self.current_game:
            return None
            
        duration = time.time() - self.current_game["start_time"]
        
        # Calcul des stats
        stats = GameStats(
            timestamp=self.current_game["start_time"],
            duration=duration,
            player1_score=self.current_game["scores"]["player1"],
            player2_score=self.current_game["scores"]["player2"],
            total_hits=self.current_game["hits"],
            avg_rally_length=sum(self.rally_lengths) / len(self.rally_lengths) if self.rally_lengths else 0,
            max_rally_length=max(self.rally_lengths) if self.rally_lengths else 0,
            ball_speed_avg=sum(self.ball_speeds) / len(self.ball_speeds) if self.ball_speeds else 0,
            ball_speed_max=max(self.ball_speeds) if self.ball_speeds else 0,
            player1_reaction_times=self.reaction_times["player1"],
            player2_reaction_times=self.reaction_times["player2"],
            player1_accuracy=self._calculate_accuracy("player1"),
            player2_accuracy=self._calculate_accuracy("player2")
        )
        
        # Sauvegarde des stats
        self._save_stats(stats)
        
        self.current_game = None
        return stats
    
    def _calculate_accuracy(self, player: str) -> float:
        """Calcule la précision d'un joueur"""
        hits = len(self.reaction_times[player])
        if not hits:
            return 0.0
        # On considère qu'un temps de réaction < 0.1s est "précis"
        good_hits = sum(1 for t in self.reaction_times[player] if t < 0.1)
        return good_hits / hits * 100
    
    def _save_stats(self, stats: GameStats):
        """Sauvegarde les stats dans un fichier JSON"""
        timestamp = datetime.fromtimestamp(stats.timestamp)
        filename = f"{self.save_dir}/game_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(stats), f, indent=2) 