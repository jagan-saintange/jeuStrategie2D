import pygame
import random
import sys
from abilities import *
from personnages import *

startposP1 = [(2,5), (3,5), (2,6), (3,6)]
startposE = [(17,5), (18,5), (17,6), (18,6)]
random.shuffle(startposP1)
random.shuffle(startposE)

class Ui:
        
    def __init__(self):
        self.liste_combattants = Unit.get_instances()
        #print('\n', self.liste_combattants)
        self.player1_units = []
        self.enemy_units = [] #laissons-les publiques
        
        
    def ajout(self, team, i):
        if not (i in self.player1_units or i in self.enemy_units):
            if team == 'player1':
                i.team = 'player1'
                x, y = startposP1.pop(0)
                i.x = x
                i.y = y
                self.player1_units.append(i)
            elif team == 'enemy':
                i.team = 'enemy'
                x, y = startposE.pop(0)
                i.x = x
                i.y = y
                self.enemy_units.append(i)
            else:
                raise TypeError('probleme ajout de combattants')
    
    def selector(self, team, discriminant, nom=None):
        
        if discriminant == 'hasard':
            i = random.choice(self.liste_combattants)
            #print(i)
            self.ajout(team, i)
                
        elif discriminant == 'personnage':
            for i in self.liste_combattants:
                #print(i.perso.nom, nom)
                if i.perso.nom == nom:
                    #print('BIP')
                    self.ajout(team, i)

    
        elif discriminant == 'univers':
            for i in self.liste_combattants:
                if i.perso.univers == nom :
                    i.perso.team = team 
                    self.ajout(team, i)
                
        else:
            raise TypeError("Sélection impossible, erreur input")
        
        return self.player1_units, self.enemy_units
    

    def show_teams(self):
        show1=[_.perso.nom for _ in self.player1_units]
        show2=[_.perso.nom for _ in self.enemy_units]
        print(f"\nl'equipe du joueur 1 est composé de {show1}")
        print(f"l'equipe de enemy est composé de {show2}")
    
    
    
    def run_ui(self):
        """Run the command-line interface for selecting fighters."""
        equipe = 'player1'
        print(self.liste_combattants)
        continuer = (len(self.player1_units)  < 4) or (len(self.enemy_units) < 4)
        while continuer:
            
            
            print("\n\n===============\nMenu:")
            print("1. Sélection par personnage")
            print("2. Sélection par univers")
            print("3. Sélection au hasard")
            print("4. Afficher les équipes")
            print("5. Fin")
            
            
            if len(self.player1_units) < 4:
                equipe = 'player1'
                print("\n===================\nc'est à player1 de choisir")    
                
            elif len(self.enemy_units) < 4 :
                equipe = 'enemy'
                print("\n==================\nc'est à l'adversaire de choisir")    
                
            
            choice = input("\nEntrez l'option souhaitée (1-5): ")
            
                
            if choice == '1':
                
                while len(self.player1_units) <4 and len(self.enemy_units)<4:
                    print("Combattants dispo:")
                    for i, fighter in enumerate(self.liste_combattants):
                        #if fighter.team == 'undefined':  # Only show unselected fighters
                        print(f"{i + 1}: {fighter.perso.nom} Team: {fighter.team})")
                        
                    fighter_choice = input("Entrez le numéro du combattant choisi: ")
                    j = int(fighter_choice) - 1
                    if 0 <= j < len(self.liste_combattants):
                        print('BIP')
                        selected_fighter = self.liste_combattants[j]
                        print('\n',selected_fighter.perso.nom)
                        if selected_fighter.team =='undefined':
                            self.selector(equipe, 'personnage', selected_fighter.perso.nom)
                        else:
                            print("LE COMBATTANT EST DEJA SELECTIONÉ ! ")
                        self.show_teams()
                    else:
                        print("NOMBRE INVALIDE")
    
            elif choice == '2':
                universe_name = input("Entrez le nom de l'univers des persos à sélectionner': ")
                self.selector(equipe, 'univers', universe_name)
                self.show_teams()
                equipe = 'enemy'
                
            elif choice == '3':
                while len(self.player1_units) <4 or len(self.enemy_units)<4:

                    if len(self.player1_units) < 4:
                        self.selector('player1', 'hasard')
                    elif len(self.enemy_units) < 4:
                        equipe = 'enemy'    
                        self.selector('enemy', 'hasard')
                self.show_teams()
                print('BEEP')
            
            elif choice == '4':
                self.show_teams()
                
            elif choice == '5':
                print("Fin")
                pygame.quit()
                sys.exit()
                break #mettre un print lancement du jeu en sortie
            else:
                print("Invalid choice. Please try again.")
            print('BEEP')
            continuer = (len(self.player1_units) < 4) or (len(self.enemy_units) < 4)
        
        print('choix validé, la partie va commencer. Les équipes sont les suivantes')
        self.show_teams()
        print('Bon fight !')
        return self.player1_units, self.enemy_units

fighter_mario = Terrien(perso=Mario, x=-1, y=-1, health=120, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=30, competences=[Poison(), Drain(), Bouclier(), Vortex()], image_path = ".\\assets\\mario_stat.png") # MARIO
fighter_luigi = Aerien(perso=Luigi, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=70, competences=[Poison(), Missile(), Bouclier(), Teleportation()], image_path = ".\\assets\\luigi_stat.png") # Luigi
fighter_peach = Terrien(perso=Peach, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=40, competences=[PluieDeProjectiles(), Desarmement(), Bouclier(), Teleportation()], image_path = ".\\assets\\peach_stat.png") # PEACH
fighter_toad = Terrien(perso=Toad, x=-1, y=-1, health=120, team='undefined', attack_power=8, defense_power=6, agility_power=3, speed=50, competences=[PluieDeProjectiles(), Soin(), Paralysie(), Vortex()], image_path = ".\\assets\\toad_stat.png") # TOAD

fighter_sonic = Aerien(perso=Sonic, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=5, speed=80, competences=[PluieDeProjectiles(), Paralysie(), Bouclier(), Vortex()], image_path = ".\\assets\\sonic_stat.png") # SONIC


fighter_mickey = Archer(perso=Mickey, x=-1, y=-1, health=90, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=75, competences=[Poison(), Drain(), Soin(), Teleportation()], image_path = ".\\assets\\mickey_stat.png") # MICKEY
fighter_minion = Aerien(perso=Minion, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=4, speed=60, competences=[Poison(), Missile(), Soin(), Vortex()], image_path = ".\\assets\\minion_stat.png") # MINION

fighter_pikachu = Terrien(perso=Pikachu, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50, competences=[Poison(), Missile(), Drain(), Vortex()], image_path = ".\\assets\\pikachu_stat.png") # PIKACHU

fighter_clochette = Terrien(perso=Clochette, x=-1, y=-1, health=100, team='undefined', attack_power=6, defense_power=4, agility_power=2, speed=40, competences=[PluieDeProjectiles(), Paralysie(), Soin(), Teleportation()], image_path = ".\\assets\\clochette_stat.png") # CLOCHETTE
fighter_alice = Archer(perso=Alice, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=4, speed=60, competences=[PluieDeProjectiles(), Drain(), Bouclier(), Teleportation()], image_path = ".\\assets\\alice_stat.png") # ALICE