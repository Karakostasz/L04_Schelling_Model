# L04 Implementing the schelling Model
# Coded by Zacharias Karakostas
# Username: Karakostasz
# Starting Date:11/09/2024


import unittest
from main import City, Agent, generate_random_parameters, read_parameters_from_file

class TestSchellingModel(unittest.TestCase):

    def setUp(self):
        """
        Set up a small City instance for testing.
        """
        self.city = City(width=5, height=5, occupation_percentage=0.8,
                         discr_attr_percentage=0.5, discrimination_rate=0.4)

    def test_initialize_grid(self):
        """
        Test if the grid initializes correctly with the right number of agents and vacant spaces.
        """
        total_cells = self.city.width * self.city.height
        occupied_cells = int(total_cells * self.city.occupation_percentage)
        red_agents = int(occupied_cells * self.city.discr_attr_percentage)
        blue_agents = occupied_cells - red_agents
        vacant_cells = total_cells - occupied_cells

        red_count = sum(1 for i in range(self.city.height) for j in range(self.city.width)
                        if self.city.grid[i, j] and self.city.grid[i, j].type == 'R')
        blue_count = sum(1 for i in range(self.city.height) for j in range(self.city.width)
                         if self.city.grid[i, j] and self.city.grid[i, j].type == 'B')
        vacant_count = sum(1 for i in range(self.city.height) for j in range(self.city.width)
                           if self.city.grid[i, j] is None)

        self.assertEqual(red_count, red_agents, "Incorrect number of red agents")
        self.assertEqual(blue_count, blue_agents, "Incorrect number of blue agents")
        self.assertEqual(vacant_count, vacant_cells, "Incorrect number of vacant spaces")

    def test_get_neighbors(self):
        """
        Test if the neighbors of a cell are calculated correctly.
        """
        neighbors = self.city.get_neighbors(2, 2)  # Test a central cell
        self.assertEqual(len(neighbors), 8, "Central cell should have 8 neighbors")

        edge_neighbors = self.city.get_neighbors(0, 2)  # Test an edge cell
        self.assertEqual(len(edge_neighbors), 5, "Edge cell should have 5 neighbors")

        corner_neighbors = self.city.get_neighbors(0, 0)  # Test a corner cell
        self.assertEqual(len(corner_neighbors), 3, "Corner cell should have 3 neighbors")

    def test_is_happy(self):
        """
        Test the happiness condition for agents.
        """
        # Manually set up neighbors for testing
        self.city.grid[2, 2] = Agent('R')
        self.city.grid[1, 2] = Agent('R')
        self.city.grid[3, 2] = Agent('B')
        self.city.grid[2, 3] = None

        # Agent at (2,2) has 1 similar, 1 dissimilar, 1 vacant neighbor
        self.assertTrue(self.city.is_happy(2, 2), "Agent should be happy with current neighbors")

        # Change the discrimination rate to make the agent unhappy
        self.city.discrimination_rate = 0.8
        self.assertFalse(self.city.is_happy(2, 2), "Agent should be unhappy with higher discrimination rate")

    def test_relocate_agent(self):
        """
        Test if an unhappy agent is relocated correctly.
        """
        self.city.grid[2, 2] = Agent('R')  # Place an agent
        initial_position = (2, 2)

        # Add vacant spaces
        self.city.grid[4, 4] = None
        self.city.grid[3, 3] = None

        self.city.relocate_agent(2, 2)  # Relocate the agent
        self.assertIsNone(self.city.grid[initial_position[0], initial_position[1]],
                          "Original cell should be vacant after relocation")

    def test_calculate_segregation(self):
        """
        Test the segregation calculation for the grid.
        """
        # Perfectly segregated grid: Top-left is all 'R', bottom-right is all 'B'
        for i in range(self.city.height):
            for j in range(self.city.width):
                if i < self.city.height // 2:
                    self.city.grid[i, j] = Agent('R')
                else:
                    self.city.grid[i, j] = Agent('B')

        segregation = self.city.calculate_segregation()
        self.assertEqual(segregation, 1.0, "Segregation should be 100% for a perfectly segregated grid")

        # Mixed grid: Alternating red and blue agents
        for i in range(self.city.height):
            for j in range(self.city.width):
                self.city.grid[i, j] = Agent('R') if (i + j) % 2 == 0 else Agent('B')

        segregation = self.city.calculate_segregation()
        self.assertLess(segregation, 1.0, "Segregation should be less than 100% for a mixed grid")

    def test_generate_random_parameters(self):
        """
        Test if random parameters are generated within expected ranges.
        """
        params = generate_random_parameters()
        self.assertIn(params["width"], range(10, 51), "Width is out of range")
        self.assertIn(params["height"], range(10, 51), "Height is out of range")
        self.assertGreaterEqual(params["occupation_percentage"], 0.5)
        self.assertLessEqual(params["occupation_percentage"], 1.0)
        self.assertGreaterEqual(params["discr_attr_percentage"], 0.3)
        self.assertLessEqual(params["discr_attr_percentage"], 0.7)
        self.assertGreaterEqual(params["discrimination_rate"], 0.2)
        self.assertLessEqual(params["discrimination_rate"], 0.8)

    def test_read_parameters_from_file(self):
        """
        Test if parameters are correctly read from a file.
        """
        with open("param.txt", "w") as f:
            f.write("width: 20\n")
            f.write("height: 20\n")
            f.write("occupation_percentage: 0.8\n")
            f.write("discr_attr_percentage: 0.5\n")
            f.write("discrimination_rate: 0.4\n")

        params = read_parameters_from_file("param.txt")
        self.assertEqual(params["width"], 20)
        self.assertEqual(params["height"], 20)
        self.assertEqual(params["occupation_percentage"], 0.8)
        self.assertEqual(params["discr_attr_percentage"], 0.5)
        self.assertEqual(params["discrimination_rate"], 0.4)


if __name__ == '__main__':
    unittest.main()