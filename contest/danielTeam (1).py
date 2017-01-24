# danielTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent1', second = 'DefensiveAgent1'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class CaptureAgent1(CaptureAgent):
  """
  My first agent
  """
  def registerInitialState(self, gameState):
    # super(CaptureAgent1, self).registerInitialState(gameState)
    self.red = gameState.isOnRedTeam(self.index)
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()

    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display

    self.walls = gameState.getWalls()
    self.legalPositions = [p for p in self.walls.asList(False) if p[1] > 0]
    self.babies = self.getFoodYouAreDefending(gameState).asList()
    self.beliefs = [util.Counter(), util.Counter(), util.Counter(), util.Counter()]
    self.isPacman = [gameState.getAgentState(i).isPacman for i in range(gameState.getNumAgents())]

    # Initialize zero position of the opponents, beliefs of the opponents and pacman_land - ghost_land of the opponents
    if self.red:
      self.opponentZeroPos = [(30, 14), (30, 13), (30, 12)]
      c = 0
      for idx in self.getOpponents(gameState):
        self.beliefs[idx][(30, 13 + c)] = 1
        c += 1
      self.pacman_land = 15
      self.ghost_land = 16
      self.going_left = -1
    else:
      self.opponentZeroPos = [(1, 1), (1, 2), (1, 3)]
      c = 1
      for idx in self.getOpponents(gameState):
        self.beliefs[idx][(1, 1 + c)] = 1
        c -= 1
      self.pacman_land = 16
      self.ghost_land = 15
      self.going_left = 1

    self.examineMaze(gameState)

  def examineMaze(self, gameState):
    w = self.walls.width
    h = self.walls.height
    walls = self.walls.deepCopy()
    food1 = self.getFoodYouAreDefending(gameState)
    food2 = self.getFood(gameState)

    # Save map as 0, 1, 2 and 3 (0:walls, 1:spaces, 2:babies, 3:food)
    for x in range(w):
      for y in range(h):
        if walls[x][y]:
          walls[x][y] = 0
        elif food1[x][y]:
          walls[x][y] = 2
        elif food2[x][y]:
          walls[x][y] = 2
        else:
          walls[x][y] = 1

    print walls

    roomsDisplay = []
    # Detect doors and spaces. Spaces are now negative
    for x in range(w):
      for y in range(h):
        if walls[x][y] > 0:
          exitsNum = 0
          if walls[x][y - 1] != 0:
            exitsNum += 1
          if walls[x][y + 1] != 0:
            exitsNum += 1
          if walls[x - 1][y] != 0:
            exitsNum += 1
          if walls[x + 1][y] != 0:
            exitsNum += 1
          if exitsNum == 1 or exitsNum == 2:
            walls[x][y] = -1 * walls[x][y]
            roomsDisplay.append((x, y))
          elif exitsNum == 0:
            # We erase unaccessible cells
            walls[x][y] = 0
          else:
            # These are doors or big rooms, we leave them positive
            pass

    print walls

    # bigRooms = []
    # # Detect big rooms
    # for x in range(w):
    #   for y in range(h):
    #     if walls[x][y] != 0:
    #       # Look for squares
    #       if walls[x - 1][y - 1] != 0 and walls[x][y - 1] != 0 and walls[x - 1][y] != 0:
    #         myRoom = -1
    #         for i, room in enumerate(bigRooms):
    #           if ((x, y) in room or (x - 1, y) in room or (x, y - 1) in room or (x - 1, y - 1) in room):
    #             myRoom = i
    #             break
    #         if myRoom < 0:
    #           bigRooms.append([(x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)])
    #         else:
    #           if (x, y) not in bigRooms[myRoom]:
    #             bigRooms[myRoom].append((x, y))
    #           if (x - 1, y) not in bigRooms[myRoom]:
    #             bigRooms[myRoom].append((x - 1, y))
    #           if (x, y - 1) not in bigRooms[myRoom]:
    #             bigRooms[myRoom].append((x, y - 1))
    #           if (x - 1, y - 1) not in bigRooms[myRoom]:
    #             bigRooms[myRoom].append((x - 1, y - 1))
    #
    # # Remove doors from big rooms
    # doorsBigRooms = []
    # for room in bigRooms:
    #   doors = []
    #   for cell in room:
    #     if ((cell[0] + 1, cell[1]) not in room and walls[cell[0] + 1][cell[1]] != 0) \
    #             or ((cell[0] - 1, cell[1]) not in room and walls[cell[0] - 1][cell[1]] != 0) \
    #             or ((cell[0], cell[1] + 1) not in room and walls[cell[0]][cell[1] + 1] != 0) \
    #             or ((cell[0], cell[1] - 1) not in room and walls[cell[0]][cell[1] - 1] != 0):
    #       doors.append(cell)
    #   for door in doors:
    #     room.remove(door)
    #   doorsBigRooms.append(doors)
    #
    # # Show big rooms
    bigRoomOneLine = []
    # for i in bigRooms:
    #   for j in i:
    #     bigRoomOneLine.append(j)

    # Create roomsGraph: every room has a number, some cells and some doors
    roomsGraph = []
    doorsGraph = []
    # # Add big rooms
    # for i, room in enumerate(bigRooms):
    #   foodRoom = 0
    #   for cell in room:
    #     walls[cell[0]][cell[1]] = -abs(walls[cell[0]][cell[1]])
    #     foodRoom += -(walls[cell[0]][cell[1]]) - 1
    #   graphNode = {"path": room, "doors": [], "food": foodRoom, "isBig": True}
    #   for doorPos in doorsBigRooms[i]:
    #     if [doorPos, []] not in doorsGraph:
    #       graphNode["doors"].append(len(doorsGraph))
    #       doorsGraph.append([doorPos, []])
    #     else:
    #       graphNode["doors"].append(doorsGraph.index([doorPos, []]))
    #   roomsGraph.append(graphNode)
    for x in range(1, w - 1):
      for y in range(1, h - 1):
        if (x, y) in bigRoomOneLine:
          pass
        elif walls[x][y] < 0:
          spacesNum = 0
          if walls[x][y - 1] < 0:
            spacesNum += 1
          if walls[x][y + 1] < 0:
            spacesNum += 1
          if walls[x - 1][y] < 0:
            spacesNum += 1
          if walls[x + 1][y] < 0:
            spacesNum += 1
          if spacesNum < 2:
            endOfPath = False
            graphNode = {"path": [], "doors": [], "food": 0, "isBig": False}
            auxx = x
            auxy = y
            while not endOfPath:
              graphNode["path"].append((x, y))
              graphNode["food"] += -walls[x][y] - 1
              walls[x][y] = 0
              xx = x
              yy = y
              if walls[x][y - 1] < 0:
                yy = y - 1
              elif walls[x][y + 1] < 0:
                yy = y + 1
              elif walls[x - 1][y] < 0:
                xx = x - 1
              elif walls[x + 1][y] < 0:
                xx = x + 1
              else:
                endOfPath = True
              if walls[x][y - 1] > 0:
                if [(x, y - 1), []] not in doorsGraph:
                  graphNode["doors"].append(len(doorsGraph))
                  doorsGraph.append([(x, y - 1), []])
                else:
                  graphNode["doors"].append(doorsGraph.index([(x, y - 1), []]))
              if walls[x][y + 1] > 0:
                if [(x, y + 1), []] not in doorsGraph:
                  graphNode["doors"].append(len(doorsGraph))
                  doorsGraph.append([(x, y + 1), []])
                else:
                  graphNode["doors"].append(doorsGraph.index([(x, y + 1), []]))
              if walls[x - 1][y] > 0:
                if [(x - 1, y), []] not in doorsGraph:
                  graphNode["doors"].append(len(doorsGraph))
                  doorsGraph.append([(x - 1, y), []])
                else:
                  graphNode["doors"].append(doorsGraph.index([(x - 1, y), []]))
              if walls[x + 1][y] > 0:
                if [(x + 1, y), []] not in doorsGraph:
                  graphNode["doors"].append(len(doorsGraph))
                  doorsGraph.append([(x + 1, y), []])
                else:
                  graphNode["doors"].append(doorsGraph.index([(x + 1, y), []]))
              x = xx
              y = yy
            roomsGraph.append(graphNode)
            x = auxx
            y = auxy

    # Create doorsGraph: every door has a number, and goes to other rooms
    for j, door in enumerate(doorsGraph):
      for i, room in enumerate(roomsGraph):
        for aDoor in room["doors"]:
          if aDoor == j:
            doorsGraph[j][1] = doorsGraph[j][1] + [i]

    # Create doorsDistance: maps what foors can be accessed from other doors
    doorsDistance = []
    print
    for dist in doorsDistance:
      print dist
    for i, door in enumerate(doorsGraph):
      doorsRow = [None] * len(doorsGraph)
      for room in door[1]:
        for neighborDoor in roomsGraph[room]["doors"]:
          if neighborDoor != i:
            doorsRow[neighborDoor] = [roomsGraph[room]["food"], len(roomsGraph[room]["path"])]
      doorsDistance.append(doorsRow)

    # Create self variables
    self.doorsGraph = doorsGraph
    self.roomsGraph = roomsGraph
    self.doorsDistance = doorsDistance

    # print
    # for room in self.roomsGraph:
    #   print room
    # print
    # for door in self.doorsGraph:
    #   print door
    # print
    # for dist in self.doorsDistance:
    #   print dist

    # Show every room
    roomsCounter = [util.Counter(), util.Counter(), util.Counter()]
    for room in roomsGraph:
      for p in room["path"]:
        roomsCounter[0][p] = 1
      # print room
      # print room["path"]
      # print room["doors"]
      # print room["food"]
      # print room["isBig"]
      # raw_input("Press Enter to continue ...")
      # break

    # Show every door
    for door in doorsGraph:
      oneLineRoom = []
      roomsCounter[1][door[0]] = 1
      for i in door[1]:
        oneLineRoom = oneLineRoom + roomsGraph[i]["path"]
      # print oneLineRoom
      # raw_input("Press Enter to continue ...")

    self.displayDistributionsOverPositions(roomsCounter)
    raw_input("Press Enter to continue ...")

  def getBeliefsCentroid(self, idx):
    """
    Get centroid (average point) of beliefs for an opponent
    """
    x = 0.0
    y = 0.0
    total = 0.0
    for p in self.beliefs[idx]:
      x += p[0]
      y += p[1]
      total += 1.0
    return (round(x / total), round(y / total))

  def setOpponentToZeroPos(self, idx):
    """
    The opponent died, update its belief to its starting position
    """
    self.beliefs[idx] = util.Counter()
    for pos in self.opponentZeroPos:
      self.beliefs[idx][pos] = 1.0 / len(self.opponentZeroPos)

  def initializeBeliefsUniformly(self, gameState, idx):
    """
    Set all legal positions with equal probability
    """
    self.beliefs[idx] = util.Counter()
    for p in self.legalPositions:
      self.beliefs[idx][p] = 1.0
    self.beliefs[idx].normalize()

  def setBeliefs(self, position, idx):
    """
    Set beliefs of one opponent to one single position
    """
    self.beliefs[idx] = util.Counter()
    self.beliefs[idx][position] = 1.0

  def observe(self, observation, gameState, myPosition, idx):
    """
    Observe noisy distance for opponent and update beliefs according to them
    """
    noisyDistance = observation
    noZero = False
    for p in self.legalPositions:
      if self.beliefs[idx][p] <= 0:
        self.beliefs[idx].pop(p, None)
        continue
      trueDistance = util.manhattanDistance(p, myPosition)
      prob = gameState.getDistanceProb(trueDistance, noisyDistance)
      if prob > 0:
        self.beliefs[idx][p] *= prob
        noZero = True
      else:
        self.beliefs[idx].pop(p, None)
    if not noZero:
      self.initializeBeliefsUniformly(gameState, idx)
    self.beliefs[idx].normalize()

  def elapseTime(self, idx):
    """
    Update beliefs knowing that the opponent has mad a move
    """
    newBeliefs = util.Counter()
    for oldPos in self.legalPositions:
      if self.beliefs[idx][oldPos] <= 0:
        continue
      newPosDist = self.getPositionDistribution(oldPos)
      for newPos, prob in newPosDist.items():
        newBeliefs[newPos] += prob * self.beliefs[idx][oldPos]
    newBeliefs.normalize()
    self.beliefs[idx] = newBeliefs

  def getPositionDistribution(self, position):
    """
    From a position, return all the possible new positions after a move of the opponent with an
    equal probability distribution
    """
    dist = util.Counter()
    (x, y) = position
    total = 1.0
    dist[position] = 1.0

    if not self.walls[x + 1][y]:
      dist[(x + 1, y)] = 1.0
      total += 1.0
    if not self.walls[x - 1][y]:
      dist[(x - 1, y)] = 1.0
      total += 1.0
    if not self.walls[x][y + 1]:
      dist[(x, y + 1)] = 1.0
      total += 1.0
    if not self.walls[x][y - 1]:
      dist[(x, y - 1)] = 1.0
      total += 1.0
    dist[(x, y)] /= total
    if (x + 1, y) in dist.keys():
      dist[(x + 1, y)] /= total
    if (x - 1, y) in dist.keys():
      dist[(x - 1, y)] /= total
    if (x, y+ 1) in dist.keys():
      dist[(x, y + 1)] /= total
    if (x, y - 1) in dist.keys():
      dist[(x, y - 1)] /= total
    return dist

  def getEatenBabies(self, gameState):
    """
    Get the positions of the babies (the food we are protecting) that are gone (aka have been eaten by the opponent)
    and save them in eaten
    """
    eaten = []
    newFood = self.getFoodYouAreDefending(gameState)
    for pos in self.babies:
      if not newFood[pos[0]][pos[1]]:
        eaten.append(pos)
    return eaten

  def updateEatenOpponents1(self, gameState, idx):
    """
    Detect if teammate has eaten an opponent, and update beliefs accordingly
    """
    teammatePos = gameState.getAgentState((self.index + 2) % 4).getPosition()
    pos = gameState.getAgentState(idx).getPosition()
    if pos is None and len(self.beliefs[idx]) == 1 and self.beliefs[idx].keys()[0] == teammatePos:
      self.setOpponentToZeroPos(idx)
      return True
    return False

  def updateEatenOpponents2(self, gameState, chosenAction):
    """
    Detect if the agent has eaten an opponent after taking choseAction, and update beliefs accordingly
    """
    myNewPos = self.getSuccessor(gameState, chosenAction).getAgentState(self.index).getPosition()
    for idx in self.getOpponents(gameState):
      pos = gameState.getAgentState(idx).getPosition()
      if pos is not None and pos == myNewPos:
        self.setOpponentToZeroPos(idx)

  def trackGhosts(self, gameState):
    """
    Takes care of the beliefs of the opponents (updates our beliefs for every opponent)
    """

    # Get some values that we will use later
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    noisyDistances = gameState.getAgentDistances()
    eatenBabies = self.getEatenBabies(gameState)

    #  Track each opponent
    opponentFound = [False] * 4
    for idx in self.getOpponents(gameState):
      pos = gameState.getAgentState(idx).getPosition()

      # If we are close to opponents (we see them), update beliefs to one point
      if pos is not None:
        self.setBeliefs(pos, idx)
        opponentFound[idx] = True

      # If the teammate has eaten a ghost, update belief to initial position
      elif self.updateEatenOpponents1(gameState, idx):
        opponentFound[idx] = True
        print "Our teammate has eaten an opponent, yeah!"

      # If not, update beliefs taking into account opponents possible movements
      else:
        # elapseTime (update beliefs of opponent considering they have taken an action)
        self.elapseTime(idx)

        # If opponent has changed from ghost to pacman or viceversa (and haven't died), we know their x coordinate
        if self.isPacman[idx] != gameState.getAgentState(idx).isPacman:
          if self.isPacman[idx]: # Was pacman, now is ghost
            for pos in self.beliefs[idx].keys():
              if pos[0] != self.ghost_land:
                self.beliefs[idx].pop(pos, None)
          else: # Was ghost, now is pacman
            for pos in self.beliefs[idx].keys():
              if pos[0] != self.pacman_land:
                self.beliefs[idx].pop(pos, None)
          self.beliefs[idx].normalize()

        # Get positions of me and my teammate
        pos0 = gameState.getAgentState(self.getTeam(gameState)[0]).getPosition()
        pos1 = gameState.getAgentState(self.getTeam(gameState)[1]).getPosition()
        # Remove impossible positions
        for p in self.beliefs[idx].keys():
          # We should see the opponents from there, if we don't they are not there
          if (pos0 is not None and util.manhattanDistance(p, pos0) <= 5) or (pos1 is not None and util.manhattanDistance(p, pos1) <= 5):
            self.beliefs[idx].pop(p, None)
          # There is still a food dot there, therefore the opponent is not there
          elif self.getFoodYouAreDefending(gameState)[p[0]][p[1]]:
            self.beliefs[idx].pop(p, None)
          # Our belief says the opponent could be a ghost when it is a pacman
          elif self.isPacman[idx] and p[0] * self.going_left < self.pacman_land * self.going_left - self.going_left:
            self.beliefs[idx].pop(p, None)
          # Our belief says the opponent could be a pacman when it is a ghost
          elif not self.isPacman[idx] and p[0] * self.going_left > self.ghost_land * self.going_left + self.going_left:
            self.beliefs[idx].pop(p, None)

    # Calculate opponents that could have eaten the missing food
    eaters = [[], []]
    for i, pos in enumerate(eatenBabies):
      eater = []
      for idx in self.getOpponents(gameState):
        if opponentFound[idx]:
          continue
        if pos in self.beliefs[idx].keys() and self.beliefs[idx][pos] > 0:
          eater.append(idx)
      eaters[i] = eater
      if i > 1:
        break

    for idx in self.getOpponents(gameState):
      if not opponentFound[idx]:
        # If we are not close to opponents (we don't see them), check if only one ghost can have eaten the food
        newBelief = False
        # This dirty code just changes the ghost beliefs
        if len(eaters[0]) == 1:
          newBelief = True
          if len(eaters[1]) == 0:
            if eaters[0][0] == idx:
              self.setBeliefs(eatenBabies[0], idx)
            else:
              newBelief = False
          else: #1 || 2
            if eaters[0][0] == idx:
              self.setBeliefs(eatenBabies[0], idx)
            else:
              self.setBeliefs(eatenBabies[1], idx)
        elif len(eaters[1]) == 1:
          newBelief = True
          if len(eaters[0]) == 2:
            if eaters[1][0] == idx:
              self.setBeliefs(eatenBabies[1], idx)
            else:
              self.setBeliefs(eatenBabies[0], idx)
          else: # 0
            if eaters[1][0] == idx:
              self.setBeliefs(eatenBabies[1], idx)
            else:
              newBelief = False

        if not newBelief:
          # If we have not figured out the exact position, use noisy distance that we have
          self.observe(noisyDistances[idx], gameState, myPos, idx)

    # This is to see all the possible positions where the opponents may be, all probabilities are turned to one
    beliefs = [util.Counter(), util.Counter(), util.Counter(), util.Counter()]
    for idx, bel in enumerate(self.beliefs):
      for p in bel:
        if bel[p] > 0:
          beliefs[idx][p] = 1
          # beliefs[idx][p] = self.beliefs[idx][p]

    self.displayDistributionsOverPositions(beliefs)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    # Track opponents position
    self.trackGhosts(gameState)

    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    chosenAction = random.choice(bestActions)

    # If we are eating any ghost, update our future belief about it
    self.updateEatenOpponents2(gameState, chosenAction)
    # Update food eaten by opponents
    self.babies = self.getFoodYouAreDefending(gameState).asList()
    # Update self.isPacman
    self.isPacman = [self.getSuccessor(gameState, chosenAction).getAgentState(i).isPacman for i in range(gameState.getNumAgents())]

    return chosenAction

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def getDistanceToClosestOpponent(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    opponentIdx = self.getOpponents(gameState)
    nearest = 100
    for idx in opponentIdx:
      opponentCentroid = getBeliefsCentroid(self, idx)
      nearest = min(nearest, getMazeDistance(myPos, opponentCentroid))
    return nearest




class OffensiveAgent1(CaptureAgent1):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    features['distanceToDefender'] = self.getDistanceToClosestOpponent(gameState, action)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True, but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToDefender': 1}

class DefensiveAgent1(CaptureAgent1):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['noisyDistanceToInvader'] = self.getDistanceToClosestOpponent(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    # directions = [a.getDirection() for a in enemies]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'noisyDistanceToInvader': -10}
