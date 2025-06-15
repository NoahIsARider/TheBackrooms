import pygame
import math
import random  # 将random导入移到文件开头

class Raycaster:
    def __init__(self, maze):
        self.maze = maze
        
        # 渲染参数
        self.fov = math.pi / 3  # 视场角（60度）
        self.half_fov = self.fov / 2
        self.num_rays = 320  # 光线数量
        self.max_depth = 20  # 最大深度
        self.delta_angle = self.fov / self.num_rays
        
        # 纹理尺寸
        self.texture_width = 64
        self.texture_height = 64
        self.entity_width = 64
        self.entity_height = 128
        
        # 墙壁纹理
        self.wall_textures = self._create_wall_textures()
        
        # 实体纹理
        self.entity_textures = self._create_entity_textures()
        
        # 地板和天花板颜色 - 更新为更符合图片的颜色
        self.floor_color = (220, 210, 180)  # 米色地板
        self.ceiling_color = (240, 240, 240)  # 白色天花板（荧光灯效果）
        
        # 光线投射结果缓存
        self.ray_casts = []
    
    def _create_wall_textures(self):
        """创建墙壁纹理"""
        textures = []
        
        # 纹理1：标准后室墙壁 - 更新为更符合图片的墙纸样式
        texture1 = pygame.Surface((self.texture_width, self.texture_height))
        texture1.fill((245, 235, 180))  # 更浅的黄色
        
        # 添加规则的墙纸图案
        for x in range(0, self.texture_width, 16):
            for y in range(0, self.texture_height, 16):
                # 绘制小菱形图案
                points = [
                    (x + 8, y),
                    (x + 16, y + 8),
                    (x + 8, y + 16),
                    (x, y + 8)
                ]
                pygame.draw.polygon(texture1, (235, 225, 170), points, 1)
        
        textures.append(texture1)
        
        # 纹理2：带有轻微污渍的墙壁
        texture2 = texture1.copy()
        for _ in range(50):
            x = random.randint(0, self.texture_width - 1)
            y = random.randint(0, self.texture_height - 1)
            size = random.randint(1, 3)
            color = (235, 225, 170)
            pygame.draw.rect(texture2, color, (x, y, size, size))
        
        textures.append(texture2)
        
        # 纹理3：带有电源插座的墙壁
        texture3 = texture1.copy()
        # 添加电源插座
        socket_y = self.texture_height // 2
        pygame.draw.rect(texture3, (200, 200, 200), (self.texture_width - 10, socket_y - 5, 8, 10))
        
        textures.append(texture3)
        
        return textures
    
    def _create_entity_textures(self):
        """创建实体纹理"""
        textures = []
        
        # 纹理1：爬行者（低矮的黑色轮廓）
        texture1 = pygame.Surface((self.entity_width, self.entity_height), pygame.SRCALPHA)
        
        # 绘制爬行者的身体（低矮的黑色轮廓）
        pygame.draw.ellipse(texture1, (30, 30, 30, 220), 
                           (10, self.entity_height - 40, self.entity_width - 20, 30))
        
        # 添加一些细节
        for _ in range(10):
            x = random.randint(15, self.entity_width - 15)
            y = random.randint(self.entity_height - 35, self.entity_height - 15)
            size = random.randint(2, 4)
            pygame.draw.circle(texture1, (10, 10, 10, 255), (x, y), size)
        
        textures.append(texture1)
        
        # 纹理2：观察者（高大的人形轮廓）
        texture2 = pygame.Surface((self.entity_width, self.entity_height), pygame.SRCALPHA)
        
        # 绘制观察者的身体（高大的人形轮廓）
        pygame.draw.rect(texture2, (20, 20, 20, 200), 
                        (self.entity_width//2 - 10, self.entity_height//2 - 40, 20, 70))
        pygame.draw.circle(texture2, (20, 20, 20, 200), 
                          (self.entity_width//2, self.entity_height//2 - 50), 15)
        
        # 添加眼睛（发光的红点）
        pygame.draw.circle(texture2, (255, 0, 0, 255), 
                          (self.entity_width//2 - 5, self.entity_height//2 - 55), 3)
        pygame.draw.circle(texture2, (255, 0, 0, 255), 
                          (self.entity_width//2 + 5, self.entity_height//2 - 55), 3)
        
        textures.append(texture2)
        
        # 纹理3：猎手（快速移动的模糊轮廓）
        texture3 = pygame.Surface((self.entity_width, self.entity_height), pygame.SRCALPHA)
        
        # 绘制猎手的身体（模糊的人形轮廓）
        for offset in range(-5, 6, 2):
            alpha = 150 - abs(offset) * 20
            pygame.draw.rect(texture3, (40, 40, 40, alpha), 
                            (self.entity_width//2 - 8 + offset, self.entity_height//2 - 35, 16, 60))
            pygame.draw.circle(texture3, (40, 40, 40, alpha), 
                              (self.entity_width//2 + offset, self.entity_height//2 - 45), 12)
        
        # 添加一些细节（锋利的爪子）
        for side in [-1, 1]:
            for i in range(3):
                start_x = self.entity_width//2 + side * 15
                start_y = self.entity_height//2 - 10 + i * 10
                end_x = start_x + side * 10
                end_y = start_y + 5
                pygame.draw.line(texture3, (200, 200, 200, 180), (start_x, start_y), (end_x, end_y), 2)
        
        textures.append(texture3)
        
        return textures
    
    def render(self, screen, player):
        """渲染3D视图"""
        screen_width, screen_height = screen.get_size()
        
        # 清空光线投射结果缓存
        self.ray_casts = []
        
        # 清除屏幕
        screen.fill(self.ceiling_color, (0, 0, screen_width, screen_height // 2))
        screen.fill(self.floor_color, (0, screen_height // 2, screen_width, screen_height // 2))
        
        # 渲染荧光灯
        self._render_ceiling_lights(screen)
        
        # 渲染墙壁
        self._render_walls(screen, player)
        
        # 渲染实体
        self._render_entities(screen, player)
        
        # 应用全局雾效果
        self._apply_fog_effect(screen)
    
    def _render_ceiling_lights(self, screen):
        """渲染天花板上的荧光灯"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        ceiling_height = screen_height // 2
        
        # 每隔一定距离绘制一个荧光灯
        light_spacing = 120
        light_width = 80
        light_height = 10
        
        for x in range(0, screen_width + light_spacing, light_spacing):
            # 计算灯的位置
            light_x = x - (pygame.time.get_ticks() // 50) % light_spacing
            
            # 绘制荧光灯
            light_rect = pygame.Rect(light_x - light_width // 2, ceiling_height // 2 - light_height // 2, 
                                    light_width, light_height)
            
            # 只绘制在屏幕内的灯
            if light_rect.right > 0 and light_rect.left < screen_width:
                # 绘制灯的主体
                pygame.draw.rect(screen, (255, 255, 255), light_rect)
                
                # 绘制灯的发光效果
                for i in range(1, 4):
                    glow_rect = light_rect.inflate(i * 4, i * 2)
                    glow_color = (255, 255, 255, 100 - i * 30)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height))
                    screen.blit(glow_surface, glow_rect)
    
    def _render_walls(self, screen, player):
        """渲染墙壁"""
        screen_width, screen_height = screen.get_size()
        
        # 获取玩家的头部摇晃偏移量
        head_bob = player.get_head_bob_offset()
        
        # 投射光线
        ray_angle = player.angle - self.half_fov
        
        for ray in range(self.num_rays):
            # 规范化角度
            ray_angle %= 2 * math.pi
            
            # 投射单个光线
            result = self._cast_ray(player.x, player.y, ray_angle)
            self.ray_casts.append(result)
            
            # 计算投影平面距离以修正鱼眼效果
            cos_angle = player.angle - ray_angle
            cos_angle %= 2 * math.pi
            if cos_angle > math.pi:
                cos_angle = 2 * math.pi - cos_angle
            dist = result['distance'] * math.cos(cos_angle)
            
            # 计算墙壁高度
            wall_height = int((screen_height * 0.8) / dist) if dist > 0 else screen_height
            
            # 应用头部摇晃效果
            bob_offset = int(head_bob * 10)
            
            # 计算墙壁顶部和底部位置
            wall_top = max(0, (screen_height // 2) - (wall_height // 2) + bob_offset)
            wall_bottom = min(screen_height, (screen_height // 2) + (wall_height // 2) + bob_offset)
            
            # 计算墙壁在屏幕上的位置
            wall_pos = int(ray / self.num_rays * screen_width)
            wall_width = int(screen_width / self.num_rays) + 1  # +1 确保没有间隙
            
            # 获取纹理
            texture_index = result['texture_index']
            texture = self.wall_textures[texture_index]
            
            # 计算纹理X坐标
            texture_x = int(result['texture_pos'] * self.texture_width)
            
            # 绘制墙壁条带
            wall_strip = pygame.Surface((1, wall_bottom - wall_top))
            for y in range(wall_bottom - wall_top):
                # 计算纹理Y坐标
                texture_y = int(y / (wall_bottom - wall_top) * self.texture_height)
                
                # 获取纹理颜色
                color = texture.get_at((texture_x, texture_y))
                
                # 根据距离添加雾效果
                fog_factor = min(1.0, dist / self.max_depth)
                color = self._apply_fog(color, fog_factor)
                
                # 设置像素颜色
                wall_strip.set_at((0, y), color)
            
            # 绘制墙壁条带到屏幕
            screen.blit(pygame.transform.scale(wall_strip, (wall_width, wall_bottom - wall_top)), (wall_pos, wall_top))
            
            # 增加光线角度
            ray_angle += self.delta_angle
    
    def _render_entities(self, screen, player):
        """渲染所有实体"""
        # 这个方法会被游戏主循环调用，传入所有实体
        # 在这里我们只是定义一个空方法，实际的实体渲染在render_entity方法中实现
        pass
    
    def _apply_fog_effect(self, screen):
        """应用全局雾效果"""
        # 创建一个带有透明度的雾效果表面
        fog_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fog_color = (220, 220, 200, 30)  # 淡黄色雾效果，轻微透明
        fog_surface.fill(fog_color)
        
        # 将雾效果表面混合到屏幕上
        screen.blit(fog_surface, (0, 0))
    
    def render_entity(self, screen, player, entity):
        """渲染实体"""
        screen_width, screen_height = screen.get_size()
        
        # 计算实体相对于玩家的位置
        dx = entity.x - player.x
        dy = entity.y - player.y
        
        # 计算实体与玩家的距离
        dist = math.sqrt(dx*dx + dy*dy)
        
        # 如果实体太远，不渲染
        if dist > self.max_depth:
            return
        
        # 计算实体相对于玩家视角的角度
        angle = math.atan2(dy, dx)
        
        # 规范化角度
        angle %= 2 * math.pi
        if angle < 0:
            angle += 2 * math.pi
        
        # 计算玩家视角范围
        player_angle = player.angle % (2 * math.pi)
        left_angle = (player_angle - self.half_fov) % (2 * math.pi)
        right_angle = (player_angle + self.half_fov) % (2 * math.pi)
        
        # 检查实体是否在视野范围内
        in_fov = False
        if left_angle > right_angle:  # 视角跨越了0度
            in_fov = angle >= left_angle or angle <= right_angle
        else:
            in_fov = angle >= left_angle and angle <= right_angle
        
        if not in_fov:
            return
        
        # 检查实体是否被墙壁遮挡
        ray_angle = math.atan2(dy, dx)
        ray_result = self._cast_ray(player.x, player.y, ray_angle)
        
        if ray_result['distance'] < dist:
            return  # 实体被墙壁遮挡
        
        # 计算实体在屏幕上的位置
        angle_diff = (player_angle - angle) % (2 * math.pi)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        
        # 计算实体在屏幕上的X坐标
        entity_x = screen_width // 2 + int(math.tan(angle_diff) * (screen_width // 2))
        if abs(entity_x - screen_width // 2) > screen_width // 2:
            return  # 实体在屏幕外
        
        # 计算实体大小
        entity_size = int((screen_height * 0.5) / dist) if dist > 0 else screen_height
        entity_width = entity_size
        entity_height = entity_size * 2  # 实体高度是宽度的两倍
        
        # 获取头部摇晃偏移量
        head_bob = player.get_head_bob_offset()
        bob_offset = int(head_bob * 10)
        
        # 计算实体顶部和底部位置
        entity_top = max(0, (screen_height // 2) - (entity_height // 2) + bob_offset)
        
        # 获取实体纹理
        texture = self.entity_textures[entity.texture_index]
        
        # 缩放纹理
        scaled_texture = pygame.transform.scale(texture, (entity_width, entity_height))
        
        # 应用雾效果
        fog_factor = min(1.0, dist / self.max_depth)
        for x in range(scaled_texture.get_width()):
            for y in range(scaled_texture.get_height()):
                color = scaled_texture.get_at((x, y))
                if color.a > 0:  # 只处理非透明像素
                    color = self._apply_fog(color, fog_factor)
                    scaled_texture.set_at((x, y), color)
        
        # 绘制实体
        screen.blit(scaled_texture, (entity_x - entity_width // 2, entity_top))
    
    def _cast_ray(self, x, y, angle):
        """投射单个光线并返回结果"""
        # 初始化结果
        result = {
            'distance': float('inf'),
            'texture_index': 0,
            'texture_pos': 0
        }
        
        # 计算光线方向向量
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 水平相交检测
        y_hor = int(y) + (1 if sin_a > 0 else 0)
        dy = 1 if sin_a > 0 else -1
        
        depth_hor = (y_hor - y) / sin_a if sin_a != 0 else float('inf')
        x_hor = x + depth_hor * cos_a
        
        delta_depth = dy / sin_a if sin_a != 0 else float('inf')
        dx = delta_depth * cos_a
        
        for _ in range(self.max_depth):
            tile_x, tile_y = int(x_hor), int(y_hor)
            if 0 <= tile_x < self.maze.width and 0 <= tile_y < self.maze.height:
                if self.maze.is_wall(tile_x, tile_y):
                    texture_pos = x_hor % 1
                    if sin_a < 0:
                        texture_pos = 1 - texture_pos
                    
                    result['distance'] = depth_hor
                    result['texture_index'] = self.maze.get_wall_texture_index(tile_x, tile_y)
                    result['texture_pos'] = texture_pos
                    break
            
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth
            
            if depth_hor > self.max_depth:
                break
        
        # 垂直相交检测
        x_vert = int(x) + (1 if cos_a > 0 else 0)
        dx = 1 if cos_a > 0 else -1
        
        depth_vert = (x_vert - x) / cos_a if cos_a != 0 else float('inf')
        y_vert = y + depth_vert * sin_a
        
        delta_depth = dx / cos_a if cos_a != 0 else float('inf')
        dy = delta_depth * sin_a
        
        for _ in range(self.max_depth):
            tile_x, tile_y = int(x_vert), int(y_vert)
            if 0 <= tile_x < self.maze.width and 0 <= tile_y < self.maze.height:
                if self.maze.is_wall(tile_x, tile_y):
                    texture_pos = y_vert % 1
                    if cos_a > 0:
                        texture_pos = 1 - texture_pos
                    
                    if depth_vert < result['distance']:
                        result['distance'] = depth_vert
                        result['texture_index'] = self.maze.get_wall_texture_index(tile_x, tile_y)
                        result['texture_pos'] = texture_pos
                    break
            
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth
            
            if depth_vert > self.max_depth:
                break
        
        return result
    
    def _apply_fog(self, color, fog_factor):
        """应用雾效果"""
        r, g, b = color[:3]
        fog_color = (50, 45, 30)  # 雾的颜色（暗黄色）
        
        r = int(r * (1 - fog_factor) + fog_color[0] * fog_factor)
        g = int(g * (1 - fog_factor) + fog_color[1] * fog_factor)
        b = int(b * (1 - fog_factor) + fog_color[2] * fog_factor)
        
        if len(color) > 3:
            return (r, g, b, color[3])
        else:
            return (r, g, b)