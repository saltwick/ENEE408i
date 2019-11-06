import json
import numpy as np

worldPoints = {}

worldPoints[0] = np.array([[0,0,0],[0,1,0],[1,1,0],[1,0,0]]).tolist()
worldPoints[1] = np.array([[10,0,0],[10,1,0],[11,-1,0],[9,-1,0]]).tolist()
worldPoints[2] = np.array([[20,0,0],[20,1,0],[11,-1,0],[9,-1,0]]).tolist()
worldPoints[3] = np.array([[30,0,0],[30,1,0],[11,-1,0],[9,-1,0]]).tolist()

with open('worldPoints.json', 'w') as f:
    json.dump(worldPoints, f)

