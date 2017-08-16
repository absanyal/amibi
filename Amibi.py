# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 18:36:50 2017

@author: AB Sanyal
"""

#Imports
import numpy as np
import matplotlib.pyplot as plt
import random

#Parameters of the world
WorldPopCap = 10000000 #Reproduction occurs if pop less than cap
family = []
WorldFood = 0
WorldO2 = 0
WorldCO2 = 1000
DNA_Size = 15

#DNA bases
commonbases = [ #By default, they are present in the initial family
        "E", #Eat: -1 food, +1 energy,-1 O2, +1 CO2; if food < 0, -1 energy
        "R", #Reproduce: Create 1 offspring if energy > 500 and -450 energy
        "P", #Photosynthesis: +1 energy, +2 food, +1 O2, -1 CO2
         ]

rarebases = [ #Not present initially; can mutate into later population with a 1% chance
            "ca", #Carnivorous eating: Eat a random prey to gain its energy
            "r2", #Reproduce 2: Create two identical offsprings, -100 food; -25 energy
            "ea", #Anaerobic respiration: -2 food, +1 energy, +2 CO2
            "hl", #Hydrolysis: -1 energy, -1 food, +1 O2, +1 CO2
            ]

#Probabilities associated with common bases
p_common = [0.5, 0.1, 0.4]

#Display DNA formatted
def formatdna(dna):
    p = ''
    for base in dna:
        p += base + '-'
    p = p.strip('-')
    return p

#Generate a random DNA; it will always contain only common bases
def generate_random_dna():
    return list(np.random.choice(commonbases, size = DNA_Size, p = p_common))

#DNA point mutation
def mutate(dna_o):
    dna = dna_o[:]
    i = 0
    while (i < len(dna)):
        r = np.random.uniform(0, 1)
        if (r > 0.01 and r < 0.03):
            original_base = dna[i]
            dna[i] = np.random.choice(commonbases)
            while (dna[i] == original_base):
                dna[i] = np.random.choice(commonbases)
        if (r <= 0.01):
            original_base = dna[i]
            dna[i] = np.random.choice(rarebases)
            while (dna[i] == original_base):
                dna[i] = np.random.choice(rarebases)
        i += 1
    return dna

#Generator of ID numbers
def id_num():
    i = 1
    while (True):
        yield i
        i += 1

id_no = id_num()

#Creature Class
class amibi:
    def __init__(self, dna):
        self.idno = next(id_no)
        self.dna = dna
        self.energy = 50
        self.age = 0
        self.lifespan = 300 * random.betavariate(500, 500)

#Create initial family
for i in range(10):
    dna = generate_random_dna()
    a = amibi(dna)
    family.append(a)

#Data to be recorded for plotting
pop_data = [len(family)]
food_data = [WorldFood]
o2_data = [WorldO2]
co2_data = [WorldCO2]

t = 0 #Time steps
while (t <= 2000 and len(family) > 0):

    if (t % 50 == 0):
        print("At t = ", t, "World pop:", len(family), "Food:", WorldFood, "O2:", WorldO2, "CO2:", WorldCO2)


    random.shuffle(family) #Shuffle the order of amibi so as to select the amibi at random

    for a in family:

        a.age += 1 #Get older

        if (a.age > 0 and a.age % 10 == 0 and a.energy > 0):
            a.energy -= 1

        #Translation
        dna = a.dna[:]
        for base in dna: #Read each base and do what it says

            if (a.energy > 0):

                if (base == 'E' and WorldFood > 0 and WorldO2 > 2):
                    WorldFood -= 1
                    WorldO2 -= 2
                    WorldCO2 += 2
                    a.energy += 1

                if (base == 'R' and WorldFood > 0 and a.age > int(a.lifespan * 0.3) and a.age < int(a.lifespan * 0.6) ):
                    if (a.energy > 600 and len(family) < WorldPopCap):
                        r = random.uniform(0, 1)
                        if (r > a.age / a.lifespan - 0.25 ):
                            childdna = mutate(dna[:])
                            family.append(amibi(childdna))
                            a.energy -= 550
                    else:
                        a.energy -= 10

                if (base == 'P' and WorldCO2 > 2):
                    WorldFood += 2
                    WorldO2 += 2
                    a.energy += 1
                    WorldCO2 -= 2

                if (base == 'ca' and a.energy > 100):
                    r = np.random.uniform(0, 1)
                    if (len(family) > 1 and r < 0.2 and WorldO2 > 100):
                        preylist = family[:]
                        preylist.remove(a)
                        prey = np.random.choice(preylist)
                        a.energy += int( prey.energy / 3 )
                        WorldCO2 += 100
                        WorldO2 -= 100
                        family.remove(prey)
                    else:
                        a.energy -= 100

                if ( base == 'r2' and a.energy > 50):

                    if (len(family) < WorldPopCap and WorldFood > 500
                    and a.age > int(a.lifespan * 0.3) and a.age < int(a.lifespan * 0.4) ):
                        r = random.uniform(0, 1)
                        if (r > a.age / a.lifespan - 0.25 ):
                            childdna = mutate(dna[:])
                            family.append(amibi(childdna))
                            family.append(amibi(childdna))
                            WorldFood -= 500
                            a.energy -= 475
                    else:
                        a.energy -= 50

                if (base == 'ea' and WorldFood > 2 and WorldO2 <= 0):
                    WorldFood -= 2
                    WorldCO2 += 2
                    a.energy += 1

                if (base == 'hl' and a.energy > 100 and WorldFood > 50):
                    WorldFood -= 50
                    a.energy -= 100
                    WorldO2 += 50
                    WorldCO2 += 50

    #Reaper protocol to purge the dead

    for a in family: #Starvation

        if (a.energy <= 0):
            family.remove(a)

    for a in family: #Chance of death at advanced age
        if (a.age > 0.75 * a.lifespan):
            r = random.uniform(0, 1)
            if (r > 0.5):
                family.remove(a)

    for a in family: #Definite death at endof lifespan

        if ( a.age > a.lifespan ):
            family.remove(a)


    #Record all data
    pop_data.append(len(family))
    food_data.append(WorldFood)
    o2_data.append(WorldO2)
    co2_data.append(WorldCO2)

    t += 1

print("Final : At t = ", t - 1, "World pop is", len(family))

#Plot Stuff
plt.plot(pop_data)
plt.title("Population")
plt.show()

plt.plot(food_data)
plt.title("World Food")
plt.show()

plt.plot(o2_data)
plt.title("World O2")
plt.show()

plt.plot(co2_data)
plt.title("World CO2")
plt.show()