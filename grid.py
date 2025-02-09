import random

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[-1 for _ in range(width)] for _ in range(height)]
        self.next_building_id = 1
        self._generate_random_layout()
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if the given position is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _place_building(self, start_x: int, start_y: int, width: int, height: int) -> bool:
        """Place a building with given dimensions. Returns False if placement is invalid."""
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not self._is_valid_position(x, y) or self.grid[y][x] != -1:
                    return False
        
        building_id = self.next_building_id
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                self.grid[y][x] = building_id
        self.next_building_id += 1
        return True
    
    def _place_road(self, x: int, y: int, width: int = 1) -> bool:
        """Place a road segment. Returns False if placement is invalid."""
        if not self._is_valid_position(x, y):
            return False
            
        for w in range(width):
            if not self._is_valid_position(x + w, y) or self.grid[y][x + w] not in [-1, 0]:
                return False
        
        for w in range(width):
            self.grid[y][x + w] = 0
        return True
    
    def _is_road_connected(self, x: int, y: int) -> bool:
        """Check if a road segment is orthogonally connected to another road."""
        if not self._is_valid_position(x, y):
            return False
            
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self._is_valid_position(new_x, new_y) and self.grid[new_y][new_x] == 0:
                return True
        return False

    def _is_adjacent_to_road(self, start_x: int, start_y: int, width: int, height: int) -> bool:
        """Check if the building area is adjacent to a road."""
        for x in range(start_x - 1, start_x + width + 1):
            if self._is_valid_position(x, start_y - 1) and self.grid[start_y - 1][x] == 0:
                return True
            if self._is_valid_position(x, start_y + height) and self.grid[start_y + height][x] == 0:
                return True
        
        for y in range(start_y - 1, start_y + height + 1):
            if self._is_valid_position(start_x - 1, y) and self.grid[y][start_x - 1] == 0:
                return True
            if self._is_valid_position(start_x + width, y) and self.grid[y][start_x + width] == 0:
                return True
        
        return False

    def reset(self):
        """Reset the grid and generate a new random layout."""
        self._generate_random_layout()

    def _generate_random_layout(self,
                               max_road_width: int = 2,
                               min_building_size: int = 2,
                               max_building_size: int = 6):
        """Generate a random layout with roads first, then buildings."""

        self.grid = [[-1 for _ in range(self.width)] for _ in range(self.height)]
        self.next_building_id = 1

        road_cells = 0

        y = 2
        while y < self.height - 2:
            road_width = random.randint(1, max_road_width)
            for w in range(road_width):
                if y + w < self.height:
                    for x in range(self.width):
                        if self.grid[y + w][x] != 0:
                            self.grid[y + w][x] = 0
                            road_cells += 1
            y += road_width + min_building_size + random.randint(0, max_building_size - min_building_size)

        x = 2
        while x < self.width - 2:
            road_width = random.randint(1, max_road_width)
            for w in range(road_width):
                if x + w < self.width:
                    for y in range(self.height):
                        if self.grid[y][x + w] != 0:
                            self.grid[y][x + w] = 0
                            road_cells += 1
            x += road_width + min_building_size + random.randint(0, max_building_size - min_building_size)

        attempts = 200
        while attempts > 0:
            width = random.randint(min_building_size, max_building_size)
            height = random.randint(min_building_size, max_building_size)
            x = random.randint(0, self.width - width)
            y = random.randint(0, self.height - height)
            
            if self._is_adjacent_to_road(x, y, width, height):
                if self._place_building(x, y, width, height):
                    attempts = 200
                    continue
            
            attempts -= 1

    def __str__(self) -> str:
        """Return a string representation of the grid."""
        result = ""
        for row in self.grid:
            for cell in row:
                if cell == -1:
                    result += "_"  # Empty space
                elif cell == 0:
                    result += "▮"  # Road
                else:
                    result += "⌂"  # Building
            result += "\n"
        return result


if __name__ == "__main__":
    grid = Grid(200, 200)

    print(grid)

