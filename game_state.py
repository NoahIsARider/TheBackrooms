class GameState:
    """游戏状态管理类"""
    
    # 游戏状态常量
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    WIN = 4
    
    def __init__(self):
        self.current_state = self.MENU
        self.previous_state = None
        
        # 菜单选项
        self.menu_options = ['开始游戏', '设置', '退出']
        self.selected_option = 0
        
        # 游戏设置
        self.settings = {
            '音量': 5,  # 范围：0-10
            '亮度': 5,  # 范围：0-10
            '难度': 1   # 0=简单，1=中等，2=困难
        }
        
        # 游戏统计信息
        self.stats = {
            '生存时间': 0,
            '遇到的实体': 0,
            '死亡次数': 0
        }
    
    def change_state(self, new_state):
        """改变游戏状态"""
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def return_to_previous_state(self):
        """返回到上一个状态"""
        if self.previous_state is not None:
            temp = self.current_state
            self.current_state = self.previous_state
            self.previous_state = temp
    
    def is_menu(self):
        """检查当前是否为菜单状态"""
        return self.current_state == self.MENU
    
    def is_playing(self):
        """检查当前是否为游戏进行状态"""
        return self.current_state == self.PLAYING
    
    def is_paused(self):
        """检查当前是否为暂停状态"""
        return self.current_state == self.PAUSED
    
    def is_game_over(self):
        """检查当前是否为游戏结束状态"""
        return self.current_state == self.GAME_OVER
    
    def is_win(self):
        """检查当前是否为胜利状态"""
        return self.current_state == self.WIN
    
    def select_next_option(self):
        """选择下一个菜单选项"""
        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
    
    def select_previous_option(self):
        """选择上一个菜单选项"""
        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
    
    def get_selected_option(self):
        """获取当前选中的菜单选项"""
        return self.menu_options[self.selected_option]
    
    def update_setting(self, setting_name, value):
        """更新游戏设置"""
        if setting_name in self.settings:
            self.settings[setting_name] = value
    
    def get_setting(self, setting_name):
        """获取游戏设置"""
        return self.settings.get(setting_name)
    
    def update_stat(self, stat_name, value):
        """更新游戏统计信息"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
    
    def increment_stat(self, stat_name, amount=1):
        """增加游戏统计信息"""
        if stat_name in self.stats:
            self.stats[stat_name] += amount
    
    def get_stat(self, stat_name):
        """获取游戏统计信息"""
        return self.stats.get(stat_name)
    
    def get_difficulty_name(self):
        """获取难度名称"""
        difficulty_names = ['简单', '中等', '困难']
        return difficulty_names[self.settings['难度']]
    
    def reset_stats(self):
        """重置游戏统计信息"""
        self.stats = {
            '生存时间': 0,
            '遇到的实体': 0,
            '死亡次数': 0
        }