import networkx as nx
from grid import Grid, CellType
import numpy as np
class GridGraph:
    def __init__(self, grid: Grid):
        self._grid = grid
        self._matrix = grid.grid
        self._rows, self._cols = grid.height, grid.width
        self._graph = nx.Graph()
        self._visited = set()
        self._orthogonal_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self._diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        self.create_graph()

    def _is_within_bounds(self, x, y):
        return 0 <= x < self._rows and 0 <= y < self._cols
    
    def _find_building_nodes(self):
        for id in range(1, self._grid.next_building_id):
            x, y = np.where(self._matrix == id)
            for i in range(len(x)):
                min_x, min_y = np.min(x), np.min(y)
                max_x, max_y = np.max(x), np.max(y)
                bounding_box = (min_x, min_y, max_x, max_y)
                type = "warehouse" if id in self._grid.warehouses else "building"
                self._graph.add_node(bounding_box, type=type, id=id)

    def _check_direction_sum(self, road, road_matrix, directions) -> int:
        sum = 0
        for direction in directions:
            x = road[0] + direction[0]
            y = road[1] + direction[1]
            if not self._is_within_bounds(x, y):
                continue
            sum += road_matrix[x][y]
        return sum
    
    def _find_intersections(self):
        corners = []
        road_matrix = np.where(self._matrix == CellType.ROAD, 0, 1)
        roads = list(zip(*np.where(road_matrix == 0)))
        for road in roads:
            ortogonal_sum = self._check_direction_sum(road, road_matrix, self._orthogonal_directions)
            diagonal_sum = self._check_direction_sum(road, road_matrix, self._diagonal_directions)
            if ortogonal_sum == 0 and diagonal_sum != 0:
                corners.append(road)
        for corner in corners:
            print(corner)

    def create_graph(self):
        self._find_building_nodes()
        self._find_intersections()

    def get_graph(self):
        return self._graph  # Corrected to return self._graph

if __name__ == "__main__":
    grid = Grid(12, 12)
    print(grid)
    graph = GridGraph(grid)
    # print("\nNODES\n")
    # print(graph.get_graph().nodes(data=True))
