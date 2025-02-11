import networkx as nx
from grid import Grid, CellType
import numpy as np
from enum import StrEnum
from graphviz import Digraph

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
                bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))  # Convert to int
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
            bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))  # Convert to int
            intersection_nodes.add(bounding_box)
        
        for node in intersection_nodes:
            self._graph.add_node(node, type=NodeType.INTERSECTION)

    def _create_end_of_road_nodes(self, end_of_road_corners):
        end_of_road_nodes = set()
        used_corners = set()
        for corner in end_of_road_corners:
            if corner in used_corners:
                continue
            used_corners.add(corner)
            end_of_road = []
            end_of_road.append(corner)
            for other in end_of_road_corners:
                if other in used_corners:
                    continue

                is_part_of_end_of_road = False
                if other[0] == corner[0]:
                    is_part_of_end_of_road = True
                    y_min = min(other[1], corner[1])
                    y_max = max(other[1], corner[1])
                    for y in range(y_min, y_max+1):
                        if self._matrix[corner[0]][y] != CellType.ROAD:
                            is_part_of_end_of_road = False
                            break
                        ort_sum, on_edge = self._check_direction_sum((corner[0], y), self._orthogonal_directions)
                        if not on_edge and ort_sum > 0:
                            is_part_of_end_of_road = False
                            break

                if other[1] == corner[1]:
                    is_part_of_end_of_road = True
                    x_min = min(other[0], corner[0])
                    x_max = max(other[0], corner[0])
                    for x in range(x_min, x_max+1):
                        if self._matrix[x][corner[1]] != CellType.ROAD:
                            is_part_of_end_of_road = False
                            break
                        ort_sum, on_edge = self._check_direction_sum((x, corner[1]), self._orthogonal_directions)
                        if not on_edge and ort_sum > 0:
                            is_part_of_end_of_road = False
                            break

                if is_part_of_end_of_road:
                    used_corners.add(other)
                    end_of_road.append(other)


            x = [corner[0] for corner in end_of_road]
            y = [corner[1] for corner in end_of_road]
            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))
            end_of_road_nodes.add(bounding_box)

        for node in end_of_road_nodes:
            self._graph.add_node(node, type=NodeType.ROAD_END)

    def _find_intersections_and_end_nodes(self):
        intersection_corners = []
        end_of_road_corners = []
        roads = list(zip(*np.where(self._road_matrix == 0)))
        for road in roads:
            node_type = self._check_intersection_point_or_end(road)
            if node_type == NodeType.INTERSECTION:
                intersection_corners.append(road)
            elif node_type == NodeType.ROAD_END:
                end_of_road_corners.append(road)

        self._create_intersection_nodes(intersection_corners)
        self._create_end_of_road_nodes(end_of_road_corners)

    def _create_edges_between_intersections_and_road_ends(self):
        intersections = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.INTERSECTION]
        road_ends = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.ROAD_END]

        for road_end in road_ends:
            min_x, min_y, max_x, max_y = road_end
            for intersection in intersections:
                int_min_x, int_min_y, int_max_x, int_max_y = intersection
                
                # Check for vertical match
                if min_x == int_min_x and max_x == int_max_x:   
                    weight = max_x - min_x + 1
                    min_x, max_x = min(int_min_x, min_x), max(int_max_x, max_x)
                    min_y, max_y = int_min_y, int_max_y
                    road = (min_x, min_y, max_x, max_y)
                    self._graph.add_edge(road_end, intersection, weight=weight, directed=False, road=road)
                # Check for horizontal match
                if min_y == int_min_y and max_y == int_max_y:
                    weight = max_y - min_y + 1
                    min_x, max_x = min(int_min_x, min_x), max(int_max_x, max_x)
                    min_y, max_y = int_min_y, int_max_y
                    road = (min_x, min_y, max_x, max_y)
                    self._graph.add_edge(road_end, intersection, weight=weight, directed=False, road=road)
    
    def _create_edges_between_intersections(self):
        intersections = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.INTERSECTION]
        for intersection in intersections:
            for other in intersections:
                if intersection == other:
                    continue
                    
                int_min_x, int_min_y, int_max_x, int_max_y = intersection
                other_min_x, other_min_y, other_max_x, other_max_y = other

                if int_min_x == other_min_x and int_max_x == other_max_x:
                    weight = int_max_y - int_min_y + 1
                    min_x, max_x = int_min_x, int_max_x
                    min_y, max_y = min(int_min_y, other_min_y), max(int_max_y, other_max_y)
                    road = (min_x, min_y, max_x, max_y)
                    self._graph.add_edge(intersection, other, weight=weight, directed=False, road=road)

                if int_min_y == other_min_y and int_max_y == other_max_y:
                    weight = int_max_x - int_min_x + 1
                    min_x, max_x = min(int_min_x, other_min_x), max(int_max_x, other_max_x)
                    min_y, max_y = int_min_y, int_max_y
                    road = (min_x, min_y, max_x, max_y)
                    self._graph.add_edge(intersection, other, weight=weight, directed=False, road=road)

    def _are_bounding_boxes_adjacent(self, box1, box2):
        min_x1, min_y1, max_x1, max_y1 = box1
        min_x2, min_y2, max_x2, max_y2 = box2

        coords1 = np.array([(x, y) for x in range(min_x1, max_x1 + 1) for y in range(min_y1, max_y1 + 1)])
        coords2 = np.array([(x, y) for x in range(min_x2, max_x2 + 1) for y in range(min_y2, max_y2 + 1)])

        for coord in coords1:
            for dx, dy in self._orthogonal_directions:
                if (coord[0] + dx, coord[1] + dy) in coords2:
                    return True
        return False


    def _create_edges_between_buildings_and_roads(self):
        # TODO: Fix this, the connections are not correct
        buildings = [node for node, data in self._graph.nodes(data=True) if data['type'] in (NodeType.BUILDING, NodeType.WAREHOUSE)]
        edges = [edge for edge in self._graph.edges(data=True)]
        for building in buildings:
            for edge in edges:
                road = edge[2].get('road')
                if road is None:
                    continue
                
                if self._are_bounding_boxes_adjacent(building, road):
                    weight = edge[2].get('weight', 1)
                    self._graph.add_edge(building, edge[1], weight=weight, directed=False)
                    self._graph.add_edge(building, edge[0], weight=weight, directed=False)
                        # Start of Selection
                    if self._graph.has_edge(edge[0], edge[1]):
                        self._graph.remove_edge(edge[0], edge[1])
                

                

    def _create_edges(self):
        self._create_edges_between_intersections_and_road_ends()
        self._create_edges_between_intersections()
        self._create_edges_between_buildings_and_roads()
        
    def create_graph(self):
        self._find_building_nodes()
        self._find_intersections_and_end_nodes()
        self._create_edges()

    def get_graph(self):
        return self._graph  # Corrected to return self._graph
    
    def output_graphviz(self):
        dot = Digraph()

        color_map = {
            NodeType.INTERSECTION: 'dodgerblue',
            NodeType.ROAD_END: 'green3',
            NodeType.BUILDING: 'gold',
            NodeType.WAREHOUSE: 'firebrick1'  
        }

        shape_map = {
            NodeType.INTERSECTION: 'octagon',
            NodeType.ROAD_END: 'square',
            NodeType.BUILDING: 'house',
            NodeType.WAREHOUSE: 'invhouse'
        }

        for node in self._graph.nodes(data=True):
            node_id, node_data = node
            shape = shape_map.get(node_data['type'], 'square')  # Default to square if type not found
            color = color_map.get(node_data['type'], 'gray')  # Default to gray if type not found
            label = f"{node_data['type']}\n{node_id}"  # Include node type in the label
            dot.node(str(node_id), label=label, shape=shape, style='filled', fillcolor=color)
        for edge in self._graph.edges(data=True):
            weight = edge[2].get('weight', 1)  # Default weight to 1 if not found
            dot.edge(str(edge[0]), str(edge[1]), label=str(weight), penwidth=str(weight*2), arrowhead='none')

        dot.render('grid_graph', format='png')


if __name__ == "__main__":
    grid = Grid(6, 6)
    print(grid)
    graph = GridGraph(grid)
    graph.output_graphviz()