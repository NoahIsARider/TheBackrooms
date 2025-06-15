import random

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]  # 1表示墙，0表示通道
        self.generate()
    
    def generate(self):
        """使用深度优先搜索算法生成迷宫"""
        # 从一个随机的奇数坐标开始
        start_x = random.randrange(1, self.width - 1, 2)
        start_y = random.randrange(1, self.height - 1, 2)
        self.grid[start_y][start_x] = 0
        
        # 创建一个栈来存储访问过的单元格
        stack = [(start_x, start_y)]
        
        # 定义可能的移动方向（上、右、下、左）
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        
        while stack:
            current_x, current_y = stack[-1]
            
            # 查找当前单元格的未访问邻居
            neighbors = []
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                # 随机选择一个未访问的邻居
                nx, ny, dx, dy = random.choice(neighbors)
                
                # 打通墙壁
                self.grid[current_y + dy // 2][current_x + dx // 2] = 0
                self.grid[ny][nx] = 0
                
                # 将新单元格添加到栈中
                stack.append((nx, ny))
            else:
                # 如果没有未访问的邻居，则回溯
                stack.pop()
        
        # 添加一些随机的通道以增加迷宫的复杂性
        self._add_random_passages()
        
        # 确保迷宫边缘是墙
        self._ensure_walls_at_edges()
    
    def _add_random_passages(self):
        """添加一些随机的通道以增加迷宫的复杂性"""
        # 添加额外的通道，打破一些墙壁
        passages_to_add = (self.width * self.height) // 20  # 添加约5%的额外通道
        
        for _ in range(passages_to_add):
            # 选择一个随机的墙壁位置（不包括边缘）
            x = random.randrange(2, self.width - 2)
            y = random.randrange(2, self.height - 2)
            
            # 确保选择的是墙壁
            if self.grid[y][x] == 1:
                # 检查是否是连接两个通道的墙
                horizontal_check = self.grid[y][x-1] == 0 and self.grid[y][x+1] == 0
                vertical_check = self.grid[y-1][x] == 0 and self.grid[y+1][x] == 0
                
                if horizontal_check or vertical_check:
                    self.grid[y][x] = 0  # 打通墙壁
    
    def _ensure_walls_at_edges(self):
        """确保迷宫边缘是墙"""
        for x in range(self.width):
            self.grid[0][x] = 1
            self.grid[self.height - 1][x] = 1
        
        for y in range(self.height):
            self.grid[y][0] = 1
            self.grid[y][self.width - 1] = 1
    
    def is_wall(self, x, y):
        """检查给定坐标是否是墙"""
        # 确保坐标在迷宫范围内
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[int(y)][int(x)] == 1
        return True  # 迷宫外部视为墙
    
    def get_random_empty_position(self):
        """获取一个随机的空位置（非墙）"""
        empty_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0:  # 如果是通道
                    empty_positions.append((x, y))
        
        if empty_positions:
            return random.choice(empty_positions)
        else:
            # 如果没有空位置（不太可能发生），返回中心位置
            return (self.width // 2, self.height // 2)
    
    def get_wall_texture_index(self, x, y):
        """获取墙壁的纹理索引，用于视觉变化"""
        # 使用坐标的哈希值来确定纹理索引，这样同一位置的墙总是有相同的纹理
        hash_value = hash((int(x), int(y)))
        return abs(hash_value) % 3  # 假设有3种不同的墙壁纹理