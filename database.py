import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('todo.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                category TEXT,
                difficulty TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT,
                estimated_time INTEGER,  -- 预计完成时间（秒）
                total_time INTEGER DEFAULT 0,  -- 累计总时间（秒）
                timer_start_time TEXT,  -- 计时器开始时间
                timer_paused_time TEXT,  -- 计时器暂停时间
                timer_status TEXT DEFAULT 'stopped'  -- 计时器状态：running, paused, stopped
            )
        ''')
        self.conn.commit()

    def add_task(self, title, description, due_date, priority, category, difficulty):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (
                title, description, due_date, priority, category, difficulty, 
                created_at, estimated_time, total_time, timer_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 'stopped')
        ''', (title, description, due_date, priority, category, difficulty, 
              datetime.now().isoformat()))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_tasks(self, sort_by=None, reverse=False):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM tasks'
        
        if sort_by:
            order_direction = 'DESC' if reverse else 'ASC'
            if sort_by == 'due_date':
                query += f' ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date {order_direction}'
            elif sort_by == 'priority':
                priority_order = "CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 WHEN '低' THEN 3 ELSE 4 END"
                query += f' ORDER BY {priority_order} {order_direction}'
            elif sort_by == 'difficulty':
                difficulty_order = "CASE difficulty WHEN '困难' THEN 1 WHEN '中等' THEN 2 WHEN '简单' THEN 3 ELSE 4 END"
                query += f' ORDER BY {difficulty_order} {order_direction}'
            elif sort_by == 'created_at':
                query += f' ORDER BY created_at {order_direction}'
        
        cursor.execute(query)
        return cursor.fetchall()

    def update_task(self, task_id, title, description, due_date, priority, category, difficulty, completed):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET title=?, description=?, due_date=?, priority=?, category=?, 
                difficulty=?, completed=?
            WHERE id=?
        ''', (title, description, due_date, priority, category, difficulty, completed, task_id))
        self.conn.commit()

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        self.conn.commit()

    def toggle_task_completion(self, task_id, completed):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE tasks SET completed=? WHERE id=?', (completed, task_id))
        self.conn.commit()

    def get_tasks_by_filter(self, filter_type, value):
        cursor = self.conn.cursor()
        if filter_type == 'priority':
            cursor.execute('SELECT * FROM tasks WHERE priority=? ORDER BY due_date', (value,))
        elif filter_type == 'category':
            cursor.execute('SELECT * FROM tasks WHERE category=? ORDER BY due_date', (value,))
        elif filter_type == 'completed':
            cursor.execute('SELECT * FROM tasks WHERE completed=? ORDER BY due_date', (value,))
        return cursor.fetchall()

    def start_timer(self, task_id, estimated_time):
        cursor = self.conn.cursor()
        current_time = datetime.now().isoformat()
        # 将预计时间从分钟转换为秒
        estimated_seconds = estimated_time * 60
        cursor.execute('''
            UPDATE tasks 
            SET timer_start_time=?, timer_status='running', estimated_time=?
            WHERE id=?
        ''', (current_time, estimated_seconds, task_id))
        self.conn.commit()

    def pause_timer(self, task_id):
        cursor = self.conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute('''
            UPDATE tasks 
            SET timer_paused_time=?, timer_status='paused'
            WHERE id=?
        ''', (current_time, task_id))
        self.conn.commit()

    def resume_timer(self, task_id):
        cursor = self.conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute('''
            UPDATE tasks 
            SET timer_start_time=?, timer_status='running'
            WHERE id=?
        ''', (current_time, task_id))
        self.conn.commit()

    def update_total_time(self, task_id, total_seconds):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET total_time=?
            WHERE id=?
        ''', (total_seconds, task_id))
        self.conn.commit()

    def stop_timer(self, task_id, completed):
        cursor = self.conn.cursor()
        current_time = datetime.now().isoformat()
        
        # 获取任务信息
        cursor.execute('SELECT timer_start_time, timer_paused_time, total_time FROM tasks WHERE id=?', (task_id,))
        task = cursor.fetchone()
        
        if task:
            start_time = datetime.fromisoformat(task[0]) if task[0] else None
            paused_time = datetime.fromisoformat(task[1]) if task[1] else None
            total_time = task[2] or 0
            
            # 计算本次计时时间（以秒为单位）
            if start_time:
                if paused_time:
                    elapsed = (paused_time - start_time).total_seconds()
                else:
                    elapsed = (datetime.now() - start_time).total_seconds()
                total_time += int(elapsed)
            
            # 更新任务状态
            cursor.execute('''
                UPDATE tasks 
                SET timer_status='stopped', timer_start_time=NULL, 
                    timer_paused_time=NULL, total_time=?, completed=?
                WHERE id=?
            ''', (total_time, completed, task_id))
            self.conn.commit()

    def get_timer_status(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timer_status, estimated_time, timer_start_time, total_time
            FROM tasks WHERE id=?
        ''', (task_id,))
        return cursor.fetchone()

    def __del__(self):
        self.conn.close() 