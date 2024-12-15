import pygame
import pygame.mixer
import sys
import random
import time
from unit import *
from abilities import *

LEVEL = 3 #doit etre > 1 ordre de grandeur des facultés débloquées : 1-3, mettre > 3 fera réfléchir l'IA plus longtemps encore tho
DBASE = 30 #degats bruts de base pour tout le monde avant tout calcul (à ajuster avec la santé des persos pour que le jeu soit équilibré)

class Game: # Classe pour représenter le jeu
    def __init__(self, screen, player_units, enemy_units):
        self.screen = screen # Écran sur lequel le jeu sera affiché
        self.player_units = player_units # Liste des unités contrôlées par le joueur
        self.enemy_units = enemy_units # Liste des unités contrôlées par l'IA
        self.messages = [] # Liste des messages à afficher dans l'interface (actions, compétences, etc.)
        # Initialisation des compétences (chacune étant une instance de classe)
        self.competences = [Poison(), PluieDeProjectiles(), Missile(), Drain(), Soin(), Bouclier(), Paralysie(), Desarmement(), Vortex(), Teleportation()]
        self.competences_utilisees = set() # Suivi des compétences utilisées (utilisation d'un set, car plus rapide pour la recherche d'éléments)
        self.interface = Interface(self.screen, self) # Instance de la classe Interface pour les interactions

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def flip_display(self): # Mise à jour de l'affichage en utilisant l'interface graphique
        self.screen.blit(self.interface.background, (0, 0)) # Arrière-plan

        for unit in self.player_units + self.enemy_units: # Unités (alliées et ennemies)
            unit.draw_unit(self.screen)

        self.interface.draw_foreground() # Objets au premier plan (arbre, sapin, tente, etc.)
        self.screen.blit(self.interface.foreground_surface, (0, 0))
        self.interface.draw_grid() # Grille semi-transparente (pour délimiter les cellules)
        self.screen.blit(self.interface.grid_surface, (0, 0))
        
        selected_unit = next((unit for unit in self.player_units + self.enemy_units if unit.is_selected), None)
        image_path = selected_unit.image_path if selected_unit else None

        # Affichage de l'interface pour l'unité sélectionnée:
        self.interface.afficher_interface([], self.messages, image_path)
        pygame.display.flip() # Mise à jour de l'écran    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:
            has_acted = False # Indique si l'utilisateur a agi pendant ce tour
            selected_unit.is_selected = True # Indique si l'utilisateur est sélectionnée
            # Gestion des effets actifs sur l'unité
            for effet in selected_unit.effects[:]:
                effet["duree"] -= 1
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{selected_unit.perso.nom} n'est plus affectée par {effet['effet']}.")
                    selected_unit.effects.remove(effet)

            # Étape 1 : Déplacement de l'unité
            max_deplacements = selected_unit.nombre_deplacements # Déplacements totaux de l'unité (calculés en fonction de sa vitesse)
            self.interface.ajouter_message(f"À toi de jouer, {selected_unit.perso.nom} ! Déplacements totaux : {max_deplacements}")
            terminated_early = False # Variable pour savoir si les déplacements ont été terminés de manière précoce
            while max_deplacements > 0: # Tant que l'unité n'a pas fini de se déplacer
                self.flip_display() # Mise à jour de l'affichage
                for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0 # Initialisation des décalages dx et dy à 0
                        if event.key == pygame.K_LEFT:
                            dx = -1 # Déplacement d'une case vers la gauche (colonne précédente)
                        elif event.key == pygame.K_RIGHT:
                            dx = 1 # Déplacement d'une case vers la droite (colonne suivante)
                        elif event.key == pygame.K_UP:
                            dy = -1 # Déplacement d'une case vers le haut (ligne précédente)
                        elif event.key == pygame.K_DOWN:
                            dy = 1 # Déplacement d'une case vers le bas (ligne suivante)
                        elif event.key == pygame.K_SPACE:
                            terminated_early = True
                            max_deplacements = 0 # Fin du compte à rebours des déplacements
                            break

                        if dx != 0 or dy != 0: # Dans le cas où un déplacement est demandé
                            new_colonne = selected_unit.x + dx # Calcul de la nouvelle colonne après que le déplacement ait été effectué
                            new_ligne = selected_unit.y + dy # Calcul de la nouvelle ligne après que le déplacement ait été effectué
                            # On s'assure de rester dans les limites de la grille et d'accéder à une case dite "passable"
                            if 0 <= new_ligne < GRID_SIZE and 0 <= new_colonne < GRID_SIZE and self.interface.passable(new_ligne, new_colonne):
                                moved = selected_unit.move(dx, dy, self.player_units, self.enemy_units) # Déplacement de l'unité
                                if moved == 0: # Dans le cas où l'unité a bougé
                                    max_deplacements -= 1 # Réduction du nombre de déplacements restants
                                self.interface.ajouter_message(f"Déplacements restants : {max_deplacements}")
                            else:
                                self.interface.ajouter_message("Zone bloquée. Prenez une autre direction.")
                        break

            # Étape 2 : Transition vers le choix attaque/compétence
            if max_deplacements == 0: # Dans le cas où l'utilisateur a épuisé tous ses déplacements
                if terminated_early == True: # Si l'utilisateur choisit d'attaquer avant d'avoir épuisé tous ses déplacements
                    selected_unit.effectuer_attaque_directe(self, self.interface, self.screen, self.enemy_units)
                    has_acted = True # Indique que l'utilisateur a agi
                else:
                    self.interface.ajouter_message("Souhaitez-vous attaquer directement (touche espace) ou utiliser une compétence (touche c) ?")
                self.flip_display() # Mise à jour de l'affichage

            # Étape 3 : Choix entre attaque directe ou compétence
            while not has_acted: # Tant que l'utilisateur n'a pas agi
                self.flip_display() # Mise à jour de l'affichage
                for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN: # Dans le cas où une touche du clavier a été enfoncée
                        if event.key == pygame.K_SPACE: # S'il s'agit de la touche "Espace" (choix de l'attaque directe)
                            selected_unit.effectuer_attaque_directe(self, self.interface, self.screen, self.enemy_units)
                            has_acted = True # Indique que l'utilisateur a agi

                        # Gestion de la sélection d'une compétence
                        elif event.key == pygame.K_c: # S'il s'agit de la touche "C" (choix d'une compétence)
                            competence_choisie = Competence.selectionner_competence(self, selected_unit)
                            if competence_choisie: # Dans le cas où une compétence a été choisie
                                cible = Competence.selectionner_cible(selected_unit, self, competence_choisie) # Choix d'une cible
                                if cible: # Dans le cas où une cible a été choisie 
                                    competence_choisie.utiliser(selected_unit, cible, self, self.interface)
                                    selected_unit.competences_utilisees.add(competence_choisie.nom) # Ajout de la compétence à l'ensemble des compétences déjà utilisées par l'unité
                            has_acted = True # Indique que l'utilisateur a agi
                selected_unit.is_selected = False # Désélection de l'unité active

                # Nettoyage des unités mortes:
                self.player_units = [unit for unit in self.player_units if unit.health > 0]
                self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0]

                # Vérification des conditions de victoire/défaite:
                if not self.player_units: # S'il ne reste plus d'unités alliées vivantes
                    self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
                    self.flip_display() # Mise à jour l'affichage
                    pygame.event.clear() # Pour ne pas laisser la boucle d'événements tourner pendant le temps de lecture
                    time.sleep(60) # Temps laissé à l'utilisateur pour lire le message
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                elif not self.enemy_units: # S'il ne reste plus d'unités ennemies vivantes
                    self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
                    self.flip_display() # Mise à jour l'affichage
                    pygame.event.clear() # Pour ne pas laisser la boucle d'événements tourner pendant le temps de lecture
                    time.sleep(60) # Temps laissé à l'utilisateur pour lire le message
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def handle_enemy_turn(self):
        """IA pour les ennemis."""
        for enemy in self.enemy_units:
            for effet in enemy.effects[:]:
                if effet["effet"] == "poison":
                    enemy.minusHP(effet["dommages"]) # Applique les dégâts du poison
                    self.interface.ajouter_message(f"{enemy.perso.nom} subit {effet['dommages']} points de dégâts à cause du poison.")
                    effet["duree"] -= 1 # Réduit la durée de l'effet
                    if effet["duree"] <= 0:
                        self.interface.ajouter_message(f"{enemy.perso.nom} n'est plus affecté par {effet['effet']}.")
                        enemy.effects.remove(effet) # Supprime l'effet expiré
                elif effet["effet"] == "désarmé":
                    if effet["duree"] == 0:
                        self.interface.ajouter_message(f"{enemy.perso.nom} n'est plus affecté par {effet['effet']}.")
                else:
                    effet["duree"] -= 1 # Réduit la durée de l'effet
                    if effet["duree"] <= 0:
                        self.interface.ajouter_message(f"{enemy.perso.nom} n'est plus affecté par {effet['effet']}.")
                        enemy.effects.remove(effet) # Supprime l'effet expiré

            self.enemy_units = [e for e in self.enemy_units if e.health > 0] # Nettoyage immédiat après effet
            if any(effet["effet"] == "immobilisé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.perso.nom} est paralysé(e) durant ce tour.")
                self.handle_enemy_attack(enemy)
                continue # Passe au prochain ennemi

            cibles_possibles = [unit for unit in self.player_units if unit.health > 0]
            if not cibles_possibles:
                continue
            
            if len(self.enemy_units) != 0 and len(self.player_units) != 0:
            # Déplacement aléatoire différencié selon le niveau de l'IA (normalement, l'intelligence de l'ia augmente de façon exponnentielle jusqu'à probablement atteindre un plafond, il faudrait étudier la fonction)
                target = random.choice(cibles_possibles)
                for _ in range(LEVEL): #plus le niveau de l'IA sera grand, plus il aura le temps de réfléchir
                    if LEVEL > 1:
                        if target.comparateur_faiblesse_resistance(enemy)[1]: #si target a une résistance, il cherche encore
                           target = random.choice(cibles_possibles)
                    if LEVEL > 2: #si niveau superieur à 2
                        if not target.comparateur_faiblesse_resistance(enemy)[0]: #si target n'a pas de faiblesse, il cherche encore
                            target = random.choice(cibles_possibles)
                    #niveau sup où il garde en mémoire un target pour toute la partie, cette fois en estimant le meilleur enemy dans la liste des joueurs?
                    #ou alors algo d'optimisation. Minimisation entre le chemin le plus court vers l'ennemi et rester hors de portée d'une attaque directe si enemy ne peut pas attaquer dans le meme tour 
                    #ou alors algo pour prendre en compte la proba de se faire tuer par un target spécifique au prochain tour, enemy fuit l'adversaire si c'est le cas
                    #vu qu'on a déjà un projet en optimisation, on ne va pas creuser plus loin :)
                    #par ailleurs toutes les fonctions qui ont été créées (je pense notamment pour le calcul des dégats, pourraient être étudiés graphiquement avec matplotlib, j'essairai de plot au moins 1 si j'ai le temps ( pour certains, ça ferait une fonction 2 entrées 1 sortie, avec des isovaleurs représentables; par exemple Unit().ponderation))
                    #on pourrait alors ajuster les valeurs de stats d'attaque et de défense plus précisément en connaissant la forme de Unit().pondération 
                
                enemy.current_move = 0
                essai = 0 #essai = 0 si le move est successful, si le move rate :  essai = 1. 0 et 1 sont aussi des bools  reconnus
                print(target)
                while enemy.current_move < enemy.nombre_deplacements:
                    self.flip_display()
                    if essai : #tentatives suivante si le essai de else n'a pas fonctionné
                        for combattant in self.player_units:
                            oui = abs(enemy.x - combattant.x) <= 1 and abs(enemy.y - combattant.y) <= 1
                            if oui: # un joueur à portée
                                target = combattant #il devient le nouveau cible
                                break # sors de la recherche de combattant
                        if oui:
                            print('essai 2')
                            break #si l'ennemi est à portée, plus besoin de se déplacer
                        else:
                            for _ in range(LEVEL):
                                dx, dy =0, 0
                                #while abs(dx+ dy)!=1:
                                dx = random.randint(-1, 1)
                                dy = random.randint(-1, 1)
                                new_col = enemy.x + dx
                                new_row = enemy.y + dy
                                if dx !=0 and dy!=0:
                                    if random.randint(0, 1) == 0:
                                        dx = 0
                                    else:
                                        dy = 0
                                            
                                    # On s'assure que la case est passable avant de permettre le déplacement
                                if self.interface.passable(new_row, new_col):
                                    print('essai 3', new_row, new_col)
                                    essai = enemy.move(dx, dy, self.enemy_units, self.player_units) #mouvement aléatoire pour essayer de se débloquer
                                    time.sleep(0.3)
                                else:    
                                    essai = 1
                                self.flip_display()
                            if essai :
                                print('essai 4', new_row, new_col)
                                break #si rien ne marche on ne bloque pas la partie
                
                    else:   # l'algo appliquera ce else en premier      
                        for _ in range(LEVEL*2):
                            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
                            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
                            if dx !=0 and dy!=0:
                                if random.randint(0, 1) == 0:
                                    dx = 0
                                else:
                                    dy = 0
                            print(dx, dy)
                            
                            #print(dx, dy)
                            #for j in range(LEVEL):
                                # On s'assure que la case est passable avant de permettre le déplacement
                            new_col = enemy.x + dx
                            new_row = enemy.y + dy
                            if self.interface.passable(new_row, new_col,):
                                print('essai 1',dx, dy)
                                essai = enemy.move(dx, dy, self.enemy_units, self.player_units)
                                time.sleep(0.3)
                                if essai ==0:
                                    break
                            essai = 1
                            #time.sleep(0.3)
                                #break
                
                        #print(enemy.current_move)
                
                    
                enemy.current_move = 0
            self.interface.ajouter_message(f"{enemy.perso.nom} s'est déplacé en ({enemy.x}, {enemy.y}).")

            # Gestion des attaques:
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                if any(effet["effet"] == "désarmé" for effet in enemy.effects): # Dans le cas où l'ennemi est désarmé
                    self.interface.ajouter_message(f"{enemy.perso.nom} est désarmé.")
                elif any(effet["effet"] == "bouclier" for effet in target.effects): # Dans le cas où la cible est protégé par un bouclier
                    self.interface.ajouter_message(f"{enemy.perso.nom} tente d'attaquer {target.perso.nom}.")
                    self.interface.ajouter_message(f"{target.perso.nom} est protégé(e) par un bouclier ! Aucun dégât subi.")
                else:
                    enemy.attack_critique_esquive(self, target, DBASE)          
                    if target.health <= 0:
                        self.player_units = [unit for unit in self.player_units if unit.health > 0] # Suppression immédiate de l'unité morte
            
            for effet in enemy.effects[:]:
                if effet["effet"] == "désarmé":
                    effet["duree"] -= 1 # Réduit la durée de l'effet
                    if effet["duree"] <= 0:
                        self.interface.ajouter_message(f"{enemy.perso.nom} n'est plus affecté par {effet['effet']}.")
                        enemy.effects.remove(effet) # Supprime l'effet expiré
        # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
            self.flip_display() # Mise à jour l'affichage
            pygame.event.clear() # Pour ne pas laisser la boucle d'événements tourner pendant le temps de lecture
            time.sleep(60) # Temps laissé à l'utilisateur pour lire le message
            pygame.quit() # Fermeture de Pygame proprement
            sys.exit() # Arrêt complet du programme

        elif not self.enemy_units: # Si la liste des unités ennemies (enemy_units) est vide
            self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
            self.flip_display() # Mise à jour l'affichage
            pygame.event.clear() # Pour ne pas laisser la boucle d'événements tourner pendant le temps de lecture
            time.sleep(60) # Temps laissé à l'utilisateur pour lire le message
            pygame.quit() # Fermeture de Pygame proprement
            sys.exit() # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)
    
    def curseur(self, selected_unit):
        pygame.draw.rect(self.screen, RED, (selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            

    def handle_enemy_attack(self, enemy):
        # Identification des cibles adjacentes
        cibles_possibles = [unit for unit in self.player_units if abs(enemy.x - unit.x) <= 1 and abs(enemy.y - unit.y) <= 1 and unit.health > 0]
        if cibles_possibles:
            target = random.choice(cibles_possibles) # Choix d'une cible aléatoire
            if any(effet["effet"] == "désarmé" for effet in enemy.effects): # Si l'ennemi est désarmé
                self.interface.ajouter_message(f"{enemy.perso.nom} est désarmé et ne peut pas attaquer ce tour.")
            elif any(effet["effet"] == "bouclier" for effet in target.effects): # Si la cible a un bouclier
                self.interface.ajouter_message(f"{enemy.perso.nom} tente d'attaquer {target.perso.nom}.")
                self.interface.ajouter_message(f"{target.perso.nom} est protégé(e) par un bouclier ! Aucun dégât subi.")
            else:
                enemy.attack_critique_esquive(self, target, DBASE)
                if target.health <= 0:
                    self.player_units = [unit for unit in self.player_units if unit.health > 0] # Suppression de l'unité morte

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

fighter_mario = Terrien(perso=Mario, x=-1, y=-1, health=120, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=30, competences=[Poison(), Drain(), Bouclier(), Vortex()], image_path = ".\\assets\\mario_stat.png")
fighter_luigi = Aerien(perso=Luigi, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=70, competences=[Poison(), Missile(), Bouclier(), Teleportation()], image_path = ".\\assets\\luigi_stat.png")
fighter_peach = Terrien(perso=Peach, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=40, competences=[PluieDeProjectiles(), Desarmement(), Bouclier(), Teleportation()], image_path = ".\\assets\\peach_stat.png")
fighter_toad = Terrien(perso=Toad, x=-1, y=-1, health=120, team='undefined', attack_power=8, defense_power=6, agility_power=3, speed=50, competences=[PluieDeProjectiles(), Soin(), Paralysie(), Vortex()], image_path = ".\\assets\\toad_stat.png")

fighter_sonic = Aerien(perso=Sonic, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=5, speed=80, competences=[PluieDeProjectiles(), Paralysie(), Bouclier(), Vortex()], image_path = ".\\assets\\sonic_stat.png")
fighter_mickey = Archer(perso=Mickey, x=-1, y=-1, health=90, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=75, competences=[Poison(), Drain(), Soin(), Teleportation()], image_path = ".\\assets\\mickey_stat.png")
fighter_minion = Aerien(perso=Minion, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=4, speed=60, competences=[Poison(), Missile(), Soin(), Vortex()], image_path = ".\\assets\\minion_stat.png")

fighter_pikachu = Terrien(perso=Pikachu, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50, competences=[Poison(), Missile(), Drain(), Vortex()], image_path = ".\\assets\\pikachu_stat.png")
fighter_clochette = Terrien(perso=Clochette, x=-1, y=-1, health=100, team='undefined', attack_power=6, defense_power=4, agility_power=2, speed=40, competences=[PluieDeProjectiles(), Paralysie(), Soin(), Teleportation()], image_path = ".\\assets\\clochette_stat.png")
fighter_alice = Archer(perso=Alice, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=4, speed=60, competences=[PluieDeProjectiles(), Drain(), Bouclier(), Teleportation()], image_path = ".\\assets\\alice_stat.png")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

def main():
    # Initialisation des joueurs disponibles (ceux qui n'ont pas été sélectionnés):
    liste_combattants = Unit.get_instances()
    player_units = []
    enemy_units = []
    
    # Position initiale des joueurs:
    startposP = [(2, 5), (3, 5), (2, 6), (3, 6)]
    startposE = [(18, 6), (6, 19), (13, 15), (19, 13)]
    random.shuffle(startposP)
    random.shuffle(startposE)

    # Ajout des combattants
    while len(player_units) < 4 or len(enemy_units) < 4:
        if len(player_units) < 4:
            combattant = random.choice(liste_combattants)
            liste_combattants.remove(combattant)
            combattant.team = 'player'
            x, y = startposP.pop(0)
            combattant.x, combattant.y = x, y
            player_units.append(combattant)
        elif len(enemy_units) < 4:
            combattant = random.choice(liste_combattants)
            liste_combattants.remove(combattant)
            combattant.team = 'enemy'
            x, y = startposE.pop(0)
            combattant.x, combattant.y = x, y
            enemy_units.append(combattant)

    # Affichage des équipes
    print("\nÉquipe d'alliés :", [c.perso.nom for c in player_units])
    print("\nÉquipe d'ennemis :", [c.perso.nom for c in enemy_units])

    time.sleep(1)
    # Initialisation de Pygame
    pygame.init()
    # Initialisation du module mixer de Pygame, nécessaire pour gérer les fonctionnalités audio
    pygame.mixer.init()
    # Chargement de la musique de fond
    pygame.mixer.music.load("./assets/musique.mp3")
    pygame.mixer.music.set_volume(0.5) # Volume (0.0 à 1.0)
    pygame.mixer.music.play(-1) # -1 pour jouer la musique en boucle
    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")
    # Instanciation du jeu
    game = Game(screen, player_units, enemy_units)
    # Boucle principale du jeu
    while True:
        for event in pygame.event.get(): # Gestion des évènements
            if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                pygame.quit() # Fermeture de Pygame proprement
                exit() # Arrêt complet du programme

        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()