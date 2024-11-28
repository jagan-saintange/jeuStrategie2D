# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 16:13:24 2024

@author: jag
"""

class Unit:
    def __init__(self, x, y, health, team):
        self.x = x
        self.y = y
        self.health = health
        self.team = team

class Archer(Unit):
    def __init__(self, x, y, health, team, attack_power, defense_power, agility_power):
        super().__init__(x, y, health, team)
        self.attack_power = attack_power
        self.defense_power = defense_power
        self.agility_power = agility_power

# Test the classes
archer = Archer(0, 0, 100, 'player', 20, 10, 15)
print(archer.__dict__)
