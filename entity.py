import random
import math

class Entity:
    def __init__(self, x, y, entity_type, maze):
        self.x = x  # 实体X坐标
        self.y = y  # 实体Y坐标
        self.entity_type = entity_type  # 实体类型
        self.maze = maze  # 迷宫引用
        
        # 实体属性
        self.speed = 0.02  # 基础移动速度
        self.detection_range = 5.0  # 检测玩家的范围
        self.angle = random.uniform(0, 2 * math.pi)  # 随机初始朝向
        
        # 根据实体类型设置特定属性
        if entity_type == 'crawler':
            self.speed = 0.015
            self.detection_range = 4.0
            self.behavior = self._crawler_behavior
            self.texture_index = 0
        elif entity_type == 'watcher':
            self.speed = 0.02
            self.detection_range = 7.0
            self.behavior = self._watcher_behavior
            self.texture_index = 1
        elif entity_type == 'hunter':
            self.speed = 0.03
            self.detection_range = 6.0
            self.behavior = self._hunter_behavior
            self.texture_index = 2
        else:  # 默认行为
            self.behavior = self._default_behavior
            self.texture_index = 0
        
        # 路径寻找变量
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30  # 每30帧更新一次路径
        
        # 随机移动变量
        self.random_move_timer = 0
        self.random_move_interval = 60  # 每60帧改变一次随机移动方向
        self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
    
    def update(self, player):
        # 计算与玩家的距离
        dist_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        
        # 检查是否能看到玩家（射线检测）
        can_see_player = self._can_see_player(player)
        
        # 根据实体类型执行不同的行为
        self.behavior(player, dist_to_player, can_see_player)
    
    def _crawler_behavior(self, player, dist_to_player, can_see_player):
        """爬行者行为：缓慢移动，但能穿过墙壁"""
        if dist_to_player <= self.detection_range and can_see_player:
            # 如果检测到玩家，直接向玩家移动
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx /= dist
                dy /= dist
            
            # 爬行者可以穿过墙壁，但速度减慢
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # 如果穿过墙壁，速度减半
            if self.maze.is_wall(new_x, new_y):
                new_x = self.x + dx * (self.speed * 0.5)
                new_y = self.y + dy * (self.speed * 0.5)
            
            self.x, self.y = new_x, new_y
        else:
            # 随机移动
            self._random_movement()
    
    def _watcher_behavior(self, player, dist_to_player, can_see_player):
        """观察者行为：静止不动，但如果玩家靠近并可见，会跟踪玩家"""
        if dist_to_player <= self.detection_range and can_see_player:
            # 更新朝向以面对玩家
            dx = player.x - self.x
            dy = player.y - self.y
            self.angle = math.atan2(dy, dx)
            
            # 只有当玩家非常接近时才移动
            if dist_to_player < self.detection_range * 0.5:
                # 向玩家移动
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    dx /= dist
                    dy /= dist
                
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                # 检查碰撞
                if not self.maze.is_wall(new_x, new_y):
                    self.x, self.y = new_x, new_y
        # 观察者在未检测到玩家时不移动
    
    def _hunter_behavior(self, player, dist_to_player, can_see_player):
        """猎手行为：积极追踪玩家，使用A*寻路"""
        # 更新路径寻找计时器
        self.path_update_timer += 1
        
        if dist_to_player <= self.detection_range and can_see_player:
            # 如果能看到玩家，直接向玩家移动
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx /= dist
                dy /= dist
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # 检查碰撞
            if not self.maze.is_wall(new_x, new_y):
                self.x, self.y = new_x, new_y
            
            # 更新朝向
            self.angle = math.atan2(dy, dx)
            
            # 重置路径
            self.path = []
        elif dist_to_player <= self.detection_range * 1.5:
            # 如果在扩展检测范围内但看不到玩家，尝试寻路
            if self.path_update_timer >= self.path_update_interval or not self.path:
                self.path = self._find_path_to_player(player)
                self.path_update_timer = 0
            
            # 沿着路径移动
            if self.path:
                next_x, next_y = self.path[0]
                dx = next_x - self.x
                dy = next_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 0.1:  # 如果已经接近路径点
                    self.path.pop(0)  # 移除当前路径点
                else:
                    # 向路径点移动
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                    
                    new_x = self.x + dx * self.speed
                    new_y = self.y + dy * self.speed
                    
                    # 检查碰撞
                    if not self.maze.is_wall(new_x, new_y):
                        self.x, self.y = new_x, new_y
                    
                    # 更新朝向
                    self.angle = math.atan2(dy, dx)
            else:
                # 如果没有路径，随机移动
                self._random_movement()
        else:
            # 如果玩家不在检测范围内，随机移动
            self._random_movement()
    
    def _default_behavior(self, player, dist_to_player, can_see_player):
        """默认行为：随机移动"""
        self._random_movement()
    
    def _random_movement(self):
        """随机移动行为"""
        # 更新随机移动计时器
        self.random_move_timer += 1
        
        # 每隔一段时间改变随机移动方向
        if self.random_move_timer >= self.random_move_interval:
            self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
            self.random_move_timer = 0
        
        # 规范化方向向量
        dx, dy = self.random_direction
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        
        # 计算新位置
        new_x = self.x + dx * (self.speed * 0.5)  # 随机移动速度较慢
        new_y = self.y + dy * (self.speed * 0.5)
        
        # 检查碰撞
        if not self.maze.is_wall(new_x, new_y):
            self.x, self.y = new_x, new_y
        else:
            # 如果碰到墙，改变方向
            self.random_direction = (-dx, -dy)
        
        # 更新朝向
        self.angle = math.atan2(dy, dx)
    
    def _can_see_player(self, player):
        """检查实体是否能看到玩家（射线检测）"""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > self.detection_range:
            return False
        
        # 规范化方向向量
        if dist > 0:
            dx /= dist
            dy /= dist
        
        # 射线检测
        step_size = 0.1
        steps = int(dist / step_size)
        
        for i in range(1, steps + 1):
            check_x = self.x + dx * (step_size * i)
            check_y = self.y + dy * (step_size * i)
            
            if self.maze.is_wall(check_x, check_y):
                return False
        
        return True
    
    def _find_path_to_player(self, player):
        """使用简化的A*算法寻找到玩家的路径"""
        # 将坐标转换为网格坐标
        start_x, start_y = int(self.x), int(self.y)
        goal_x, goal_y = int(player.x), int(player.y)
        
        # 如果起点或终点是墙，返回空路径
        if self.maze.is_wall(start_x, start_y) or self.maze.is_wall(goal_x, goal_y):
            return []
        
        # 简化的A*算法
        open_set = [(start_x, start_y)]
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self._heuristic(start_x, start_y, goal_x, goal_y)}
        
        while open_set:
            # 找到f_score最小的节点
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            if current == (goal_x, goal_y):
                # 重建路径
                path = []
                while current in came_from:
                    path.append((current[0] + 0.5, current[1] + 0.5))  # 添加单元格中心点
                    current = came_from[current]
                return path[::-1]  # 反转路径
            
            open_set.remove(current)
            
            # 检查四个方向的邻居
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # 检查是否在迷宫范围内且不是墙
                if (0 <= neighbor[0] < self.maze.width and 
                    0 <= neighbor[1] < self.maze.height and 
                    not self.maze.is_wall(neighbor[0], neighbor[1])):
                    
                    tentative_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self._heuristic(neighbor[0], neighbor[1], goal_x, goal_y)
                        
                        if neighbor not in open_set:
                            open_set.append(neighbor)
        
        return []  # 如果没有找到路径
    
    def _heuristic(self, x1, y1, x2, y2):
        """曼哈顿距离启发式函数"""
        return abs(x1 - x2) + abs(y1 - y2)