# L04 Implementing the schelling Model
# Coded by Zacharias Karakostas
# Username: Karakostasz
# Starting Date:11/08/2024




import random
import matplotlib.pyplot as plt
import numpy as np

class Agent:
    """
    Represents an agent in the Schelling model simulation.

    Attributes:
        type (str): The type of the agent ('R' for red, 'B' for blue).
    """
    def __init__(self, agent_type):
        """
        Initializes an agent with the specified type.

        Args:
            agent_type (str): The type of the agent ('R' or 'B').
        """
        self.type = agent_type  # Assign the type to the agent


class City:
    """
    Represents the city grid in the Schelling model simulation.

    Attributes:
        width (int): Width of the city grid.
        height (int): Height of the city grid.
        occupation_percentage (float): Proportion of the grid that is occupied.
        discr_attr_percentage (float): Proportion of red agents in the city.
        discrimination_rate (float): Threshold for agent satisfaction.
        grid (np.array): A 2D array representing the city grid.
        moved_agents (set): Tracks unique agents that have moved during the simulation.
    """
    def __init__(self, width, height, occupation_percentage, discr_attr_percentage, discrimination_rate):
        """
        Initializes the city grid with agents and vacant spaces.

        Args:
            width (int): Width of the city grid.
            height (int): Height of the city grid.
            occupation_percentage (float): Proportion of the grid that is occupied.
            discr_attr_percentage (float): Proportion of red agents in the city.
            discrimination_rate (float): Threshold for agent satisfaction.
        """
        self.width = width  # Set the grid width
        self.height = height  # Set the grid height
        self.occupation_percentage = occupation_percentage  # Set occupation percentage
        self.discr_attr_percentage = discr_attr_percentage  # Set the percentage of red agents
        self.discrimination_rate = discrimination_rate  # Set discrimination rate
        self.grid = np.full((height, width), None)  # Initialize an empty grid
        self.moved_agents = set()  # Initialize an empty set to track moved agents
        self.initialize_grid()  # Populate the grid with agents and vacant spaces

    def initialize_grid(self):
        """
        Populates the city grid with red and blue agents and vacant spaces.

        The number of agents and vacant spaces is determined by the input parameters.
        """
        total_cells = self.width * self.height  # Calculate the total number of cells
        occupied_cells = int(total_cells * self.occupation_percentage)  # Number of occupied cells
        red_agents = int(occupied_cells * self.discr_attr_percentage)  # Number of red agents
        blue_agents = occupied_cells - red_agents  # Number of blue agents
        vacant_cells = total_cells - occupied_cells  # Number of vacant cells

        # Create a list of agents and vacant spaces
        agents = [Agent('R')] * red_agents + [Agent('B')] * blue_agents + [None] * vacant_cells
        random.shuffle(agents)  # Shuffle the list for random placement

        # Populate the grid with agents and vacant spaces
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i, j] = agents.pop()

    def get_neighbors(self, x, y):
        """
        Retrieves the neighboring agents of a specified cell.

        Args:
            x (int): Row index of the cell.
            y (int): Column index of the cell.

        Returns:
            list: A list of neighboring agents or None for vacant spaces.
        """
        neighbors = []  # List to store neighbors
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonal directions
        for dx, dy in directions:
            nx, ny = x + dx, y + dy  # Calculate the coordinates of the neighbor
            if 0 <= nx < self.height and 0 <= ny < self.width:  # Check bounds
                neighbors.append(self.grid[nx, ny])  # Add neighbor to the list
        return neighbors

    def is_happy(self, x, y):
        """
        Determines if an agent is satisfied based on the similarity of its neighbors.

        Args:
            x (int): Row index of the cell.
            y (int): Column index of the cell.

        Returns:
            bool: True if the agent is happy, False otherwise.
        """
        agent = self.grid[x, y]  # Get the agent in the specified cell
        if agent is None:  # Vacant cells are always happy
            return True

        neighbors = self.get_neighbors(x, y)  # Get the list of neighbors
        similar = sum(
            1 for neighbor in neighbors if neighbor and neighbor.type == agent.type)  # Count similar neighbors
        total = sum(1 for neighbor in neighbors if neighbor)  # Count total non-vacant neighbors

        # Agents with no neighbors are considered happy
        if total == 0:
            return True

        # Ensure happiness calculation aligns with the discrimination rate
        return similar / total >= self.discrimination_rate

    def relocate_agent(self, x, y):
        """
        Moves an unhappy agent to a random vacant cell.

        Args:
            x (int): Row index of the agent.
            y (int): Column index of the agent.
        """
        vacant_cells = [(i, j) for i in range(self.height) for j in range(self.width) if self.grid[i, j] is None]
        if vacant_cells:  # Ensure there are vacant cells available
            new_x, new_y = random.choice(vacant_cells)  # Choose a random vacant cell
            self.moved_agents.add((x, y))  # Track the moved agent
            self.grid[new_x, new_y] = self.grid[x, y]  # Move the agent
            self.grid[x, y] = None  # Vacate the original cell

    def calculate_segregation(self):
        """
        Calculates the segregation level of the grid.

        Returns:
            float: The proportion of happy agents to total agents.
        """
        total_agents = 0  # Total number of agents
        happy_agents = 0  # Number of happy agents
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i, j] is not None:  # If the cell is occupied
                    total_agents += 1
                    if self.is_happy(i, j):  # Check if the agent is happy
                        happy_agents += 1
        return happy_agents / total_agents if total_agents > 0 else 1  # Return the segregation level

    def visualize(self, iteration, ax, fig, report_text=None, report=""):
        """
        Visualizes the current state of the city grid.

        Args:
            iteration (int): The current iteration of the simulation.
        """
        # Map agent types to numerical values
        color_map = {'R': 1, 'B': 2, None: 0}
        grid_numeric = np.array([[color_map[self.grid[i, j].type] if self.grid[i, j] else color_map[None]
                                  for j in range(self.width)] for i in range(self.height)])  # Create numerical grid

        # Clear the existing plot
        ax.cla()

        # Define the colormap and plot the grid
        cmap = plt.cm.colors.ListedColormap(['white', 'red', 'blue'])
        ax.imshow(grid_numeric, cmap=cmap, interpolation='none')

        # Set the title to show the current iteration
        ax.set_title(f"Iteration {iteration}", fontsize=12)

        # Remove axis ticks for better clarity
        ax.axis('off')

        # Update the report text or create a new one if it doesn't exist
        if report_text:
            report_text.set_text(report)  # Update the existing text
        else:
            report_text = fig.text(0.5, 0.01, report, ha='center', fontsize=10, wrap=True)

        return report_text

    def run_simulation(self, max_iterations):
        """
        Runs the simulation for the specified number of iterations.

        Args:
            max_iterations (int): Maximum number of iterations to simulate.
        """
        # Create the figure and axis for the visualization
        fig, ax = plt.subplots(figsize=(8, 8))

        for iteration in range(max_iterations):
            # Find all unhappy agents
            unhappy_agents = [(i, j) for i in range(self.height) for j in range(self.width)
                              if self.grid[i, j] is not None and not self.is_happy(i, j)]

            # If there are no unhappy agents, stop the simulation
            if not unhappy_agents:
                break

            # Relocate each unhappy agent
            for x, y in unhappy_agents:
                self.relocate_agent(x, y)

            # Generate the current report
            current_report = (
                f"Grid Size: {self.width}x{self.height} | "
                f"Occupation: {self.occupation_percentage:.2f} | "
                f"Discrimination Rate: {self.discrimination_rate:.2f} | "
                f"Iteration: {iteration + 1} | "
                f"Agents Moved: {len(self.moved_agents)}"
            )

            # Update the visualization with the current report
            self.visualize(iteration + 1, ax, fig, report=current_report)
            plt.pause(0.5)  # Pause to create an animation effect

        # Show the final state
        plt.show()


