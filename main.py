import pygame
import sys
import random
import math
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
YELLOW = (245, 235, 180)  # 更新为更浅的黄色
DARK_YELLOW = (235, 225, 170)  # 更新为更浅的暗黄色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('The Backrooms')
clock = pygame.time.Clock()

# 加载游戏资源
font = pygame.font.SysFont('Arial', 24)

# 导入游戏模块
from maze import Maze
from player import Player
from entity import Entity
from raycasting import Raycaster
from game_state import GameState

# 主游戏类
class Game:
    def __init__(self):
        self.running = True
        self.game_state = GameState()
        self.maze = Maze(20, 20)  # 创建20x20的迷宫
        
        # 确保玩家起始位置是空地
        start_x, start_y = self.maze.get_random_empty_position()
        self.player = Player(start_x + 0.5, start_y + 0.5, self.maze)
        
        # 创建光线投射器
        self.raycaster = Raycaster(self.maze)
        
        # 创建实体（敌人）
        self.entities = []
        self.spawn_entities(5)  # 生成5个实体
        
        # 游戏状态变量
        self.game_over = False
        self.win = False
        self.start_time = pygame.time.get_ticks()
        self.survival_time = 0
        
    def spawn_entities(self, count):
        for _ in range(count):
            # 确保实体生成在空地上，且与玩家有一定距离
            while True:
                x, y = self.maze.get_random_empty_position()
                # 计算与玩家的距离
                dist = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if dist > 5:  # 确保实体与玩家的初始距离足够远
                    break
            
            entity_type = random.choice(['crawler', 'watcher', 'hunter'])
            self.entities.append(Entity(x + 0.5, y + 0.5, entity_type, self.maze))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                # 游戏结束时按R键重新开始
                if (self.game_over or self.win) and event.key == K_r:
                    self.__init__()
    
    def update(self):
        if self.game_over or self.win:
            return
        
        # 更新玩家位置
        self.player.update()
        
        # 更新实体
        for entity in self.entities:
            entity.update(self.player)
            
            # 检测实体与玩家的碰撞
            dist = math.sqrt((entity.x - self.player.x)**2 + (entity.y - self.player.y)**2)
            if dist < 0.5:  # 如果实体与玩家距离小于0.5个单位，游戏结束
                self.game_over = True
        
        # 更新生存时间
        self.survival_time = (pygame.time.get_ticks() - self.start_time) // 1000
        
        # 检查是否达到胜利条件（例如生存超过5分钟）
        if self.survival_time >= 300:  # 5分钟 = 300秒
            self.win = True
    
    def render(self):
        # 清空屏幕
        screen.fill(BLACK)
        
        if not self.game_over and not self.win:
            # 使用光线投射器渲染3D视图
            self.raycaster.render(screen, self.player)
            
            # 渲染实体
            for entity in self.entities:
                self.raycaster.render_entity(screen, self.player, entity)
            
            # 渲染UI
            self.render_ui()
        elif self.game_over:
            self.render_game_over()
        elif self.win:
            self.render_win()
        
        # 更新显示
        pygame.display.flip()
    
    def render_ui(self):
        # 显示生存时间
        time_text = font.render(f'life times: {self.survival_time}s', True, WHITE)
        screen.blit(time_text, (10, 10))
        
        # 显示剩余时间
        remaining_time = max(0, 300 - self.survival_time)
        remaining_text = font.render(f'remaining time: {remaining_time}s', True, WHITE)
        screen.blit(remaining_text, (10, 40))
        
        # 显示小地图
        self.render_minimap()
    
    def render_minimap(self):
        # 小地图尺寸和位置
        map_size = 100
        cell_size = map_size / max(self.maze.width, self.maze.height)
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # 绘制小地图背景
        pygame.draw.rect(screen, GRAY, (map_x, map_y, map_size, map_size))
        
        # 绘制墙壁
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[y][x] == 1:  # 如果是墙
                    pygame.draw.rect(screen, DARK_YELLOW, 
                                    (map_x + x * cell_size, map_y + y * cell_size, 
                                     cell_size, cell_size))
        
        # 绘制玩家位置
        player_x = map_x + self.player.x * cell_size
        player_y = map_y + self.player.y * cell_size
        pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), 2)
        
        # 绘制实体位置
        for entity in self.entities:
            entity_x = map_x + entity.x * cell_size
            entity_y = map_y + entity.y * cell_size
            pygame.draw.circle(screen, RED, (int(entity_x), int(entity_y)), 2)
    
    def render_game_over(self):
        # 游戏结束画面
        game_over_text = font.render('Game Over! You Are Caught', True, RED)
        survival_text = font.render(f'You servived for {self.survival_time} seconds', True, WHITE)
        restart_text = font.render('Press R to Restart', True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(survival_text, (SCREEN_WIDTH//2 - survival_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    
    def render_win(self):
        # 胜利画面
        win_text = font.render('Congradulations! You servived for 5 minutes', True, YELLOW)
        restart_text = font.render('Press R to Restart', True, WHITE)
        
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 25))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 25))
    
    def run(self):
        # 主游戏循环
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

# 游戏入口点
def main():
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()