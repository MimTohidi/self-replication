import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Cell:
    def __init__(self, x, y, state=1.0, replication_rules=None):

        self.x = x
        self.y = y
        self.age = 0
        self.state = state 
        self.division_age = random.randint(1, 3) 
        self.replication_rules = replication_rules or {
            "growth_factor": 0.1,
            "decay_factor": 0.05
        }

    def ready_divide(self):
        return self.age >= self.division_age and self.state > 0.5

    def divide(self, environment, shape_mask):
        
        new_positions = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1)
        ]
        random.shuffle(new_positions)  
        
        for pos in new_positions:
            if environment.is_within_shape(*pos, shape_mask) and environment.is_empty(*pos):
                mutated_rules = {
                    "growth_factor": self.replication_rules["growth_factor"] + random.uniform(-0.01, 0.01),
                    "decay_factor": self.replication_rules["decay_factor"] + random.uniform(-0.01, 0.01)
                }
                new_cell = Cell(*pos, replication_rules=mutated_rules)
                environment.add_cell(new_cell)
                break

    def update(self, environment, shape_mask):
        self.age += 1
        neighbors = environment.get_neighbor_state_sum(self.x, self.y)
        self.state += self.replication_rules["growth_factor"] * neighbors * (1 - self.state)
        self.state -= self.replication_rules["decay_factor"] * self.state
        self.state = max(0, min(1, self.state))  

        if self.ready_divide():
            self.divide(environment, shape_mask)
            self.age = 0  

class Environment:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.cells = []

    def is_empty(self, x, y):
        for cell in self.cells:
            if cell.x == x and cell.y == y:
                return False
        return True

    def is_within_shape(self, x, y, shape_mask):
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return shape_mask[y][x] == 1
        return False

    def add_cell(self, cell):
        self.cells.append(cell)

    def update(self, shape_mask):
        cells_copy = self.cells[:]
        for cell in cells_copy:
            cell.update(self, shape_mask)

    def get_neighbor_state_sum(self, x, y):
        neighbors = [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ]
        total_state = 0
        for nx, ny in neighbors:
            for cell in self.cells:
                if cell.x == nx and cell.y == ny:
                    total_state += cell.state
        return total_state

    def get_cell_positions_and_states(self):
        positions = [(cell.x, cell.y) for cell in self.cells]
        states = [cell.state for cell in self.cells]
        return positions, states


def create_shape_mask(grid_size):
    mask = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    center = grid_size // 2
    for y in range(grid_size):
        for x in range(grid_size):
            if abs(x - center) + abs(y - center) <= grid_size // 3:
                mask[y][x] = 1
    return mask

def simulate(steps, grid_size):
    env = Environment(grid_size)
    shape_mask = create_shape_mask(grid_size)

    start_cell = Cell(grid_size // 2, grid_size // 2)
    env.add_cell(start_cell)

    fig, ax = plt.subplots(figsize=(6, 6))
    ims = []

    for step in range(steps):
        env.update(shape_mask)
        positions, states = env.get_cell_positions_and_states()
        xs = [pos[0] for pos in positions]
        ys = [pos[1] for pos in positions]
        sizes = [state * 100 for state in states]

        im = ax.scatter(xs, ys, c='blue', s=sizes)
        ims.append([im])

        ax.set_xlim(-1, grid_size)
        ax.set_ylim(-1, grid_size)
        ax.set_title(f"Step {step}")
        ax.set_xticks([])
        ax.set_yticks([])

    ani = animation.ArtistAnimation(fig, ims, interval=200, blit=True, repeat_delay=1000)
    plt.show()

simulate(500, 30)