def generate_random_parameters():
    """
    Generates random parameters for the simulation.

    Returns:
        dict: Randomly generated parameters.
    """
    return {
        "width": random.randint(10, 50),
        "height": random.randint(10, 50),
        "occupation_percentage": round(random.uniform(0.5, 1.0), 2),
        "discr_attr_percentage": round(random.uniform(0.3, 0.7), 2),
        "discrimination_rate": round(random.uniform(0.2, 0.8), 2),
    }

def read_parameters_from_file(file_path):
    """
    Reads simulation parameters from a file.

    Args:
        file_path (str): Path to the file containing simulation parameters.

    Returns:
        dict: Parameters parsed from the file.

    Raises:
        ValueError: If the file cannot be read or has invalid formatting.
    """
    params = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':')
                params[key.strip()] = float(value.strip()) if '.' in value.strip() else int(value.strip())
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")
    return params


def print_report(width, height, occupation_percentage, discr_attr_percentage, discrimination_rate,
                 initial_segregation, final_segregation, moved_agents):
    """
    Prints the simulation report.

    Args:
        width (int): Grid width.
        height (int): Grid height.
        occupation_percentage (float): Proportion of grid that is occupied.
        discr_attr_percentage (float): Proportion of red agents.
        discrimination_rate (float): Satisfaction threshold for agents.
        initial_segregation (float): Segregation level at the start.
        final_segregation (float): Segregation level at the end.
        moved_agents (int): Total number of agents that moved during the simulation.
    """
    print("\nSimulation Report:")
    print(f"Grid size: {width} x {height}")
    print(f"Occupation percentage: {occupation_percentage}")
    print(f"Discriminating attribute percentage: {discr_attr_percentage}")
    print(f"Discrimination rate: {discrimination_rate}")
    print(f"Initial segregation level: {initial_segregation:.2f}")
    print(f"Final segregation level: {final_segregation:.2f}")
    print(f"Number of agents who moved: {moved_agents}")

