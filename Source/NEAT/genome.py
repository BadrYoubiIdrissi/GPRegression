# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 12:21:44 2016

@author: Badr Youbi Idrissi

Un genome est un contennaire de connexions et de noeuds

C'est sur cet objet que va opérer les opérateurs génétiques
"""

import prob.mutation
from scipy.stats import bernoulli, norm
from connexion import Connexion
from noeud import Noeud
import random
import pygame

class Genome():
    def __init__(self, *args, **kwargs):
        if kwargs['generer']:
            self.nb_entree = args[0]            
            self.nb_sortie = args[1]
            self.indiceInnov = 0
            self.noeuds = []
            self.connexions = []            
            
            for i in range(self.nb_entree):
                self.noeuds.append(Noeud(i, "entree"))
            
            for i in range(self.nb_entree,self.nb_entree + self.nb_sortie):
                self.noeuds.append(Noeud(i, "sortie"))
            
            for i in range(self.nb_entree):
                for j in range(self.nb_sortie):
                    self.indiceInnov += 1
                    self.connexions.append(Connexion(i,j,norm.rvs(),self.indiceInnov))
    
        else:
            self.connexions = args[0]
            self.noeuds = args[1]
            self.indiceInnov = len(self.noeuds)    
            
    def weight_mutation(self):
        for c in self.connexions:
            if bernoulli.rvs(prob.mutation.poids_radical):
                c.poids = norm.rvs()
            else:
                c.poids  += 0.1*norm.rvs()
                
    def node_mutation(self):
        connex_alea = random.sample(self.connexions,1)
        connex_alea.activation = False
        
        noeud = Noeud(len(self.noeuds)+1, "cache")
        entree = connex_alea.entree
        sortie = connex_alea.sortie
        
        self.indiceInnov += 1
        con1 = Connexion(entree, noeud.id, norm.rvs(), self.indiceInnov)
        
        self.indiceInnov += 1
        con2 = Connexion(noeud.id, sortie, norm.rvs(), self.indiceInnov)
        
        self.noeuds.append(noeud)
        self.connexions.append(con1)
        self.connexions.append(con2)
    
    def connection_mutation(self):
        entree = random.randint(0,len(self.noeuds)-1)
        sortie = random.randint(entree+1, self.len(self.noeuds)-1)
        self.indiceInnov += 1
        self.connexions.append(Connexion(entree, sortie, norm.rvs(), self.indiceInnov))
    
    def draw(self, x, y):
        screen = pygame.display.get_surface()
        i = 0
        j = 0 
        for n in self.noeuds:
            if n.fonction == "entree":
                pygame.draw.circle(screen, (0,255,0), (x+30*i,y), 10)
                i += 1
            elif n.fonction == "sortie":
                pygame.draw.circle(screen, (0,0,255), (x+30*j,y+100), 10)
                j += 1

                