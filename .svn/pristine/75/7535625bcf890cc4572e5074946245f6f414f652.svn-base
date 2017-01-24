# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called
by Pacman agents (in searchAgents.py).
"""

import util
import sets
import copy

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other
    maze, the sequence of moves will be incorrect, so only use this for tinyMaze
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s,s,w,s,w,w,s,w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first
    [2nd Edition: p 75, 3rd Edition: p 87]

    Your search algorithm needs to return a list of actions that reaches
    the goal.  Make sure to implement a graph search algorithm
    [2nd Edition: Fig. 3.18, 3rd Edition: Fig 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    
    visited = sets.Set()
    
    fringe = util.Stack()
    initList = [problem.getStartState(), None]
    fringe.push(initList)
    
    while not fringe.isEmpty():
        
        current = fringe.pop()
        currentXY = current[0]
        currentActions = current[1]
        
        #print currentXY
        if currentXY not in visited:
            visited.add(currentXY)
        
        #Find Successors and push to stack
        successorList = problem.getSuccessors(currentXY)
        for i in range(0, len(successorList)):
            if successorList[i][0] not in visited:
                xy = successorList[i][0]
                actions = copy.copy(currentActions)
                #print "Before if\n", actions,"\n",currentActions
                if not actions:
                    actions = [successorList[i][1]]
                else:
                    actions.append(successorList[i][1])
                #print "After if\n" ,actions,"\n" ,currentActions

                list = [xy, actions]
                
                fringe.push(list)
        
        
        
        if problem.isGoalState(currentXY):
            return currentActions
            
    
    return None
    
    util.raiseNotDefined()

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first.
    [2nd Edition: p 73, 3rd Edition: p 82]
    """
    
    visited = sets.Set()
    
    fringe = util.Queue()
    initList = [problem.getStartState(), None]
    fringe.push(initList)
    
    while not fringe.isEmpty():
        
        current = fringe.pop()
        currentXY = current[0]
        currentActions = current[1]
        
        #print currentXY
        if currentXY not in visited:
            visited.add(currentXY)
    
        #Find Successors and push to stack
        successorList = problem.getSuccessors(currentXY)
        for i in range(0, len(successorList)):
            if successorList[i][0] not in visited:
                xy = successorList[i][0]
                visited.add(xy)
                actions = copy.copy(currentActions)

                if not actions:
                    actions = [successorList[i][1]]
                else:
                    actions.append(successorList[i][1])
                
                list = [xy, actions]
                
                fringe.push(list)
        
        
        
        if problem.isGoalState(currentXY):
            return currentActions


    return None

def uniformCostSearch(problem):
    "Search the node of least total cost first. "
    
    #Create set for graph search
    visited = sets.Set()
    
    #Establish data structure and push the start state
    fringe = util.PriorityQueue()
    initList = [problem.getStartState(), None, 0]
    fringe.push(initList, 0)
    
    
    #Loop through fringe
    while not fringe.isEmpty():
        
        current = fringe.pop()
        currentXY = current[0]
        currentActions = current[1]
        currentCost = current[2]
        
        #Check for goal state
        if problem.isGoalState(currentXY):
            return currentActions
        
        if currentXY not in visited:
           visited.add(currentXY)
        
        #Find Successors and push to stack
        successorList = problem.getSuccessors(currentXY)
        for i in range(0, len(successorList)):
            if successorList[i][0] not in visited:
                
                #(x,y)
                xy = successorList[i][0]
                
                #actions
                actions = copy.copy(currentActions)
                if actions is None:
                    actions = [successorList[i][1]]
                else:
                    actions.append(successorList[i][1])
                
                #cost
                cost = currentCost + successorList[i][2]
                
                #package and push
                list = [xy, actions, cost]
                fringe.push(list, cost)


    return None

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    "Search the node that has the lowest combined cost and heuristic first."
    
    #Create set for graph search
    visited = sets.Set()
    
    #Establish data structure and push the start state
    fringe = util.PriorityQueue()
    initList = [problem.getStartState(), None, 0]
    fringe.push(initList, 0)
    
    
    #Loop through fringe
    while not fringe.isEmpty():
        
        current = fringe.pop()
        currentState = current[0]
        currentActions = current[1]
        currentCost = current[2]
        
        #Check for goal state
        if problem.isGoalState(currentState):
            return currentActions
        
        if currentState not in visited:
            visited.add(currentState)
        
        #Find Successors and push to stack
        successorList = problem.getSuccessors(currentState)
        for i in range(0, len(successorList)):
            if successorList[i][0] not in visited:
                
                #(x,y)
                xy = successorList[i][0]
                
                #actions
                actions = copy.copy(currentActions)
                if actions is None:
                    actions = [successorList[i][1]]
                else:
                    actions.append(successorList[i][1])
                
                #cost
                cost = currentCost + successorList[i][2]
                costAndHeuristic = heuristic(xy, problem) + cost
              
                #package and push
                list = [xy, actions, cost]
                fringe.push(list, costAndHeuristic)


    return None


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
