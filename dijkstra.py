import pygame
from queue import PriorityQueue
import sys

DISPLAY_SIZE = 800
NUMBER_OF_ROWS = 40
display = pygame.display.set_mode((DISPLAY_SIZE, DISPLAY_SIZE))
pygame.display.set_caption("Pathfinding visualizer (Dijkstra's algorithm)")

# colours from https://www.webucator.com/blog/2015/03/python-color-constants-module/
VIOLETRED = (208,32,144)
VIOLETRED4 = (139,34,82)
DEEPSKYBLUE3 = (0,154,205)
DEEPSKYBLUE4 = (0,104,139)
SNOW3 = (205,201,201)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

class Node:
	# Node constructor
	def __init__(self, row, col, blockSize):
		self.row = row
		self.col = col
		self.x = row * blockSize
		self.y = col * blockSize
		self.blockSize = blockSize
		self.colour = SNOW3

	def isNotBarrier(self):
		return self.colour != BLACK
		
	def setColour(self, colour):
		self.colour = colour
	
	def isNotDefaultColour(self):
		return self.colour != SNOW3
	
	# we will only redraw the node (not the whole display)
	def drawNode(self, display):
		rect = pygame.Rect(self.x, self.y, self.blockSize, self.blockSize)
		pygame.draw.rect(display, self.colour, rect)
		pygame.draw.rect(display, BLACK, rect, 1)
		pygame.display.update(rect)
	
	# basic defintion to compare nodes (ie. just return True)
	def __lt__(self, other):
		return True

def makeGrid(display, size, numRows):
	grid = []
	blockSize = size // numRows
	for i in range(numRows):
		grid.append([])
		for j in range(numRows):
			node = Node(i, j, blockSize)
			node.drawNode(display)
			grid[i].append(node)
	return grid

def resetGrid(display, grid):
	for row in grid:
		for node in row:
			if node.isNotDefaultColour():
				node.setColour(SNOW3)
				node.drawNode(display)

def getMousePosition(position, size, numRows):
	blockSize = size // numRows
	y, x = position
	return y // blockSize, x // blockSize

def resetSearchingAnimation(display, size, startNode, endNode, grid):
	for row in grid:
		for node in row:
			if node.isNotDefaultColour() and node.isNotBarrier() and node is not startNode and node is not endNode:
				node.setColour(SNOW3)
				node.drawNode(display)

def dijkstrasAlgorithm(display, size, startNode, endNode, grid):
	queue = PriorityQueue()
	queue.put((0, startNode))
	previousNode = {}
	distanceOfNode = {}
	for row in grid:
		for node in row:
			distanceOfNode[node] = float("inf")
	distanceOfNode[startNode] = 0
	visited = {startNode}

	clock = pygame.time.Clock()
	while not queue.empty():
		node = queue.get()[1]
		visited.remove(node)

		if node == endNode:
			resetSearchingAnimation(display, size, startNode, endNode, grid)
			path = []
			node = previousNode[endNode]
			while node is not startNode:
				path.append(node)
				node = previousNode[node]
			path = list(reversed(path))
			return path

		listOfNeighbours = []
		# up
		if node.row - 1 >= 0 and grid[node.row - 1][node.col].isNotBarrier():
			listOfNeighbours.append(grid[node.row - 1][node.col])
		# down
		if node.row + 1 < NUMBER_OF_ROWS and grid[node.row + 1][node.col].isNotBarrier():
			listOfNeighbours.append(grid[node.row + 1][node.col])
		# left
		if node.col - 1 >=  0 and grid[node.row][node.col - 1].isNotBarrier():
			listOfNeighbours.append(grid[node.row][node.col - 1])
		# right
		if node.col + 1 < NUMBER_OF_ROWS and grid[node.row][node.col + 1].isNotBarrier():
			listOfNeighbours.append(grid[node.row][node.col + 1])

		for neighbour in listOfNeighbours:
			distance = distanceOfNode[node] + 1
			if (distance < distanceOfNode[neighbour]):
				previousNode[neighbour] = node
				distanceOfNode[neighbour] = distance
				if neighbour not in visited:
					queue.put((distance, neighbour))
					visited.add(neighbour)
					if neighbour is not endNode:
						neighbour.setColour(DEEPSKYBLUE4)
						neighbour.drawNode(display)
		if node is not startNode:
			node.setColour(DEEPSKYBLUE3)
			node.drawNode(display)

		clock.tick(60)

def drawPath(display, size, grid, path, colour, animationTime):
	for node in path:
		node.setColour(colour)
		node.drawNode(display)
		pygame.time.wait(animationTime)

def main(display, size, numRows):
	pygame.init()
	grid = makeGrid(display, size, numRows)
	startNode = None
	endNode = None
	path = []
	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():

			# check if the user exits the pygame display
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# check if the user clicks enter key
			if event.type == pygame.KEYDOWN:

				# start finding the path
				if event.key == pygame.K_RETURN:
					path = dijkstrasAlgorithm(display, size, startNode, endNode, grid)
					drawPath(display, size, grid, path, YELLOW, 50)

				# rewatch the animation
				elif event.key == pygame.K_p:
					drawPath(display, size, grid, path, SNOW3, 0)
					dijkstrasAlgorithm(display, size, startNode, endNode, grid)
					drawPath(display, size, grid, path, YELLOW, 50)

				# reset the display
				elif event.key == pygame.K_r:
					for row in grid:
						for node in row:
							resetGrid(display, grid)
							startNode = None
							endNode = None

			# check if the user left or right clicks the mouse
			leftClick = pygame.mouse.get_pressed()[0]
			rightClick = pygame.mouse.get_pressed()[2]
			if leftClick or rightClick:
				position = pygame.mouse.get_pos()
				row, col = getMousePosition(position, size, numRows)
				node = grid[row][col]

				# left click
				if leftClick:
					if startNode is None and node is not endNode:
						node.setColour(VIOLETRED)
						node.drawNode(display)
						startNode = node
					elif endNode is None and node is not startNode:
						node.setColour(VIOLETRED4)
						node.drawNode(display)
						endNode = node
					elif node is not startNode and node is not endNode:
						node.setColour(BLACK)
						node.drawNode(display)

				# right click
				else:
					if node is startNode:
						startNode = None
					elif node is endNode:
						endNode = None
					node.setColour(SNOW3)
					node.drawNode(display)

		clock.tick(60)

if __name__ == "__main__":
	main(display, DISPLAY_SIZE, NUMBER_OF_ROWS)
