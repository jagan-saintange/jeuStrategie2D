import pygame
import random
import sys
from unit import *
from abilities import *
from personnages import *

startposP1 = [(2,5), (3,5), (2,6), (3,6)]
startposE = [(18,6), (6,19), (13,15), (19,13)]
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
        else:
            raise TypeError("Sélection impossible, erreur input")
        
        return self.player1_units, self.enemy_units
    

    def show_teams(self):
        show1=[_.perso.nom for _ in self.player1_units]
        show2=[_.perso.nom for _ in self.enemy_units]
        print(f"\nl'equipe du joueur 1 est composé de {show1}")
        print(f"l'equipe de enemy est composé de {show2}")
    
    
    
    def run_ui(self):
        """choix des persos au hasard"""
        print(self.liste_combattants)
        while len(self.player1_units) <4 or len(self.enemy_units)<4:
            if len(self.player1_units) < 4:
                self.selector('player1', 'hasard')
            elif len(self.enemy_units) < 4:
                equipe = 'enemy'    
                self.selector('enemy', 'hasard')
        self.show_teams()
        print('BEEP')
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
