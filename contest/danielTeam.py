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
import game
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

    # print self.distancer.isReadyForMazeDistance()
    # print self.display

    # print self.debugDraw(cells=, color=, clear=False)
    # print self.debugClear()

    # To show belief, for debugging
    # print self.displayDistributionsOverPositions()

    # Forget observations
    # print self.final()
    # print self.getCurrentObservation()
    # print self.getPreviousObservation()

    self.walls = gameState.getWalls()
    self.legalPositions = [p for p in self.walls.asList(False) if p[1] > 0]
    self.babies = self.getFoodYouAreDefending(gameState).asList()
    self.eaten = []
    self.beliefs = [util.Counter(), util.Counter(), util.Counter(), util.Counter()]
    self.isPacman = [gameState.getAgentState(i).isPacman for i in range(gameState.getNumAgents())]
    
    if self.red:
      self.opponentZeroPos = [(30, 14), (30, 13), (30, 12)]
      c = 0
      for idx in self.getOpponents(gameState):
        self.beliefs[idx][(30, 13 + c)] = 1
        c += 1
    else:
      self.opponentZeroPos = [(1, 1), (1, 2), (1, 3)]
      c = 1
      for idx in self.getOpponents(gameState):
        self.beliefs[idx][(1, 1 + c)] = 1
        c -= 1

    # for idx in self.getOpponents(gameState):
    #   self.setOpponentToZeroPos(idx)

    # print self.getAction(gameState)
    # print self.getCapsules(gameState)
    # print self.getCapsulesYouAreDefending(gameState)
    # print self.getFood(gameState).asList()
    # print self.getFoodYouAreDefending(gameState).asList()
    # print self.getOpponents(gameState)
    # print self.getTeam(gameState)
    # print self.getScore(gameState)
    # print gameState

    # print self.getWeights(gameState)
    # print self.getFeatures(gameState)

  def setOpponentToZeroPos(self, idx):
    self.beliefs[idx] = util.Counter()
    for pos in self.opponentZeroPos:
      self.beliefs[idx][pos] = 1.0 / len(self.opponentZeroPos)

  def initializeBeliefsUniformly(self, gameState, idx):
    self.beliefs[idx] = util.Counter()
    for p in self.legalPositions:
      self.beliefs[idx][p] = 1.0
    self.beliefs[idx].normalize()

  def setBeliefs(self, position, idx):
    self.beliefs[idx] = util.Counter()
    self.beliefs[idx][position] = 1.0

  def observe(self, observation, gameState, myPosition, idx):
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
    if not noZero:
      self.initializeBeliefsUniformly(gameState, idx)
    self.beliefs[idx].normalize()

  def elapseTime(self, idx):
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
    #TODO: Use get walls to make more efficient (we just check if pos is True)
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

  def trackGhosts(self, gameState):
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    noisyDistances = gameState.getAgentDistances()
    if len(noisyDistances) != gameState.getNumAgents():
      print "noisyDistances are unknown ({}), setting beliefs uniformly".format(noisyDistances)
      for idx in self.getOpponents(gameState):
        self.initializeBeliefsUniformly(gameState, idx)
      return

    opponentFound = [False] * 4
    for idx in self.getOpponents(gameState):
      #TODO better predict movement
      #TODO we know we should see them if they are closer than 5, if we dont see them, they are further
      pos = gameState.getAgentState(idx).getPosition()
      if pos is not None:
        # If we are close to opponents (we see them), update beliefs to one point
        self.setBeliefs(pos, idx)
        opponentFound[idx] = True
      # If the teammate has eaten a ghost, update belief to initial position
      elif self.updateEatenOpponents1(gameState, idx):
        opponentFound[idx] = True
        print "Teammate has eaten pacman"
      else:
        # If not, update beliefs
        self.elapseTime(idx)
        # If opponent has changed from ghost to pacman (and haven't died), we know their x coordinate
        if self.isPacman[idx] != gameState.getAgentState(idx).isPacman:
          print "Cambio Inesperado!"
          if self.red:
            pacman_land = 15
            ghost_land = 16
          else:
            pacman_land = 16
            ghost_land = 15
          if self.isPacman[idx]: # Was pacman, now is ghost
            for pos in self.beliefs[idx].keys():
              if pos[0] != ghost_land:
                self.beliefs[idx].pop(pos, None)
          else: # Was ghost, now is pacman
            for pos in self.beliefs[idx].keys():
              if pos[0] != pacman_land:
                self.beliefs[idx].pop(pos, None)
          self.beliefs[idx].normalize()
        # Remove impossible positions because we should see the opponents from there
        pos0 = gameState.getAgentState(self.getTeam(gameState)[0]).getPosition()
        pos1 = gameState.getAgentState(self.getTeam(gameState)[1]).getPosition()
        for p in self.beliefs[idx].keys():
          if (pos0 is not None and util.manhattanDistance(p, pos0) < 5) or (pos1 is not None and util.manhattanDistance(p, pos1) < 5):
            self.beliefs[idx].pop(p, None)
    # Calculate opponents that could have eaten the missing food
    eaters = [[], []]
    for i, pos in enumerate(self.eaten):
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
              self.setBeliefs(self.eaten[0], idx)
            else:
              newBelief = False
          else: #1 || 2
            if eaters[0][0] == idx:
              self.setBeliefs(self.eaten[0], idx)
            else:
              self.setBeliefs(self.eaten[1], idx)
        elif len(eaters[1]) == 1:
          newBelief = True
          if len(eaters[0]) == 2:
            if eaters[1][0] == idx:
              self.setBeliefs(self.eaten[1], idx)
            else:
              self.setBeliefs(self.eaten[0], idx)
          else: # 0
            if eaters[1][0] == idx:
              self.setBeliefs(self.eaten[1], idx)
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
          beliefs[idx][p] = 1 #self.beliefs[idx][p]
          # beliefs[idx][p] = self.beliefs[idx][p]

    self.displayDistributionsOverPositions(beliefs)

  def getEatenFood(self, gameState):
    self.eaten = []
    newFood = self.getFoodYouAreDefending(gameState)
    for pos in self.babies:
      if not newFood[pos[0]][pos[1]]:
        self.eaten.append(pos)

  def updateEatenOpponents1(self, gameState, idx):
    teammatePos = gameState.getAgentState((self.index + 2) % 4).getPosition()
    pos = gameState.getAgentState(idx).getPosition()
    # We assume that all beliefs that are zero are removed from self.beliefs
    if pos is None and len(self.beliefs[idx]) == 1 and self.beliefs[idx].keys()[0] == teammatePos:
      self.setOpponentToZeroPos(idx)
      return True
    return False

  def updateEatenOpponents2(self, gameState, chosenAction):
    myNewPos = self.getSuccessor(gameState, chosenAction).getAgentState(self.index).getPosition()
    teammatePos = gameState.getAgentState((self.index + 2) % 4).getPosition()
    for idx in self.getOpponents(gameState):
      pos = gameState.getAgentState(idx).getPosition()
      if pos is not None and pos == myNewPos:
        self.setOpponentToZeroPos(idx)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    myState = gameState.getAgentState(self.index)
    self.getEatenFood(gameState)
    self.trackGhosts(gameState)
    # Update food eaten by opponents
    self.babies = self.getFoodYouAreDefending(gameState).asList()
    # myPos = myState.getPosition()
    # noisyDistances = gameState.getAgentDistances()



    # for idx in self.getOpponents(gameState):
    #   state = gameState.getAgentState(idx)
    #   print idx
    #   print state.getPosition()
    #   print "Position: "
    #   if state.getPosition() is None:
    #     print None
    #   else:
    #     print distanceCalculator.manhattanDistance(myPos, state.getPosition())
    #   print "NoisyDistance: "
    #   if len(noisyDistances) == 4:
    #     print noisyDistances[idx]
    #   else:
    #     print None
    # print "<<<<"
    # print self.index
    # print myPos
    # print myState
    # print gameState.getAgentDistances()
    # self.getTeam(gameState)
    # self.getOpponents(gameState)
    # print "-------------------"

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
    # Update isPacman
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

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True, but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

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
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
