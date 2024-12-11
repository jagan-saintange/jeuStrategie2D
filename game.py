import pygame
import random
import sys
import time
from ui import *
from abilities import *

LEVEL = 3 #doit etre > 1 ordre de grandeur des facultés débloquées : 1-3, mettre > 3 fera réfléchir l'IA plus longtemps encore tho
DBASE = 30 #degats bruts de base pour tout le monde avant tout calcul (à ajuster avec la santé des persos pour que le jeu soit équilibré)

#############¶

class Game: # Classe pour représenter le jeu
    def __init__(self, screen, player_units, enemy_units):
        self.screen = screen
        self.interface = Interface(self.screen, self)
        self.player_units = player_units
        self.enemy_units = enemy_units
        random.shuffle(startposP1)
        random.shuffle(startposE)

        self.player_row = 5
        self.player_col = 5
        self.messages = []
        
        # Initialisation des compétences
        self.competences = [Poison(),
                            PluieDeProjectiles(),
                            Missile(),
                            Drain(),
                            Soin(),
                            Bouclier(),
                            Paralysie(),
                            Desarmement(), 
                            Vortex(),   
                            Teleportation()]
        
        # Attribution de chaque compétence à une touche du clavier (A, Z, E, R, T, Y, U, I, O, P)
        self.touches_competences = {"Poison": pygame.K_a,
                                    "Pluie de projectiles": pygame.K_z,
                                    "Missile": pygame.K_e,
                                    "Drain": pygame.K_r,
                                    "Soin": pygame.K_t,
                                    "Bouclier": pygame.K_y,
                                    "Paralysie": pygame.K_u,
                                    "Désarmement": pygame.K_i,
                                    "Vortex": pygame.K_o,
                                    "Téléportation": pygame.K_p}

        self.competences_utilisees = set() # Suivi des compétences utilisées

    def flip_display(self, selected_unit=None): # Mise à jour de l'affichage en utilisant l'interface graphique
        self.screen.blit(self.interface.background, (0, 0)) # Arrière-plan

        for unit in self.player_units + self.enemy_units: # Unités (alliées et ennemies)
            unit.draw_unit(self.screen)
        
        if selected_unit != None:            
            self.curseur(selected_unit)

        self.interface.draw_foreground() # Objets au premier plan (arbre, sapin, tente, etc.)
        self.screen.blit(self.interface.foreground_surface, (0, 0))
        self.interface.draw_grid() # Grille semi-transparente (pour délimiter les cellules)
        self.screen.blit(self.interface.grid_surface, (0, 0))

        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_interface(competences_disponibles, self.touches_competences, self.messages)
        pygame.display.flip() # Mise à jour de l'écran    
        
        

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:
            has_acted = False  # Indicateur pour savoir si l'unité a agi ou non pendant ce tour

            # Gestion des effets actifs sur l'unité
            for effet in selected_unit.effects[:]:
                if effet["effet"] == "poison":
                    #selected_unit.attack(dommage=effet["dommages"])
                    selected_unit.minusHP(dommage = effet["dommages"])
                effet["duree"] -= 1
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{selected_unit.perso.nom} n'est plus affectée par {effet['effet']}.")
                    selected_unit.effects.remove(effet)

            selected_unit.is_selected = True
            self.flip_display(selected_unit)

            # Étape 1 : Déplacement de l'unité
            max_deplacements = selected_unit.nombre_deplacements
            self.interface.ajouter_message(f"À toi de jouer, {selected_unit.perso.nom} ! Déplacements totaux : {max_deplacements}")
            while not has_acted:
    
                    # Important: cette boucle permet de gérer les événements Pygame
                    for event in pygame.event.get():
    
                        # Gestion de la fermeture de la fenêtre
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        
                        
                        
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:  # Vérifier si la touche Échap est pressée
                                pygame.quit()
                                sys.exit()
                        
                        """
                        # Gestion des touches du clavier
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_TAB:
                                game.toggle_inspect(selected_unit)
                                self.flip_display()
                        """
                        # Gestion des touches du clavier
                        if event.type == pygame.KEYDOWN:
    
                            # Déplacement (touches fléchées)
                            dx, dy = 0, 0
                            if event.key == pygame.K_LEFT:
                                dx = -1
                            elif event.key == pygame.K_RIGHT:
                                dx = 1
                            elif event.key == pygame.K_UP:
                                dy = -1
                            elif event.key == pygame.K_DOWN:
                                dy = 1
                    
                        
                            
                            
                            if dx != 0 or dy != 0:
                                selected_unit.move(dx, dy, self.player_units, self.enemy_units)
                                print(f'il vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité')
                                
                                self.flip_display(selected_unit)
    
                            # Attaque (touche espace) met fin au tour
                            if event.key == pygame.K_SPACE:
                                selected_unit.current_move = 0
                                self.interface.ajouter_message("Souhaitez-vous attaquer directement (touche espace) ou utiliser une compétence (touche c) ?")
                                self.flip_display(selected_unit)
                                # Étape 3 : Choix entre attaque directe ou compétence
                                while not has_acted:
                                    self.flip_display(selected_unit)
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        if event.type == pygame.KEYDOWN:
                                            # Gestion de l'attaque directe
                                            if event.key == pygame.K_SPACE:
                                                self.interface.ajouter_message("Vous avez choisi d'attaquer directement. Veuillez sélectionner une cible.")
                                                self.flip_display(selected_unit)

                                                # Sélection de la cible
                                                cible_x, cible_y = selected_unit.x, selected_unit.y
                                                selecting_target = True
                                                while selecting_target:
                                                    self.flip_display(selected_unit)
                                                    rect = pygame.Rect(cible_x * CELL_SIZE, cible_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                                                    pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
                                                    pygame.display.update()

                                                    for target_event in pygame.event.get():
                                                        if target_event.type == pygame.QUIT:
                                                            pygame.quit()
                                                            sys.exit()
                                                        if target_event.type == pygame.KEYDOWN:
                                                            if target_event.key == pygame.K_LEFT:
                                                                cible_x = max(0, cible_x - 1)
                                                            elif target_event.key == pygame.K_RIGHT:
                                                                cible_x = min(GRID_SIZE - 1, cible_x + 1)
                                                            elif target_event.key == pygame.K_UP:
                                                                cible_y = max(0, cible_y - 1)
                                                            elif target_event.key == pygame.K_DOWN:
                                                                cible_y = min(GRID_SIZE - 1, cible_y + 1)
                                                            elif target_event.key == pygame.K_RETURN:
                                                                selecting_target = False

                                                # Vérification de la cible
                                                cible = next((enemy for enemy in self.enemy_units if enemy.x == cible_x and enemy.y == cible_y), None)
                                                if cible and abs(selected_unit.x - cible_x) + abs(selected_unit.y - cible_y) == 1:
                                                    #selected_unit.attack_critique_esquive(cible, dommages, interface)
                                                    selected_unit.attack(cible, DBASE)
                                                    #self.interface.ajouter_message(f"{selected_unit.perso.nom} attaque {cible.perso.nom} (-{DBASE} PdV).")
                                                    if cible.health <= 0:
                                                        self.enemy_units.remove(cible)
                                                    has_acted = True
                                                else:
                                                    self.interface.ajouter_message("La cible n'est pas à votre portée.")
                                                    has_acted = True
                                            # Gestion de la sélection d'une compétence
                                            elif event.key == pygame.K_c:
                                                competence = Competence.selectionner_competence(self.interface, self.screen, self.competences, self.touches_competences, self.competences_utilisees)
                                                if competence:
                                                    cible = Competence.selectionner_cible(selected_unit, self, competence)
                                                    if cible:
                                                        Competence.utiliser_competence(selected_unit, cible, competence, self, self.interface)
                                                        self.competences_utilisees.add(competence.nom)
                                                        if len(self.competences_utilisees) == len(self.competences):
                                                            self.interface.ajouter_message("Toutes les compétences ont été utilisées. Recharge des compétences...")
                                                            self.competences_utilisees.clear()
                                                    has_acted = True

                                selected_unit.is_selected = False

                                # Nettoyage des unités mortes
                                self.player_units = [unit for unit in self.player_units if unit.health > 0]
                                self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0]

                                # Vérification des conditions de victoire/défaite
                                if not self.player_units:
                                    self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
                                    pygame.quit()
                                    sys.exit()
                                elif not self.enemy_units:
                                    self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
                                    pygame.quit()
                                    sys.exit()



    def handle_enemy_turn(self):
        """IA pour les ennemis."""
        for enemy in self.enemy_units:
            for effet in enemy.effects[:]:
                if effet["effet"] == "poison":
                    #enemy.attack(dommage = effet["dommages"]) # Applique les dégâts du poison
                    enemy.minusHP(dommage = effet["dommages"])
                effet["duree"] -= 1 # Réduit la durée de l'effet
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) n'est plus affectée par {effet['effet']}.")
                    enemy.effects.remove(effet) # Supprime l'effet expiré
            # Vérifie si l'ennemi est immobilisé (paralysie)
            if any(effet["effet"] == "immobilisé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est paralysée et ne peut pas agir ce tour.")
                continue # Passe au prochain ennemi
            
            if len(self.enemy_units) != 0 and len(self.player_units) != 0:
            # Déplacement aléatoire différencié selon le niveau de l'IA (normalement, l'intelligence de l'ia augmente de façon exponnentielle jusqu'à probablement atteindre un plafond, il faudrait étudier la fonction)
                target = random.choice(self.player_units)
                for _ in range(LEVEL): #plus le niveau de l'IA sera grand, plus il aura le temps de réfléchir
                    if LEVEL > 1:
                        if target.comparateur_faiblesse_resistance(enemy)[1]: #si target a une résistance, il cherche encore
                           target = random.choice(self.player_units)
                    if LEVEL > 2: #si niveau superieur à 2
                        if not target.comparateur_faiblesse_resistance(enemy)[0]: #si target n'a pas de faiblesse, il cherche encore
                            target = random.choice(self.player_units)
                    #niveau sup où il garde en mémoire un target pour toute la partie, cette fois en estimant le meilleur enemy dans la liste des joueurs?
                    #ou alors algo d'optimisation. Minimisation entre le chemin le plus court vers l'ennemi et rester hors de portée d'une attaque directe si enemy ne peut pas attaquer dans le meme tour 
                    #ou alors algo pour prendre en compte la proba de se faire tuer par un target spécifique au prochain tour, enemy fuit l'adversaire si c'est le cas
                    #vu qu'on a déjà un projet en optimisation, on ne va pas creuser plus loin :)
                    #par ailleurs toutes les fonctions qui ont été créées (je pense notamment pour le calcul des dégats, pourraient être étudiés graphiquement avec matplotlib, j'essairai de plot au moins 1 si j'ai le temps ( pour certains, ça ferait une fonction 2 entrées 1 sortie, avec des isovaleurs représentables; par exemple Unit().ponderation))
                    #on pourrait alors ajuster les valeurs de stats d'attaque et de défense plus précisément en connaissant la forme de Unit().pondération 
                
                enemy.current_move = 0
                essai = 0 #essai = 0 si le move est successful, si le move rate :  essai = 1. 0 et 1 sont aussi des bools  reconnus
                while enemy.current_move < enemy.nombre_deplacements:
                    self.flip_display(enemy)
                    if essai : #tentatives suivante si le essai de else n'a pas fonctionné
                        if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                            break #si l'ennemi est portée, plus besoin de se déplacer
                        else:
                            for _ in range(LEVEL):
                                dx, dy =0, 0
                                while abs(dx+ dy)!=1:
                                    dx = random.randint(-1, 1)
                                    dy = random.randint(-1, 1)
                                essai = enemy.move(dx, dy, self.enemy_units, self.player_units) #mouvement aléatoire pour essayer de se débloquer
                                if essai :
                                    break #si rien ne marche on ne bloque pas la partie
                
                    else:   # l'algo appliquera ce else en premier      
                    
                        #on input l'ess
                        dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
                        dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
                        if abs(dx) - abs(dx) == 0:
                            if abs(enemy.x - target.x) > abs(enemy.y - target.y):
                                dy = 0
                            elif abs(enemy.x - target.x) < abs(enemy.y - target.y):
                                dx = 0
                            else:
                                if random.randint(0, 1) == 0:
                                    dx = 0
                                else:
                                    dy = 0
                        #print(dx, dy)
                        essai = enemy.move(dx, dy, self.enemy_units, self.player_units)
                        self.flip_display(enemy)
                        time.sleep(0.3)
                        #print(enemy.current_move)
                    
                enemy.current_move = 0
            self.interface.ajouter_message(f"L'unité a été déplacée à ({enemy.x}, {enemy.y}).")

            # Vérifie si l'ennemi est désarmé (ne peut pas attaquer)
            if any(effet["effet"] == "désarmé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est désarmée.")
                continue # Passe au prochain ennemi
            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target, DBASE)
                if target.health <= 0:
                    self.player_units.remove(target)
        self.enemy_units = [enemy for enemy in self.enemy_units if enemy.health > 0] # Mise à jour de la liste des ennemis pour exclure ceux qui sont morts
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
            pygame.quit() # Fermeture de Pygame proprement
            sys.exit() # Arrêt complet du programme # On vérifie si le jeu est terminé après que l'unité ait agi
        elif not self.enemy_units: # Si la liste des unités ennemies (enemy_units) est vide
            self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
            pygame.quit() # Fermeture de Pygame proprement
            sys.exit() # Arrêt complet du programme # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)
    
    def curseur(self, selected_unit):
        pygame.draw.rect(self.screen, GREEN, (selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            
            
#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

def main():
    ui = Ui()
    player_units, enemy_units = ui.run_ui()
    print('chargement du jeu...')
    time.sleep(0.2)
    # Initialisation de Pygame
    pygame.init()
    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")
    # Instanciation du jeu
    game = Game(screen, player_units, enemy_units)
    for i in player_units + enemy_units:
        i.interf(game.interface)
    # Boucle principale du jeu
    while True:
        for event in pygame.event.get(): # Gestion des évènements
            if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                pygame.quit() # Fermeture de Pygame proprement
                sys.exit() # Arrêt complet du programme

        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()