def get_simulation_parameters():
    """
    Handles user input for simulation parameters.

    Prompts the user to choose between loading parameters from a file
    or generating them randomly. Reads parameters from the specified file
    or generates random parameters.

    Returns:
        dict: A dictionary containing the simulation parameters.

    Raises:
        ValueError: If an error occurs during file reading.
    """
    # Prompt the user for input method
    input_method = input("Load parameters from a file or generate randomly? (file/random): ").strip().lower()

    if input_method == "file":
        # Read parameters from a file
        file_path = input("Enter the file path: ").strip()
        try:
            params = read_parameters_from_file(file_path)
        except ValueError as e:
            raise ValueError(e)
    elif input_method == "random":
        # Generate random parameters
        params = generate_random_parameters()
        print("Randomly generated parameters:")
        for key, value in params.items():
            print(f"{key}: {value}")
    else:
        raise ValueError("Invalid input. Please choose 'file' or 'random'.")

    return params


def main():
    """
    Main function to orchestrate the simulation.

    Handles user input for parameters, initializes the simulation,
    runs the simulation, and prints the results.
    """
    # Get simulation parameters
    params = get_simulation_parameters()

    # Prompt for the number of simulation iterations
    max_iterations = int(input("Enter maximum iterations: "))

    # Initialize the city
    city = City(params["width"], params["height"], params["occupation_percentage"],
                params["discr_attr_percentage"], params["discrimination_rate"])

    # Create a figure and axis for visualization
    fig, ax = plt.subplots(figsize=(8, 8))


    # Display the initial state and calculate initial segregation
    print("Initial state:")
    city.visualize(0, ax, fig)  # Pass the `ax` object here
    initial_segregation = city.calculate_segregation()

    # Run the simulation
    city.run_simulation(max_iterations)

    # Calculate final segregation
    final_segregation = city.calculate_segregation()

    # Print the simulation report
    print_report(params["width"], params["height"], params["occupation_percentage"],
                 params["discr_attr_percentage"], params["discrimination_rate"],
                 initial_segregation, final_segregation, len(city.moved_agents))


if __name__ == "__main__":
    main()
