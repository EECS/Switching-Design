import pickle

loopGains = []
loopPaths = []
loopPathSets = []
forwardPaths = []
forwardPathSets = []
forwardPathGains = []

def getForwardPaths(traversal, currentPoint, endPoint, currentGain, currentPath):
	if currentPoint == endPoint:
		#Add current path, current gain and current path set to appropriate lists
		#for discovered forward path.
		temp = set(list(map(int, (currentPath + str(currentPoint)).split("+"))))
		forwardPaths.append(currentPath + str(currentPoint))
		forwardPathGains.append(currentGain)
		forwardPathSets.append(temp)
	#Continue traversal only if node has not been visited.		
	elif not traversal[currentPoint]:
		traversalSlave = list(traversal)
		traversalSlave[currentPoint] = True
		#Explore all outwards paths from current point to find all potential paths.
		for i_nextPoint in range(len(nextPoints[currentPoint])):
			nextPoint = nextPoints[currentPoint][i_nextPoint]
			getForwardPaths(traversalSlave, nextPoint, endPoint, currentGain +"*"+ gains[currentPoint][i_nextPoint], currentPath + str(currentPoint)+"+")

def forwardPathCreation(startPoint, endPoint):
	#Create traversal boolean list that stores whether a node has been visited
	#to determine when searching is complete.
	traversalMaster = []
	for i in range(len(nextPoints)):
		traversalMaster.append(False)
	
	#Create local copy of traversal list for recursive purposes.
	traversalSlave = list(traversalMaster)
	traversalSlave[startPoint] = True
	#Explore all paths from starting point, to determine forward paths in graph.
	for i_nextNode in range(len(nextPoints[startPoint])):
		nextNode = nextPoints[startPoint][i_nextNode]
		currentGain = gains[startPoint][i_nextNode]
		getForwardPaths(traversalSlave, nextNode, endPoint, currentGain, str(startPoint)+ "+")

#Recursive function to create discover all loops in graph.
def getLoops(traversal, currentPoint, loopEnd, currentGain, currentPath):
	if currentPoint == loopEnd:
		#Need to update short-circuit scheme.
		#Convert current path to set and determine if the set (loop) has been discovered.
		#Only add to loopPathSets if it has not been discovered.
		temp = set(list(map(int, (currentPath + str(currentPoint)).split("+"))))
		pathDiscovered = False
		for i in range(len(loopPathSets)):
			#Path is identical if intersection length is identical to already discovered
			#path length.
			if len(temp.intersection(loopPathSets[i])) == len(loopPathSets[i]):
				pathDiscovered = True
		
		if not pathDiscovered:
			loopGains.append(currentGain)
			loopPaths.append(currentPath + str(currentPoint))
			loopPathSets.append(temp)
			
	elif not traversal[currentPoint]:
		#Begin traversal to loop end point from loop start point.
		for i_nextPoint in range(len(nextPoints[currentPoint])):
			nextPoint = nextPoints[currentPoint][i_nextPoint]
			traversalSlave = list(traversal)
			traversalSlave[currentPoint] = True
			getLoops(traversalSlave, nextPoint, loopEnd, currentGain +"*"+ gains[currentPoint][i_nextPoint], currentPath + str(currentPoint)+"+")

def loopCreation():
	#Create traversal boolean list that stores whether a node has been visited
	#to determine when searching is complete.
	traversalMaster = []
	for i in range(len(nextPoints)):
		traversalMaster.append(False) 
	
	#Explore all paths, across every point, to determine loops in graph.
	for i_loopStart in range(len(nextPoints)):
		for j_nextNode in range(len(nextPoints[i_loopStart])):
			#Create local copy of traversal list for recursive purposes.
			traversalSlave = list(traversalMaster)
			traversalSlave[i_loopStart] = True
			nextNode = nextPoints[i_loopStart][j_nextNode]
			currentGain = gains[i_loopStart][j_nextNode]
			#Current path is current node.
			currentPath = i_loopStart
			getLoops(traversalSlave, nextNode, i_loopStart, currentGain, str(currentPath)+ "+")
					
def getDeltaI():
	deltaI = []
	for currentForwardPath in forwardPathSets:
		#Create empty list for current forward path to append if non-touching loops exist.
		deltaI.append([])
		independentLoopCount = 0
		currentLoop = 0
		for loopPath in loopPathSets:
			if len(currentForwardPath.intersection(loopPath)) == 0:
				deltaI[independentLoopCount].append(loopGains[currentLoop])
				independentLoopCount += 1
			
			currentLoop += 1
	
	return deltaI

def getIndependentLoops(currentDepth, neededLoopDepth, currentLoopPath, loopPathIndex, currentGain, delta):
	#Explore all subsequent loops in the list that are after the loop being currently explored.
	for currentLoopPathIndex in range(loopPathIndex, len(loopPathSets)):
		#Must review validity.
		possibleDepth = len(loopPathSets) - currentLoopPathIndex + currentDepth
		#print("Current loop path index " + str(currentLoopPathIndex))
		if possibleDepth >= neededLoopDepth:
			loopPathSet = loopPathSets[currentLoopPathIndex]
			if len(currentLoopPath.intersection(loopPathSet))==0:
				#print("Here")
				if currentDepth != neededLoopDepth:
					getIndependentLoops(currentDepth+1, neededLoopDepth, currentLoopPath, currentLoopPathIndex, currentGain+loopGains[currentLoopPathIndex], delta)
				else:
					delta[neededLoopDepth-1].append(currentGain)	
		else:
			break
	
