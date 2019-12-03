import json
import numpy as np
from collections import defaultdict
worldPoints = defaultdict(list)

# Front Wall
tags = [x for x in range(42,50)]
tags = tags + [x for x in range(0,11)]
xs = list(range(-40, 55, 5))
for i,t in enumerate(tags):
    x = xs[i]
    y = 0
    z = 0
    worldPoints[t] = [[x,y,z], [x+1, y, z], [x+1,y-1,z], [x,y-1,z]]

# Left Wall
worldPoints[40] = [[-45,0,3],[-45,0,2],[-45,-1,2],[-45,-1,3]]
worldPoints[41] = [[-45,0,10],[-45,0,9],[-45,-1,9],[-45,-1,10]]
worldPoints[39] = [[-63,0,15],[-63,0,14],[-63,-1,14],[-63,-1,15]]
worldPoints[38] = [[-63,0,20],[-63,0,19],[-63,-1,19],[-63,-1,20]]
worldPoints[37] = [[-63,0,25],[-63,0,24],[-63,-1,24],[-63,-1,25]]
worldPoints[36] = [[-63,0,30],[-63,0,29],[-63,-1,29],[-63,-1,30]]

# Right Wall
worldPoints[11] = [[55,0,4], [55,0,5],[55,-1,5],[55,-1,4]]
worldPoints[12] = [[73,0,15],[-73,0,16],[73,-1,16],[73,-1,15]]
worldPoints[13] = [[73,0,20],[-73,0,21],[73,-1,21],[73,-1,20]]
worldPoints[14] = [[73,0,25],[-73,0,26],[73,-1,26],[73,-1,25]]
worldPoints[15] = [[73,0,30],[-73,0,31],[73,-1,31],[73,-1,30]]

# Left Doorway

worldPoints[18] = [[-60,0,5], [-60,0,4], [-60,-1,4],[-60,-1,5]]
# Right Doorway
worldPoints[17] = [[-47,0,10],[-46,0,10],[-46,-1,10],[-47,-1,10]]
worldPoints[23] = [[-46,0,0],[-46,0,1],[-46,-1,1],[-46,-1,0]]

# Hallway Farside
worldPoints[24] = [[-56,0,-33],[-55,0,-33],[-55,-1,-33],[-56,-1,-33]]
worldPoints[26] = [[-37,0,-33],[-36,0,-33],[-36,-1,-33],[-37,-1,-33]]

worldPoints[30] = [[-27,0,-33],[-26,0,-33],[-26,-1,-33],[-27,-1,-33]]
worldPoints[31] = [[-22,0,-33],[-21,0,-33],[-21,-1,-33],[-22,-1,-33]]

# Hallway Near side
worldPoints[25] = [[-37,0,-6],[-37,0,-5],[-37,-1,-5],[-37,-1,-6]]
worldPoints[27] = [[-42,0,-1],[-43,0,-1],[-43,-1,-1],[-42,-1,-1]]
worldPoints[28] = [[-27,0,-1],[-28,0,-1],[-28,-1,-1],[-27,-1,-1]]
worldPoints[29] = [[-22,0,-1],[-23,0,-1],[-23,-1,-1],[-22,-1,-1]]

with open('worldPoints.json', 'w') as f:
    json.dump(worldPoints, f)
