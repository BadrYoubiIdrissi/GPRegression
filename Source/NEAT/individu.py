# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 12:40:45 2016

Objet Individu:
    Un objet individu contient un genome et un phenotype, faisant le lien entre
    les deux. Il s'occupera aussi à se muter correctement.

@author: Badr Youbi Idrissi
"""

from genome import Genome
from phenotype import Phenotype
from connexion import Connexion
from scipy.stats import bernoulli, norm

import random as rand
import prob.crossover
import utilitaires as ut

class Individu():
    
    def __init__(self, nb_entrees, nb_sorties):
        self.nb_e = nb_entrees
        self.nb_s = nb_sorties
        self.genome = Genome(self.nb_e,self.nb_s)
        self.phenotype = Phenotype(self.nb_e,self.nb_s)
        self.idToPos = {} #Ce tableau fera l'interface entre le genome et l'individu
    
    def __add__(self, mate):
        fils = Individu(self.nb_e, self.nb_s)
        
        #On fait le croisement des genomes dans un premier temps
        plusGrdInnov = max(max(self.genome.connexions), max(mate.genome.connexions))
        plusFort = self.fitness() > mate.fitness()
        
        if plusFort:
            fils.phenotype = self.phenotype
        else:
            fils.phenotype = mate.phenotype
        
        for i in range(plusGrdInnov+1):
            selfcon = self.genome[i]
            matecon = self.genome[i]
            if selfcon != None and matecon != None:
                c = ut.randomPick([selfcon, matecon])
                #Ici on dans le cadre de deux connexions de meme indice d'innov
                if not(selfcon.activation) or not(matecon.activation) : 
                    #On a une probabilité "prob.crossover.activation" d'activer
                    #les connexions désactivés dans les parents
                    if rand.random() < prob.crossover.activation :
                        c.activer()
                    else : 
                        c.desactiver()
                fils.genome.connexions[i] = c
                fils.phenotype.modifierConnexion(c.entree, c.sortie, self.idToPos, c.poids)
            #Les cas ici traitent les genes disjoints ou en excès
            elif selfcon == None:
                if not(plusFort):
                    fils.genome.connexions[i] = matecon
                    fils.phenotype.modifierConnexion(matecon.entree, matecon.sortie, self.idToPos, matecon.poids)
            elif matecon == None:
                if plusFort:
                    fils.genome.connexions[i] = selfcon
                    fils.phenotype.modifierConnexion(selfcon.entree, selfcon.sortie, self.idToPos, selfcon.poids)

        fils.phenotype.reinit()
        return fils
    
    def generer(self):
        #On ajoute au début les entrées et les sorties
        self.idToPos = { i : (0,i) for i in range(self.nb_e)}
        self.idToPos.update({self.nb_e + j : (1,j) for j in range(self.nb_s)})
        #On met les valeurs de poids de genome dans le phenotype
        self.genome.generer()
        self.phenotype.generer()
        for innov in self.genome.connexions:
            c = self.genome.connexions[innov]
            k, l = self.idToPos[c.sortie][1], self.idToPos[c.entree][1]
            self.phenotype.liens[0][1][k,l] = c.poids
        
    def fitness(self):
        return 0
        
    def add_key(self, nouvid, couche, num):
        """Met à jour la table idToPos en ajoutant un noeud qui 
        sera en la couche et dont le numéro est num"""
        assert nouvid not in self.idToPos, "Le nouvel identifiant ne doit pas être existent"
        self.idToPos[nouvid] = (couche, num)
    
    def insertLayer(self, couche):
        """Insère une couche aprés la couche indiqué en paramètre"""
        #Décale tous les position d'une couche
        for i in self.idToPos:
                if self.idToPos[i][0] > couche:
                    n, h = self.idToPos[i]
                    self.idToPos[i] = (n+1,h)
        #Ajoute une nouvelle couche en inserant de nouvelles matrices liens
        self.phenotype.insertLayer(couche)
    
    def posToId(self, pos):
        for i in self.idToPos:
            if self.idToPos[i] == pos:
                return i
    
    def insertNoeudCouche(self, couche, idNouvNoeud):
        assert idNouvNoeud not in self.idToPos, "Noeud déja existant"
        self.phenotype.insertNode(couche)
        self.idToPos[idNouvNoeud] = (couche, len(self.phenotype.couches[couche])-1)
    
    def insertNoeud(self, con, p1, p2, innov, idNouvNoeud):
        """Cette fonction prend une connexion déja existante et la remplace par deux
           nouvelle connexions et un noeud intermédiaire qui occupera la couche milieu si elle existe
           et créera une nouvelle couche si la connexion relie deux couches succéssives ou la même couche"""
        #On désactive la connexion précèdente
        idN1 = con.entree
        idN2 = con.sortie
        con.desactiver()
        #On récupère la position dans le phénotype des deux noeuds précèdemment reliés
        c1, n1 = self.idToPos[idN1]
        c2, n2 = self.idToPos[idN2]
        
        #On a une disjonction de cas selon que les deux noeuds était dans deux couches successifs ou pas
        if abs(c1-c2) >= 2:
            #Si les deux noeuds ne sont pas dans de ux couches succéssifs alors on met le nouveau noeud 
            #dans une couche au milieu des deux couches
            m = (c1+c2)//2
            p = len(self.phenotype.couches[m])  
            #On met à jour la table idToPos
            self.add_key(idNouvNoeud, m,p)
            #On insère le noeud dans la couche m
            self.phenotype.insertNode(m)
            
            self.phenotype.modifierConnexion(idN1,idNouvNoeud, self.idToPos,p1)
            self.phenotype.modifierConnexion(idNouvNoeud, idN2, self.idToPos,p2)
            self.phenotype.modifierConnexion(idN1, idN2, self.idToPos, 0)
            
            self.genome.ajouterConnexion(idN1, idNouvNoeud, p1, innov)
            self.genome.ajouterConnexion(idNouvNoeud, idN2, p2, innov+1)

        else:
            #On ajoute la nouvelle couche en dessus de la couche en dessous (ie le min)
            c = min(c1,c2)
            
            self.insertLayer(c)
            self.insertNoeudCouche(c+1, idNouvNoeud)
            c1, n1 = self.idToPos[idN1]
            c2, n2 = self.idToPos[idN2]

            self.phenotype.modifierConnexion(idN1, idNouvNoeud, self.idToPos, p1)
            self.phenotype.modifierConnexion(idNouvNoeud, idN2, self.idToPos, p2)
            self.phenotype.modifierConnexion(idN1, idN2, self.idToPos, 0)
            
            self.genome.ajouterConnexion(idN1, idNouvNoeud, p1, innov)
            self.genome.ajouterConnexion(idNouvNoeud, idN2, p2, innov+1)
        
        self.phenotype.reinit()
    
    def connexionPossible(self):
        if not(self.phenotype.estComplet()):
            noeuds = self.idToPos.keys()
            noeudsSansEntree = [i for i in noeuds if (i not in range(self.nb_e))]
            e = ut.randomPick(noeuds)
            s = ut.randomPick(noeudsSansEntree)
            c = self.genome.entreeSortieToCon(e,s)
            while c != None and c.activation:
                e = ut.randomPick(noeuds)
                s = ut.randomPick(noeudsSansEntree)
                c = self.genome.entreeSortieToCon(e,s)
            if c !=None:
                return c
            else:
                return Connexion(e, s, 1)
    
    def mutationPoids(self):
        for c in self.connexions:
            if bernoulli.rvs(prob.mutation.poids_radical):
                c.poids = norm.rvs()
            else:
                c.poids  += 0.1*norm.rvs()
            self.phenotype.modifierConnexion(c.entree, c.sortie, self.idToPos, c.poids)
                
    def insertLien(self, c, innov):      
        self.phenotype.modifierConnexion(c.entree, c.sortie, self.idToPos, c.poids)
        if not(c.activation):
            c.activer()
        else:
            self.genome.ajouter(c, innov)
    
    def draw(self, pos):
        self.phenotype.draw(pos, self.posToId)
    
