loopEndPoints = []
loopGains = []
loopPaths = []
loopPathSets = []
independentLoopGains = []

def getLoopEndPoints():
	for i in range(len(nextPoints)):
		if nextPoints[i] != None:
			for j in nextPoints[i]:
				nextPoint = j
				if nextPoint < i:
					loopEndPoints.append(i)

def getLoops(currentPoint, loopEnd, currentGain, currentPath):
	if loopEnd == currentPoint:
		loopGains.append(currentGain)
		loopPaths.append(currentPath + str(currentPoint))
	else:
		#Only explore path if next point from loop ending point has index
		#that is smaller than loop ending point.
		if currentPoint < loopEnd:
			#Begin traversal to loop end point from loop start point.
			for i in range(len(nextPoints[currentPoint])):
				nextPoint = nextPoints[currentPoint][i]
				if nextPoint > currentPoint:
					getLoops(nextPoint, loopEnd, currentGain + gains[currentPoint][i], currentPath + str(currentPoint)+"+")

def loopCreation():
	for loopEnd in loopEndPoints:
		#Expand all backwards paths from current loop end point.
		for i in range(len(nextPoints[loopEnd])):
			loopStart = nextPoints[loopEnd][i]
			if loopStart < loopEnd:
				currentGain = gains[loopEnd][i]
				currentPath = loopEnd
				getLoops(loopStart, loopEnd, currentGain, str(currentPath)+ "+")
					
def getIndependentLoops():
	for i in range(len(loopPaths)):
		#Update loopPaths list to remove '+' delimiter and make numbers into ints. Then create
		#a list of sets out of the loopPaths so that intersections can be determined easily.
		loopPaths[i] = list(map(int, loopPaths[i].split("+")))
		loopPathSets.append(set(loopPaths[i]))
	
	for j in range(len(loopPathSets)):
		firstLoop = loopPathSets[j]
		for k in range(j+1, len(loopPathSets)):
			secondLoop = loopPathSets[k]
			if len(firstLoop.intersection(secondLoop)) == 0:
				independentLoopGains.append(loopGains[j]+loopGains[k])
	
if __name__ == '__main__':		
	nextPoints = [[1],[2,0], [3], [2]]
	gains = [["G0"],["G1", "G4"], ["G2"], ["G3"]]
	getLoopEndPoints()
	loopCreation()
	getIndependentLoops()
		
	print("Loop end points are " + str(loopEndPoints))
	print("Loop gains are " + str(loopGains))
	print("Loop paths are " + str(loopPaths))
	print("Independent Loop Gains are " + str(independentLoopGains))