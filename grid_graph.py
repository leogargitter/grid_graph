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
        self._road_matrix = np.where(self._matrix == CellType.ROAD, 0, 1)
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

    def _check_direction_sum(self, road, directions) -> tuple[int, bool]:
        sum = 0
        on_edge = False
        for direction in directions:
            x = road[0] + direction[0]
            y = road[1] + direction[1]
            if not self._is_within_bounds(x, y):
                on_edge = True
                continue
            sum += self._road_matrix[x][y]

        return sum, on_edge
    
    def _check_intersection_point_or_end(self, road) -> str:
        ort_sum, ort_on_edge = self._check_direction_sum(road, self._orthogonal_directions)
        diag_sum, diag_on_edge = self._check_direction_sum(road, self._diagonal_directions)

        if ort_on_edge and diag_on_edge and ort_sum > 0 and diag_sum > 0:
            return NodeType.ROAD_END
        
        if ort_sum == 0 and diag_sum != 0:
            return NodeType.INTERSECTION
        
        return None
    
    def _check_if_intersection_edge(self, road) -> bool:
        ort_sum, _ =self._check_direction_sum(road, self._orthogonal_directions)
        diag_sum, _ = self._check_direction_sum(road, self._diagonal_directions)

        return ort_sum == 0 and diag_sum == 0
    
    def _create_intersection_nodes(self, intersection_corners):
        intersection_nodes = set()
        used_corners = set()
        
        for corner in intersection_corners:
            if corner in used_corners:
                continue
            used_corners.add(corner)
            intersection = []
            intersection.append(corner)
            for other in intersection_corners:
                is_part_of_intersection = False

                if other != corner and (other[0] == corner[0]):
                    y_check = min(other[1], corner[1]) + 1
                    if (corner[0], y_check) == corner or (other[0], y_check) == other:
                        is_part_of_intersection = True
                    else:
                        is_part_of_intersection = self._check_if_intersection_edge((corner[0], y_check))
                
                if other != corner and (other[1] == corner[1]):
                    x_check = min(other[0], corner[0]) + 1
                    if (x_check, corner[1]) == corner or (x_check, other[1]) == other:
                        is_part_of_intersection = True
                    else:
                        is_part_of_intersection = self._check_if_intersection_edge((x_check, corner[1]))
                
                if is_part_of_intersection:
                    intersection.append(other)
                    used_corners.add(other)
            
            x = [corner[0] for corner in intersection]
            y = [corner[1] for corner in intersection]
            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            bounding_box = (min_x, min_y, max_x, max_y)
            intersection_nodes.add(bounding_box)
        
        return intersection_nodes
                
    

    def _find_intersections_and_ends(self):
        intersection_corners = []
        end_of_road_corners = []
        roads = list(zip(*np.where(self._road_matrix == 0)))
        for road in roads:
            node_type = self._check_intersection_point_or_end(road)
            if node_type == NodeType.INTERSECTION:
                intersection_corners.append(road)
            elif node_type == NodeType.ROAD_END:
                end_of_road_corners.append(road)

        intersection_nodes = self._create_intersection_nodes(intersection_corners)
        print("\n===INTERSECTIONS===\n")
        for node in intersection_nodes:
            print(node)
        print("\n===END OF ROAD===\n")
        for node in end_of_road_corners:
            print(node)
        
    def create_graph(self):
        self._find_building_nodes()
        self._find_intersections_and_ends()

    def get_graph(self):
        return self._graph  # Corrected to return self._graph

if __name__ == "__main__":
    grid = Grid(15, 15)
    print(grid)
    graph = GridGraph(grid)
    # print("\nNODES\n")
    # print(graph.get_graph().nodes(data=True))
