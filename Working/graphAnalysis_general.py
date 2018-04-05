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

def getDeltaI(delta):
    deltaI = []
    currentForwardPath_count = 0
    dependentLoopGains = []
    for currentForwardPath in forwardPathSets:
        #Create empty list for current forward path to append delta I to.
        deltaI.append([])
        #Create empty list for current forward path to append dependent loop gains on the forward path.
        dependentLoopGains.append([])
        currentLoop = 0
        #Find loop paths that are dependent on current forward path.
        for loopPath in loopPathSets:
            if len(currentForwardPath.intersection(loopPath)) != 0:
                dependentLoopGains[currentForwardPath_count].append(loopGains[currentLoop])

            currentLoop += 1

        sum = ''
        #Sum together all loop gains that are dependent on the forward path.
        for loopGain in dependentLoopGains[currentForwardPath_count]:
            if sum =='':
                sum += loopGain
            else:
                sum += "+"+loopGain
        
        #Append the sum of the loop gains that are dependent
        if sum != '':
            deltaI[currentForwardPath_count].append(sum)

        currentForwardPath_count += 1

    return deltaI

def getIndependentLoops(currentDepth, neededLoopDepth, nextLoopPath_Index, currentLoopPathSets, currentGain, delta):
    #Explore all subsequent loops in the list that are after the loop being currently explored.
    for currentLoopPathIndex in range(nextLoopPath_Index, len(loopPathSets)):
        #Possible depth is equal to the total amount of loops minus the current loop being explored plus the current depth of the search
        #E.g. [Loop A, Loop B, Loop C], exploring loop B with a starting loop of A, length is 3, currentLoopPathIndex is 1,
        #current depth is 1 for a possible depth of 3, which is possible if A, B and C are independent.
        possibleDepth = (len(loopPathSets)) - currentLoopPathIndex + currentDepth
        #Only explore this path if the possible depth of the independent loops exceeds the needed loop depth for the delta equation.
        #e.g. if the possible loop depth is 2 but the needed pairs of loops taken "at a time" is 3, the loop will not continue
        #because the path cannot yield independent loop pairs of the correct number.
        if possibleDepth >= neededLoopDepth:
            loopPathSet = loopPathSets[currentLoopPathIndex]
            #print("Current Tested Loop Path: "+str(loopPathSet))
            addLoop = False
            #Determine if loops are independent from one another. Must check that the loops are independent from all previously
            #explored loops in order to be truly independent as a group. I.E., just because A is independent from B and A is
            # independent from C, B is not necessarily independent from C.
            for independentLoop_index in range(len(currentLoopPathSets)):
                currentPathTest = currentLoopPathSets[independentLoop_index]
                #print("Top Level Loop Path Set: "+str(currentPathTest))
                if len(currentPathTest.intersection(loopPathSet)) == 0:
                    #print("Independence True")

                    #Only add the loop path to the set of independent loop paths if
                    #loopPathSet is independent from all previous loop paths.
                    if(independentLoop_index == len(currentLoopPathSets)-1):
                        addLoop = True
                else:
                    break
            
                if addLoop:
                    #print("Current Depth: "+str(currentDepth))
                    #print("Needed depth: "+str(neededLoopDepth))
                    if currentDepth != neededLoopDepth:
                        currentLoopPathSetsCopy = list(currentLoopPathSets)
                        #Append the current indepent loopPathSet to the list of independent sets in currentLoopPathSetsCopy.
                        currentLoopPathSetsCopy.append(loopPathSet)
                        #Current depth is not equal to needLoopDepth, thus continue searching for the correct number of
                        #independent loop pairs taken "at a time." Calling the function again increases the depth by 1,
                        #as well as the index at which loops are being searched for. 
                        getIndependentLoops(currentDepth+1, neededLoopDepth, currentLoopPathIndex+1,currentLoopPathSetsCopy,
                        currentGain+"*"+loopGains[currentLoopPathIndex], delta)
                    else:
                        #print("Loop Added")
                        delta[neededLoopDepth-1].append(currentGain+"*"+loopGains[currentLoopPathIndex])
                        addLoop = False
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

    #Represents the amount of loops to be taken "at a time". Start at 2 "loops at a time", already gathered
    # the 1 "loop at a time" case with finding all loops in the graph.
    neededLoopDepth = 2

    #Continue searching for independent loop pairs if independent loop pairs at previous pair integer have been found
    #and as long as the neededLoopDepth does not exceed the total number of loops in loopGains.
    while neededLoopDepth <= len(loopGains) and len(delta[neededLoopDepth-2]) > 0:
        #Current depth of loop pairs. At the top level, the first test is taken 2 "at a time."
        currentDepth = 2
        #Update so that multiple sets aren't explored several times.
        for j in range(len(loopPathSets)):
            currentLoopPath = loopPathSets[j]
            #Compare the next set with the current set to determine independence.
            nextLoopPath_Index = j+1
            currentGain = loopGains[j]
            getIndependentLoops(currentDepth, neededLoopDepth, nextLoopPath_Index, [currentLoopPath], currentGain, delta)

        neededLoopDepth += 1

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

if __name__ == '__main__':
    #Length is equal to total nodes in graph.
    #Graph indices in nextPoints are equal to their nodes.
    #points = [Node([1], ["(1)"]), Node([2, 3], ["(1/R2)", "(1/R1)"]), Node([4], ["(1)"])]
    nextPoints = [[1],[2],[3],[1,5],[5,1],[]]
    gains = [['(1)'],['(1/R1)'],['(R2)'],['(-1)','(1)'],['(1)','(-1)'],[]]
    forwardPathCreation(4, 5)
    loopCreation()
    delta = getDelta()
    delta_I = getDeltaI(delta)

    masonGain = masonGainFormula(delta_I, delta)
    
    filename = "Test.pickle"
    
    with open(filename, 'wb') as f:
        pickle.dump(masonGain, f)

    print("Forward Paths are " + str(forwardPaths))
    print("Forward Path Gains are " + str(forwardPathGains))
    print("Loop gains are " + str(loopGains))
    print("Loop paths are " + str(loopPaths))

    for independentLoops_index in range(len(delta_I)):
        print("Delta I, Loops dependent upon Forward Path " + str(independentLoops_index+1) + ": " + str(delta_I[independentLoops_index]))
    
    print("Delta " + str(delta))
    print("Mason Gain Formula: " + str(masonGain))