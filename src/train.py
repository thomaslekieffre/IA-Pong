import os
import numpy as np
from pong_env import PongEnv
from q_agent import QLearningAgent
import matplotlib.pyplot as plt
from collections import deque
import json
import time

def plot_training_progress(scores, avg_scores, filename="training_progress.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(scores, label='Score', alpha=0.4)
    plt.plot(avg_scores, label='Score moyen (100 épisodes)', linewidth=2)
    plt.xlabel('Épisode')
    plt.ylabel('Score')
    plt.legend()
    plt.savefig(filename)
    plt.close()

def train(save_interval=50, model_dir="models", stats_dir="training_stats", load_model=True):
    # Création des dossiers si nécessaire
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(stats_dir, exist_ok=True)
    
    # Initialisation
    env = PongEnv(opponent_difficulty=0.2)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = QLearningAgent(state_size, action_size)
    
    # Chargement du meilleur modèle précédent s'il existe
    best_model_path = os.path.join(model_dir, "best_model.pth")
    if load_model and os.path.exists(best_model_path):
        print("Chargement du meilleur modèle précédent...")
        agent.load(best_model_path)
        # On remet epsilon à 0.5 pour permettre plus d'exploration
        agent.epsilon = 0.5
        print(f"Modèle chargé avec epsilon = {agent.epsilon}")
    else:
        print("Pas de modèle précédent trouvé, démarrage d'un nouvel entraînement")
        # On commence avec beaucoup d'exploration
        agent.epsilon = 1.0
        # On ralentit la décroissance d'epsilon
        agent.epsilon_decay = 0.9995
        agent.epsilon_min = 0.05  # On garde un minimum d'exploration
    
    # Pour le suivi des performances
    scores = []
    avg_scores = []
    score_window = deque(maxlen=100)
    best_avg_score = -np.inf
    episode = 0
    
    # Stats d'entraînement
    training_stats = {
        "episodes": [],
        "scores": [],
        "avg_scores": [],
        "epsilon": [],
        "losses": []
    }
    
    print("Début de l'entraînement continu (Ctrl+C pour arrêter)...")
    print(f"Epsilon initial: {agent.epsilon}")
    print(f"Epsilon decay: {agent.epsilon_decay}")
    print(f"Epsilon minimum: {agent.epsilon_min}")
    start_time = time.time()
    
    try:
        while True:  # Boucle infinie
            episode += 1
            state, _ = env.reset()
            score = 0
            episode_losses = []
            
            while True:
                # Sélection et exécution de l'action
                action = agent.get_action(state)
                next_state, reward, done, _, _ = env.step(action)
                
                # Enregistrement dans la mémoire et entraînement
                agent.memory.push(state, action, reward, next_state, done)
                loss = agent.train_step()
                if loss is not None:
                    episode_losses.append(loss)
                
                state = next_state
                score += reward
                
                if done:
                    break
            
            # Mise à jour des stats
            score_window.append(score)
            scores.append(score)
            avg_score = np.mean(score_window)
            avg_scores.append(avg_score)
            
            # Sauvegarde des stats
            training_stats["episodes"].append(episode)
            training_stats["scores"].append(score)
            training_stats["avg_scores"].append(avg_score)
            training_stats["epsilon"].append(agent.epsilon)
            training_stats["losses"].append(np.mean(episode_losses) if episode_losses else 0)
            
            # Affichage des progrès
            if episode % 10 == 0:
                elapsed_time = time.time() - start_time
                print(f"\nTemps écoulé: {elapsed_time/3600:.2f} heures")
                print(f"Épisode {episode}")
                print(f"Score: {score:.2f}")
                print(f"Score moyen: {avg_score:.2f}")
                print(f"Meilleur score moyen: {best_avg_score:.2f}")
                print(f"Epsilon: {agent.epsilon:.2f}")
                print(f"Loss: {np.mean(episode_losses) if episode_losses else 0:.4f}")
                print("-" * 50)
            
            # Sauvegarde du modèle
            if episode % save_interval == 0:
                model_path = os.path.join(model_dir, f"model_episode_{episode}.pth")
                agent.save(model_path)
                
                # Si c'est le meilleur modèle, on le sauvegarde séparément
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    agent.save(os.path.join(model_dir, "best_model.pth"))
                    print(f"\n>>> Nouveau meilleur score moyen: {best_avg_score:.2f} !")
                    
                # Sauvegarde des stats
                stats_path = os.path.join(stats_dir, "training_stats.json")
                with open(stats_path, 'w') as f:
                    json.dump(training_stats, f, indent=2)
                    
                # Plot des progrès
                plot_training_progress(scores, avg_scores)
                
    except KeyboardInterrupt:
        print("\n\nEntraînement interrompu par l'utilisateur!")
        # Sauvegarde de sécurité
        print("Sauvegarde de l'état actuel...")
        agent.save(os.path.join(model_dir, "interrupted_model.pth"))
        if avg_score > best_avg_score:
            agent.save(os.path.join(model_dir, "best_model.pth"))
        with open(os.path.join(stats_dir, "training_stats.json"), 'w') as f:
            json.dump(training_stats, f, indent=2)
        plot_training_progress(scores, avg_scores)
    
    # Stats finales
    training_time = time.time() - start_time
    print("\nStats finales:")
    print(f"Durée totale: {training_time/3600:.2f} heures")
    print(f"Épisodes joués: {episode}")
    print(f"Meilleur score moyen: {best_avg_score:.2f}")

if __name__ == "__main__":
    # Entraînement continu
    train(save_interval=50, load_model=True, model_dir="models", stats_dir="training_stats")