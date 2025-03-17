import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
import os

class DQN(nn.Module):
    def __init__(self, input_size, output_size, hidden_size=128):
        super(DQN, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
        
    def forward(self, x):
        return self.network(x)

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
        
    def push(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def __len__(self):
        return len(self.memory)

class QLearningAgent:
    def __init__(self, state_size, action_size, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.state_size = state_size
        self.action_size = action_size
        self.device = device
        
        # Hyperparamètres
        self.gamma = 0.99  # Facteur de réduction
        self.epsilon = 1.0  # Exploration initiale à 100%
        self.epsilon_min = 0.05  # Exploration minimale à 5%
        self.epsilon_decay = 0.9995  # Décroissance plus lente
        self.learning_rate = 0.0005  # Learning rate plus petit pour stabilité
        self.batch_size = 128  # Batch size plus grand
        self.train_start = 1000  # Commence l'entraînement après 1000 exemples
        
        # Réseaux plus grands
        self.model = DQN(state_size, action_size, hidden_size=128).to(device)
        self.target_model = DQN(state_size, action_size, hidden_size=128).to(device)
        self.target_model.load_state_dict(self.model.state_dict())
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.memory = ReplayMemory(50000)  # Mémoire plus grande
        
        # Pour le suivi des performances
        self.training_step = 0
        
    def update_target_model(self):
        """Met à jour le réseau target avec les poids du réseau principal"""
        self.target_model.load_state_dict(self.model.state_dict())
        
    def get_action(self, state):
        """Sélectionne une action selon la politique epsilon-greedy"""
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
            
        with torch.no_grad():
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.model(state)
            return q_values.argmax().item()
            
    def train_step(self):
        """Effectue une étape d'entraînement sur un batch"""
        if len(self.memory) < self.train_start:
            return
            
        # Sample batch
        batch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Conversion en tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Calcul des Q-values
        current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_model(next_states).max(1)[0].detach()
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Calcul de la perte et optimisation
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Mise à jour de epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Mise à jour périodique du réseau target
        self.training_step += 1
        if self.training_step % 100 == 0:
            self.update_target_model()
            
        return loss.item()
        
    def save(self, filename):
        """Sauvegarde le modèle"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step
        }, filename)
        
    def load(self, filename):
        """Charge le modèle"""
        if os.path.exists(filename):
            checkpoint = torch.load(filename)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            self.training_step = checkpoint['training_step'] 