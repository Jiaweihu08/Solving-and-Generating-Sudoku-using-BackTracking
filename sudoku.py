import pygame, sys
from random import randint, choice, shuffle
from copy import deepcopy
from time import sleep


pygame.init()

width = 450
cell_size = width // 9

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 60, 0)

cell_states_color = {'fixed': BLACK, 'pending': BLUE, 'calculating': ORANGE}

font = pygame.font.SysFont('Verdana', 20)


class Cell:
	def __init__(self, x, y, size=cell_size):
		self.x = x
		self.y = y
		self.size = size

		self.i = x * size
		self.j = y * size
		self.num = 0

		self.selected = False
		self.state = None
		self.define_lines()

	def define_lines(self):
		p1 = (self.i, self.j)
		p2 = (self.i + self.size, self.j)
		p3 = (self.i + self.size, self.j + self.size)
		p4 = (self.i, self.j + self.size)

		self.lines = [p1, p2, p3, p4]

	def set_state(self):
		if self.num == 0:
			self.state = 'pending'
		else:
			self.state = 'fixed'

	def update_val(self, num):
		if self.state != 'fixed':
			self.num = num

	def draw(self, scree):
		if self.selected or self.state == 'calculating':
			pygame.draw.lines(screen, BLACK, True, self.lines, 2)

		color = cell_states_color[self.state]

		surface = font.render(str(self.num), True, color)
		screen.blit(surface, (self.i + self.size//3, self.j+self.size//3))

	def __repr__(self):
		return str(self.num)


def is_possible(grid, x, y, n):
	""" Check if a given number n is possible at positive x and y
	with the current configuration of the grid
	"""
	for i in range(9):
		if grid[i][y].num == n:
			return False

	for j in range(9):
		if grid[x][j].num == n:
			return False

	x0 = (x // 3) * 3
	y0 = (y // 3) * 3
	for i in range(3):
		for j in range(3):
			if grid[x0 + i][y0 + j].num == n:
				return False
	return True


def solve_sudoku(grid, x0=0, draw=None):
	"""Main function for solving the puzzle.
	It finds the first empty spot and solves it using
	backtracking.
	"""
	x, y = get_empty_spot(grid, x0)
	return solve_curr_spot(grid, x, y, draw=draw)


def get_empty_spot(grid, x0):
	"""Fin the next empty spot.
	"""
	for x in range(x0, 9):
		for y in range(9):
			if grid[x][y].num == 0:
				return x, y
	return None, None


def solve_curr_spot(grid, x, y, nums=range(1, 10), draw=None):
	"""Function used to find the correct value
	for the grid at x and y. It iteratively tries different
	values in num.
	Cell states are modified accordingly for visualization purposes.
	"""
	if x == None:
		return True, grid

	cell = grid[x][y]
	for n in nums:
		if is_possible(grid, x, y, n):
			cell.num = n
			cell.state = 'calculating'
			if draw:
				draw()
			solved, grid = solve_sudoku(grid, x, draw=draw)
			if solved:
				cell.state = 'fixed'
				return True, grid
			cell.num = 0
			cell.state = 'pending'
	return False, grid


def initialize_full_grid():
	"""Function to return a solved sudoku generated 'randomly'
	It first generates an empty grid, and assigns shuffled values
	to a row.
	This grid is then solved using backtracking.
	"""
	grid = []
	spots = []
	for x in range(9):
		row = []
		for y in range(9):
			row.append(Cell(x, y))
			spots.append((x, y))
		grid.append(row)

	rand_nums = list(range(1, 10))
	shuffle(rand_nums)
	row = grid[randint(0, 8)]

	for n, cell in zip(rand_nums, row):
		cell.num = n
	
	_, grid = solve_sudoku(grid)

	return grid, spots


def is_irreplaceable(grid, x_, y_):
	"""For puzzle generation, the function is used to check
	wether the value for the current position is the only value
	possible by first removing the current value and tries to solve
	the resulting puzzle with all other values.
	"""
	curr_val = grid[x_][y_].num
	grid[x_][y_].num = 0

	nums = list(range(1, 10))
	nums.remove(curr_val)

	solved, _ = solve_curr_spot(grid, x_, y_, nums)
	if solved:
		return False
	return True


def generate():
	"""Function for puzzle generation
	"""
	grid, spots = initialize_full_grid()
	solution = deepcopy(grid)

	num_remaining_spots = randint(30, 40)

	while len(spots) > num_remaining_spots:
		x_, y_ = choice(spots)
		if is_irreplaceable(deepcopy(grid), x_, y_):
			spots.remove((x_, y_))
			grid[x_][y_].num = 0

	return grid, solution


def get_clicked_pos(pos):
	x, y = pos
	i, j = x // cell_size, y // cell_size
	return i, j


def draw_lines(screen):
	hline_1 = ((0, 3 * cell_size), (width, 3 * cell_size))
	hline_2 = ((0, 6 * cell_size), (width, 6 * cell_size))

	vline_1 = ((3 * cell_size, 0), (3 * cell_size, width))
	vline_2 = ((6 * cell_size, 0), (6 * cell_size, width))

	for line in [hline_1, hline_2, vline_1, vline_2]:
		pygame.draw.line(screen, BLACK, *line, 2)


def draw(grid, screen, speed=None):
	screen.fill(WHITE)
	draw_lines(screen)
	for row in grid:
		for cell in row:
			cell.draw(screen)
	if speed != None:
		sleep(speed)
	pygame.display.update()


def main(screen):
	pygame.display.set_caption('Backtracking for Sudoku solving and generation')
	grid, solution = generate()

	for row in grid:
		for cell in row:
			cell.set_state()

	
	selected_cell = None

	while True:
		draw(grid, screen)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				i, j = get_clicked_pos(pos)
				cell = grid[i][j]
				if selected_cell != None:
					if selected_cell == cell:
						cell.selected = False
						selected_cell = None
					else:
						selected_cell.selected = False
						selected_cell = cell
						cell.selected = True
				else:
					cell.selected = True
					selected_cell = cell


			if event.type == pygame.KEYDOWN:
				if selected_cell != None:
					key = pygame.key.name(event.key)
					if key.isdigit() and is_possible(grid, selected_cell.x, selected_cell.y, int(key)) or key == '0':
						selected_cell.update_val(key)
						selected_cell.selected = False
						selected_cell = None


				elif event.key == pygame.K_SPACE:
					pygame.display.set_caption('Using Backtracking to Solve the Puzzle')
					for row in grid:
						for cell in row:
							cell.update_val(0)
					solved, grid = solve_sudoku(grid, draw=lambda: draw(grid, screen, 0.2))
					pygame.display.set_caption('Solved!!')


				elif event.key == pygame.K_g:
					pygame.display.set_caption('Backtracking for Sudoku solving and generation')
					grid, solution = generate()
					for row in grid:
						for cell in row:
							cell.set_state()


				elif event.key == pygame.K_RETURN:
					solved = False
					for i in range(9):
						if solved == True:
							break
						for j in range(9):
							if grid[i][j].num != solution[i][j].num:
								pygame.display.set_caption("There's an error, try again")
								solved = True
								break

					if solved == False:
						pygame.display.set_caption('You made it!!!')
						grid, solution = generate()
						for row in grid:
							for cell in row:
								cell.set_state()

					
if __name__ == '__main__':
	screen = pygame.display.set_mode((width, width))
	main(screen)

