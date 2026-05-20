"""
任务执行器模块
"""

import sys
import threading
import time
from typing import Callable


class StreamOutputCollector:
    """
    流式输出收集器
    
    用于重定向stdout，收集输出并传递给回调函数
    """
    
    def __init__(self, output_func: Callable, stop_check_func: Callable):
        """
        初始化输出收集器
        
        Args:
            output_func: 输出回调函数
            stop_check_func: 停止检查函数
        """
        self.output_func = output_func
        self.stop_check_func = stop_check_func
        self.char_buffer = []
        self.last_output_time = 0
        self.output_interval = 0.05  # 输出间隔（秒）
    
    def write(self, text):
        """
        写入文本
        
        Args:
            text: 要写入的文本
        """
        if not self.stop_check_func():
            return
        
        if text:
            current_time = time.time()
            
            # 立即输出换行符
            if text == '\n':
                if self.char_buffer:
                    output_text = ''.join(self.char_buffer)
                    self.output_func(output_text)
                    self.char_buffer = []
                self.output_func('\n')
                self.last_output_time = current_time
            else:
                # 缓冲其他字符
                self.char_buffer.append(text)
                
                # 定期刷新缓冲区
                if current_time - self.last_output_time > self.output_interval:
                    if self.char_buffer:
                        output_text = ''.join(self.char_buffer)
                        self.output_func(output_text)
                        self.char_buffer = []
                    self.last_output_time = current_time
    
    def flush(self):
        """刷新缓冲区"""
        if self.char_buffer:
            output_text = ''.join(self.char_buffer)
            self.output_func(output_text)
            self.char_buffer = []


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, root, output_func: Callable, status_var=None):
        """
        初始化任务执行器
        
        Args:
            root: Tkinter根窗口
            output_func: 输出函数
            status_var: 状态变量
        """
        self.root = root
        self.output_func = output_func
        self.status_var = status_var
        
        # 执行状态
        self.running = False
        self.agent = None
        self.execution_thread = None
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.running
    
    def execute_task(self, agent, task: str, on_complete: Callable = None):
        """
        执行任务
        
        Args:
            agent: PhoneAgent实例
            task: 任务描述
            on_complete: 完成回调
        """
        self.agent = agent
        self.running = True
        
        # 创建输出收集器
        original_stdout = sys.stdout
        sys.stdout = StreamOutputCollector(self._safe_output, self.is_running)
        
        def run():
            try:
                # 执行任务
                result = agent.run(task)
                
                # 输出结果
                self._safe_output(f"\n✅ 任务完成: {result}\n")
                
            except Exception as e:
                self._safe_output(f"\n❌ 执行出错: {str(e)}\n")
                
            finally:
                # 恢复stdout
                sys.stdout = original_stdout
                
                # 更新状态
                self.running = False
                
                # 调用完成回调
                if on_complete:
                    self.root.after(0, on_complete)
        
        # 启动执行线程
        self.execution_thread = threading.Thread(target=run, daemon=True)
        self.execution_thread.start()
    
    def stop(self):
        """停止执行"""
        self.running = False
        self._safe_output("\n🛑 正在停止任务...\n")
        
        if self.status_var:
            self.root.after(0, lambda: self.status_var.set("🛑 任务已停止"))
    
    def _safe_output(self, text):
        """
        安全输出文本
        
        Args:
            text: 要输出的文本
        """
        try:
            self.root.after(0, lambda: self.output_func(text))
        except Exception:
            pass