def getDelta():
	delta = []
	
	#Create delta list where the ith entry is equal to the ith + 1 loop combinations.
	#E.g. The index 1 entry in the list will hold the independent loop gains taken 2 at a time.
	for i in range(len(loopPaths)):
		if i == 0:
			delta.append(loopGains)
		else:
			delta.append([])
	
	currentLoopPair = 1
	
	#Continue searching for independent loop pairs if independent loop pairs at previous integer have been found
	#and as long as the amount of independent loop pairs does not exceed the total number of loops.
	while currentLoopPair <= len(loopGains) and len(delta[currentLoopPair-1]) > 0:
		currentDepth = 1
		#Attempting to find independent loop pairs taken neededLoopDepth "at a time".
		#E.g. if neededLoopDepth is 2, trying to find independent loop pairs taken 2 at a time.
		neededLoopDepth = currentLoopPair + 1
		#Update so that multiple sets aren't explored several times.
		for j in range(len(loopPathSets)):
			currentLoopPath = loopPathSets[j]
			#Compare the next set with the current set to determine independence.
			loopPathIndex = j+1
			currentGain = loopGains[j]
			getIndependentLoops(currentDepth, neededLoopDepth, currentLoopPath, loopPathIndex, currentGain, delta)
			
		currentLoopPair += 1
	
	return delta

def masonGainFormula(delta_I, delta):
	numerator = ''
	denominator = ''
	
	#Create numerator of mason gain formula.
	gainPathCount = 0
	for gain in forwardPathGains:
		delta_I_temp = ''
		for nontouchingLoop in delta_I[gainPathCount]:
			#First non-touching loop is identified.
			if delta_I_temp == '':
				delta_I_temp += nontouchingLoop
			else:
				delta_I_temp += "+" + nontouchingLoop
		
		if numerator != '':
				numerator += "+"
		#No non-touching loops on forward path.
		if delta_I_temp == '':
			numerator += gain
		#Non-touching loops on forward path exist
		else:
			numerator += gain + "*"+"(1-"+"("+delta_I_temp+")"+")"
				
		gainPathCount += 1
	
	numerator = "("+numerator+")"
	#Create denominator of mason gain formula.
	independentLoopPair = 1
	for loopPairs in delta:
		#Only add to denominator if loop pairs are populated.
		if len(loopPairs)>0:
			deltaTemp = ""
			for loop in loopPairs:
				if deltaTemp != '':
					deltaTemp += "+"
					
				deltaTemp += loop
			
			deltaTemp = "(" + deltaTemp + ")"
			
			#Odd loop pairs are subtracted in the delta formula.
			if independentLoopPair%2 != 0:
				deltaTemp = "-" + deltaTemp
			else:
				deltaTemp = "+" + deltaTemp
				
			independentLoopPair += 1
			
			denominator = denominator + deltaTemp
	
	#Format denominator with leading 1.
	denominator = "((1)" + denominator+")"
	
	return numerator+"/"+denominator

#################################################################################
#Standard Form portion of the program below, mason gain portion above.
#################################################################################

def findDenominator(masonGainForm):
	parenStack = []
	denomStart = 0
	
	#Loop through string to determine the start of the denominator.
	for c in masonGainForm:
		#Open parentheses indicates new term to be discovered.
		if c == "(":
			parenStack.append(c)
		#Close parantheses indicates last term is now closed.
		elif c == ")":
			parenStack.pop()
		elif c == "/":
			#Denominator occurs when all parens are closed and a division character occurs.
			if len(parenStack) == 0:
				return denomStart + 1
		
		denomStart += 1
	
	return denomStart
	
def getTerms(numerDenom):
	parenStack = []
	currentTerm = ""
	#Track individual terms between curly braces e.g. ().
	tempTerm = ""
	#Term list where new entries indicate summation of terms.
	terms = []
	isNegative = False
	
	for c in numerDenom:
		#Open parentheses indicates new term to be discovered.
		if c == "(":
			parenStack.append(c)
		#Close parantheses indicates last term is now closed.
		elif c == ")":
			parenStack.pop()
		else:
			tempTerm += c
	#Numerator or denominator does not contain any addition or subtraction operations,
	#must add it to the term list after search is complete.
	if len(currentTerm) != 0:
		terms.append(currentTerm)
	
	return terms
	
if __name__ == '__main__':
	#Length is equal to total nodes in graph.
	#Graph indices in nextPoints are equal to their nodes.
	#points = [Node([1], ["(1)"]), Node([2, 3], ["(1/R2)", "(1/R1)"]), Node([4], ["(1)"])]
    nextPoints = [[1],[2],[3,4],[1],[1]]
    gains = [['(1)'],['(1/R1)'],['(R2)','(R3)'],['(-1)'],['(-1)']]
    forwardPathCreation(0, 1)
    loopCreation()
    delta_I = getDeltaI()
    delta = getDelta()
    masonGain = masonGainFormula(delta_I, delta)
    
    filename = "Test.pickle"
    
    with open(filename, 'wb') as f:
        pickle.dump(masonGain, f)
	
	print("Forward Paths are " + str(forwardPaths))
	print("Forward Path Gains are " + str(forwardPathGains))
	print("Loop gains are " + str(loopGains))
	print("Loop paths are " + str(loopPaths))
	print("Delta I, Independent Loop gains from forward path " + str(delta_I))
	print("Delta " + str(delta))
	print("Mason Gain Formula: " + str(masonGain))