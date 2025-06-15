import pygame
import math
from pygame.locals import *

class Player:
    def __init__(self, x, y, maze):
        self.x = x  # 玩家X坐标
        self.y = y  # 玩家Y坐标
        self.angle = 0  # 玩家朝向角度（弧度）
        self.maze = maze  # 迷宫引用
        
        # 移动速度和旋转速度
        self.move_speed = 0.05
        self.run_speed = 0.08
        self.rot_speed = 0.03
        
        # 碰撞检测参数
        self.collision_radius = 0.2
        
        # 脚步声计时器
        self.footstep_timer = 0
        self.footstep_interval = 20  # 脚步声间隔（帧数）
        
        # 头部摇晃效果
        self.head_bob = 0
        self.head_bob_amount = 0.5
        self.head_bob_speed = 0.1
        
        # 疲劳系统
        self.stamina = 100  # 最大耐力值
        self.current_stamina = 100  # 当前耐力值
        self.stamina_recovery_rate = 0.2  # 每帧恢复的耐力
        self.stamina_drain_rate = 0.5  # 奔跑每帧消耗的耐力
        self.is_running = False
    
    def update(self):
        # 获取按键状态
        keys = pygame.key.get_pressed()
        
        # 处理旋转
        if keys[K_LEFT] or keys[K_a]:
            self.angle -= self.rot_speed
        if keys[K_RIGHT] or keys[K_d]:
            self.angle += self.rot_speed
        
        # 规范化角度到 [0, 2π)
        self.angle = self.angle % (2 * math.pi)
        
        # 计算方向向量
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        
        # 处理奔跑状态
        self.is_running = keys[K_LSHIFT] and self.current_stamina > 0
        
        # 更新耐力
        if self.is_running:
            self.current_stamina = max(0, self.current_stamina - self.stamina_drain_rate)
        else:
            self.current_stamina = min(self.stamina, self.current_stamina + self.stamina_recovery_rate)
        
        # 确定移动速度
        speed = self.run_speed if self.is_running else self.move_speed
        
        # 处理移动
        moved = False
        
        if keys[K_UP] or keys[K_w]:
            # 向前移动
            new_x = self.x + dx * speed
            new_y = self.y + dy * speed
            if not self._check_collision(new_x, new_y):
                self.x, self.y = new_x, new_y
                moved = True
        
        if keys[K_DOWN] or keys[K_s]:
            # 向后移动
            new_x = self.x - dx * speed
            new_y = self.y - dy * speed
            if not self._check_collision(new_x, new_y):
                self.x, self.y = new_x, new_y
                moved = True
        
        # 侧向移动（左右平移）
        if keys[K_q]:  # 左平移
            strafe_dx = math.cos(self.angle - math.pi/2)
            strafe_dy = math.sin(self.angle - math.pi/2)
            new_x = self.x + strafe_dx * speed
            new_y = self.y + strafe_dy * speed
            if not self._check_collision(new_x, new_y):
                self.x, self.y = new_x, new_y
                moved = True
        
        if keys[K_e]:  # 右平移
            strafe_dx = math.cos(self.angle + math.pi/2)
            strafe_dy = math.sin(self.angle + math.pi/2)
            new_x = self.x + strafe_dx * speed
            new_y = self.y + strafe_dy * speed
            if not self._check_collision(new_x, new_y):
                self.x, self.y = new_x, new_y
                moved = True
        
        # 更新头部摇晃效果
        if moved:
            self.head_bob += self.head_bob_speed
            self.footstep_timer += 1
            
            # 播放脚步声
            if self.footstep_timer >= self.footstep_interval:
                self.footstep_timer = 0
                # 这里可以添加脚步声音效
        else:
            # 如果没有移动，逐渐减少头部摇晃
            if self.head_bob > 0:
                self.head_bob = max(0, self.head_bob - self.head_bob_speed/2)
    
    def _check_collision(self, x, y):
        """检查给定位置是否与墙壁碰撞"""
        # 检查玩家周围的几个点
        for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
            check_x = x + math.cos(angle) * self.collision_radius
            check_y = y + math.sin(angle) * self.collision_radius
            if self.maze.is_wall(check_x, check_y):
                return True
        return False
    
    def get_head_bob_offset(self):
        """获取头部摇晃的偏移量"""
        return math.sin(self.head_bob) * self.head_bob_amount