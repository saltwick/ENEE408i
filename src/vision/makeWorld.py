import json
import numpy as np
from collections import defaultdict
worldPoints = defaultdict(list)

tags = [x for x in range(43,50)]
tags = tags + [x for x in range(0,9)]

xs = list(range(-35, 45, 5))
for i,t in enumerate(tags):
    x = xs[i]
    y = 0
    z = 0
    worldPoints[t] = [[x,y,z], [x+1, y, z], [x+1,y-1,z], [x,y-1,z]]


with open('worldPoints.json', 'w') as f:
    json.dump(worldPoints, f)
