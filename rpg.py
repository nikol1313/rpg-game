#!/usr/bin/env python3
from collections import deque
import functools, time, random

def buff(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        multiplier = random.randint(1, 5)
        original_attack_power = self.attack_power
        self.attack_power = original_attack_power * multiplier
        print(f"-> BUFF ACTIVE: Power increased {multiplier}x! Current temporary attack power: {self.attack_power}")
        result = func(*args, **kwargs)
        self.attack_power = original_attack_power
        return result
    return wrapper

def def_buff(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if getattr(self, 'has_jackpot', False):
            return func(*args, **kwargs)
        multiplier = random.randint(2, 4)
        original_defense = self.defense
        self.defense = original_defense * multiplier
        print(f"-> BUFF ACTIVE: defense increased {multiplier}x! Current temporary defense is: {self.defense}")
        result = func(*args, **kwargs)

        self.defense = original_defense
        return result
    return wrapper

def cooldowns(seconds):
    def decorator(func):
        last_called = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            now = time.time()
            if self.name in last_called and now - last_called[self.name] < seconds:
                print(f"-> COOLDOWN: {self.name}'s ability is on cooldown!")
                return None
            last_called[self.name] = now
            return func(*args, **kwargs)
        return wrapper
    return decorator

def blast_crit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        original_blast_power = self.blast
        is_crit = random.random() < 0.3
        if is_crit:
            random_crit = random.randint(1, 3)
            self.blast = original_blast_power * random_crit
            print(f"-> CRITICAL HIT BONUS FOR BLAST! Critical multiplier: {random_crit}x (Base for this hit: {original_blast_power})")
        result = func(*args, **kwargs)
        self.blast = original_blast_power
        return result
    return wrapper

class Inventory:
    def __init__(self):
        self.items = []
    def add_item(self, item):
        self.items.append(item)
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
    def list_items(self):
        for item in self.items:
            print(f"{item.name} - {item.description}")

class Item:
    def __init__(self, name, description, weight):
        self.name = name
        self.description = description
        self.weight = weight
    def use(self, target):
        raise NotImplementedError

class Consumable(Item):
    def __init__(self, name, description, weight, heal_amount=0, mana_restore=0):
        super().__init__(name, description, weight)
        self.heal_amount = heal_amount
        self.mana_restore = mana_restore
    def use(self, target):
        target.hp += self.heal_amount
        print(f"{target.name} healed {self.heal_amount} HP")

class Equipment(Item):
    def __init__(self, name, description, weight, attack_bonus=5, defense_bonus=5):
        super().__init__(name, description, weight)
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
    def equip(self, target):
        target.attack_stat += self.attack_bonus
        target.defense += self.defense_bonus
        print(f"{target.name} equipped {self.name}")
    def unequip(self, target):
        target.attack_stat -= self.attack_bonus
        target.defense -= self.defense_bonus
        print(f"{target.name} unequipped {self.name}")

class Hero:
    def __init__(self, name, power, attack, shield, blast, hp=100, attack_power=15, defense=10):
        self.name = name
        self.power = power
        self.attack_stat = attack
        self.shield = shield
        self.blast = blast
        self.hp = hp
        self.attack_power = attack_power
        self.defense = defense
        self.inventory = Inventory()
    @cooldowns(2)
    @buff
    @blast_crit
    def attack_enemy(self, enemy):
        mitigation = enemy.defense / (enemy.defense + 50)
        damage = max(10, int(self.attack_power * (1.2) * (1 - mitigation)))
        enemy.hp -= damage
        return f"{self.name} attacks {enemy.name} for {damage} damage! Enemy HP: {enemy.hp}"

class Enemy:
    def __init__(self, name, power, attack, shield, hp=100, attack_power=12, defense=20):
        self.name = name
        self.attack_stat = attack
        self.shield = shield
        self.power = power
        self.defense = defense
        self.hp = hp
        self.attack_power = attack_power
    @cooldowns(1)
    @def_buff
    def attack(self, target):
        damage = max(3, int(self.attack_power * 1.2))
        target.hp -= damage
        print(f"{self.name} attacks {target.name} for {damage} damage! {target.name}'s HP: {target.hp}")

class BattleQueue:
    def __init__(self):
        self.queue = deque()
    def enqueue(self, character):
        self.queue.append(character)
    def dequeue(self):
        if self.queue:
            return self.queue.popleft()
        return None
    def is_empty(self):
        return len(self.queue) == 0

player = Hero("Hero", power=10, attack=7, shield=3, blast=5)
enemy = Enemy("Goblin", power=7, attack=6, shield=5)

battle_queue = BattleQueue()
battle_queue.enqueue(player)
battle_queue.enqueue(enemy)

while not battle_queue.is_empty():
    fighter = battle_queue.dequeue()
    if fighter and fighter.hp > 0:
        if isinstance(fighter, Enemy):
            fighter.attack(player)
        elif isinstance(fighter, Hero):
            res = fighter.attack_enemy(enemy)
            if res:
                print(res)
        time.sleep(0.5)
        if fighter.hp > 0:
            battle_queue.enqueue(fighter)
    if player.hp <= 0 or enemy.hp <= 0:
        if random.random() < 0.5:
            print("THE PLAYER RESSURECTED, CONTINUING THE GAME:")
            battle_queue.enqueue(fighter)
        else:
            print("Battle ended!")
            break
