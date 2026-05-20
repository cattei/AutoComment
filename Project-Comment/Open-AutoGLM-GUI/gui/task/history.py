"""
任务历史管理模块
"""

import os
import json
from datetime import datetime
from typing import List, Dict


class TaskHistory:
    """任务历史管理器"""
    
    def __init__(self, history_file='config/task_history.json'):
        """
        初始化任务历史管理器
        
        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = history_file
        self.history = []
        self.load()
    
    def load(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"加载任务历史失败: {e}")
            self.history = []
    
    def save(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务历史失败: {e}")
    
    def add(self, task: str, platform: str = None):
        """
        添加任务到历史
        
        Args:
            task: 任务描述
            platform: 平台名称
        """
        record = {
            'task': task,
            'platform': platform,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 添加到开头
        self.history.insert(0, record)
        
        # 限制历史记录数量
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save()
    
    def get_all(self) -> List[Dict]:
        """获取所有历史记录"""
        return self.history.copy()
    
    def delete(self, index: int):
        """
        删除指定索引的历史记录
        
        Args:
            index: 历史记录索引
        """
        if 0 <= index < len(self.history):
            del self.history[index]
            self.save()
    
    def clear(self):
        """清空所有历史记录"""
        self.history = []
        self.save()
    
    def remove_duplicates(self):
        """移除重复的任务"""
        seen = set()
        unique = []
        
        for record in self.history:
            task = record.get('task', '')
            if task not in seen:
                seen.add(task)
                unique.append(record)
        
        self.history = unique
        self.save()
