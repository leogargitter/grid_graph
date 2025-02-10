import networkx as nx
from grid import Grid, CellType
import numpy as np
from enum import StrEnum

class NodeType(StrEnum):
    BUILDING = "building"
    WAREHOUSE = "warehouse"
    INTERSECTION = "intersection"
    ROAD_END = "road_end"



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
                type = NodeType.WAREHOUSE if id in self._grid.warehouses else NodeType.BUILDING
                self._graph.add_node(bounding_box, type=type, id=id)

    def _check_direction_sum(self, road, road_matrix, directions) -> tuple[int, bool]:
        sum = 0
        on_edge = False
        for direction in directions:
            x = road[0] + direction[0]
            y = road[1] + direction[1]
            if not self._is_within_bounds(x, y):
                on_edge = True
                continue
            sum += road_matrix[x][y]

        return sum, on_edge
    
    def _check_intersection_point_or_end(self, road, road_matrix) -> str:
        ort_sum, ort_on_edge = self._check_direction_sum(road, road_matrix, self._orthogonal_directions)
        diag_sum, diag_on_edge = self._check_direction_sum(road, road_matrix, self._diagonal_directions)

        if ort_on_edge and diag_on_edge and ort_sum > 0 and diag_sum > 0:
            return NodeType.ROAD_END
        
        if ort_sum == 0 and diag_sum != 0:
            return NodeType.INTERSECTION
        
        return None
    
    def _find_intersections(self):
        intersection_corners = []
        end_of_road_corners = []
        road_matrix = np.where(self._matrix == CellType.ROAD, 0, 1)
        roads = list(zip(*np.where(road_matrix == 0)))
        for road in roads:
            node_type = self._check_intersection_point_or_end(road, road_matrix)
            if node_type == NodeType.INTERSECTION:
                intersection_corners.append(road)
            elif node_type == NodeType.ROAD_END:
                end_of_road_corners.append(road)

        print("\n===INTERSECTIONS===\n")
        print(intersection_corners)
        print("\n===END OF ROAD===\n")
        print(end_of_road_corners)
        
    def create_graph(self):
        self._find_building_nodes()
        self._find_intersections()

    def get_graph(self):
        return self._graph  # Corrected to return self._graph

if __name__ == "__main__":
    grid = Grid(6, 6)
    print(grid)
    graph = GridGraph(grid)
    # print("\nNODES\n")
    # print(graph.get_graph().nodes(data=True))
