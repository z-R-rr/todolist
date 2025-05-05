from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTextEdit, QLabel, QComboBox,
                             QDateEdit, QListWidget, QListWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QMenu, QFrame, QSpinBox)
from PyQt6.QtCore import Qt, QDate, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor, QPalette
from database import Database
from datetime import datetime, timedelta

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setup_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f9ff;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #1976D2;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton[text="取消"] {
                background-color: #f44336;
            }
            QPushButton[text="取消"]:hover {
                background-color: #d32f2f;
            }
        """)

    def setup_ui(self):
        self.setWindowTitle("任务详情")
        self.setMinimumWidth(500)
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入任务标题")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("输入任务描述（可选）")
        self.description_edit.setMaximumHeight(100)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高", "中", "低"])
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["困难", "中等", "简单"])
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["工作", "学习", "生活", "其他"])

        layout.addRow("标题:", self.title_edit)
        layout.addRow("描述:", self.description_edit)
        layout.addRow("截止日期:", self.due_date_edit)
        layout.addRow("优先级:", self.priority_combo)
        layout.addRow("困难度:", self.difficulty_combo)
        layout.addRow("分类:", self.category_combo)

        buttons = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

        if self.task_data:
            self.title_edit.setText(self.task_data[1])
            self.description_edit.setText(self.task_data[2])
            if self.task_data[3]:
                self.due_date_edit.setDate(QDate.fromString(self.task_data[3], "yyyy-MM-dd"))
            self.priority_combo.setCurrentText(self.task_data[4])
            self.category_combo.setCurrentText(self.task_data[5])
            self.difficulty_combo.setCurrentText(self.task_data[6])

        self.setLayout(layout)

    def get_task_data(self):
        return {
            'title': self.title_edit.text(),
            'description': self.description_edit.toPlainText(),
            'due_date': self.due_date_edit.date().toString("yyyy-MM-dd"),
            'priority': self.priority_combo.currentText(),
            'category': self.category_combo.currentText(),
            'difficulty': self.difficulty_combo.currentText()
        }

class TimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f9ff;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

    def setup_ui(self):
        self.setWindowTitle("设置预计时间")
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hours_spin)
        time_layout.addWidget(QLabel("小时"))
        time_layout.addWidget(self.minutes_spin)
        time_layout.addWidget(QLabel("分钟"))

        buttons = QHBoxLayout()
        start_btn = QPushButton("开始计时")
        cancel_btn = QPushButton("取消")
        start_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(start_btn)
        buttons.addWidget(cancel_btn)

        layout.addRow("预计完成时间:", time_layout)
        layout.addRow(buttons)
        self.setLayout(layout)

    def get_time_minutes(self):
        return self.hours_spin.value() * 60 + self.minutes_spin.value()

class TaskItem(QFrame):
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setup_ui()
        self.update_timer_display()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # 创建标题行
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_label = QLabel(self.task_data[1])
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        if self.task_data[7]:  # 如果任务已完成
            title_label.setStyleSheet("color: #888; text-decoration: line-through;")
        
        priority_label = QLabel(self.task_data[4])
        priority_color = {
            "高": "#e74c3c",
            "中": "#f39c12",
            "低": "#2ecc71"
        }.get(self.task_data[4], "#888")
        priority_label.setStyleSheet(f"color: {priority_color}; font-weight: bold; font-size: 12px;")
        
        title_layout.addWidget(title_label, 1)
        title_layout.addWidget(priority_label)
        
        # 创建详情行
        details_layout = QHBoxLayout()
        details_layout.setSpacing(15)
        
        category_label = QLabel(self.task_data[5])
        category_label.setStyleSheet("color: #666; font-size: 12px;")
        
        difficulty_label = QLabel(self.task_data[6])
        difficulty_color = {
            "困难": "#e74c3c",
            "中等": "#f39c12",
            "简单": "#2ecc71"
        }.get(self.task_data[6], "#888")
        difficulty_label.setStyleSheet(f"color: {difficulty_color}; font-size: 12px;")
        
        due_date_label = QLabel(self.task_data[3] if self.task_data[3] else "无截止日期")
        due_date_label.setStyleSheet("color: #666; font-size: 12px;")
        
        details_layout.addWidget(category_label)
        details_layout.addWidget(difficulty_label)
        details_layout.addStretch()
        details_layout.addWidget(due_date_label)
        
        # 创建计时器行
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(15)
        
        # 计时器状态标签
        self.timer_status_label = QLabel()
        self.timer_status_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 12px;")
        
        # 计时器时间显示
        self.timer_time_label = QLabel()
        self.timer_time_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # 计时器按钮组
        self.timer_buttons_layout = QHBoxLayout()
        self.timer_buttons_layout.setSpacing(10)
        
        # 开始/暂停按钮
        self.timer_button = QPushButton("开始计时")
        self.timer_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # 结束按钮
        self.stop_button = QPushButton("结束计时")
        self.stop_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_button.hide()  # 初始隐藏结束按钮
        
        self.timer_buttons_layout.addWidget(self.timer_button)
        self.timer_buttons_layout.addWidget(self.stop_button)
        
        # 根据任务完成状态显示/隐藏计时按钮
        if self.task_data[7]:  # 如果任务已完成
            self.timer_button.hide()
        
        timer_layout.addWidget(self.timer_status_label)
        timer_layout.addWidget(self.timer_time_label)
        timer_layout.addStretch()
        timer_layout.addLayout(self.timer_buttons_layout)
        
        layout.addLayout(title_layout)
        layout.addLayout(details_layout)
        layout.addLayout(timer_layout)
        
        self.setStyleSheet("""
            TaskItem {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
                min-height: 120px;
                min-width: 600px;
            }
            TaskItem:hover {
                background-color: #f5f9ff;
                border: 1px solid #2196F3;
            }
        """)

    def update_timer_display(self):
        timer_status = self.task_data[13]  # timer_status
        total_time = self.task_data[10]    # total_time (以秒为单位)
        estimated_time = self.task_data[9]  # estimated_time (以秒为单位)
        
        if timer_status == 'running':
            self.timer_button.setText("暂停")
            self.timer_status_label.setText("计时中")
            self.stop_button.show()
            
            # 计算已用时间（包括之前累计的时间）
            start_time = datetime.fromisoformat(self.task_data[11])  # timer_start_time
            current_elapsed = (datetime.now() - start_time).total_seconds()
            total_elapsed = current_elapsed + (total_time if total_time else 0)
            
            hours = int(total_elapsed) // 3600
            minutes = (int(total_elapsed) % 3600) // 60
            seconds = int(total_elapsed) % 60
            
            # 显示已用时间和预计时间
            if estimated_time:
                est_hours = estimated_time // 3600
                est_minutes = (estimated_time % 3600) // 60
                est_secs = estimated_time % 60
                self.timer_time_label.setText(
                    f"已用: {hours:02d}:{minutes:02d}:{seconds:02d} / 预计: {est_hours:02d}:{est_minutes:02d}:{est_secs:02d}"
                )
            else:
                self.timer_time_label.setText(f"已用: {hours:02d}:{minutes:02d}:{seconds:02d}")
                
        elif timer_status == 'paused':
            self.timer_button.setText("继续")
            self.timer_status_label.setText("已暂停")
            self.stop_button.show()
            
            # 显示已用时间
            if total_time > 0:
                hours = total_time // 3600
                minutes = (total_time % 3600) // 60
                seconds = total_time % 60
                self.timer_time_label.setText(f"已用: {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.timer_time_label.setText("未开始计时")
                
        else:  # stopped
            self.timer_button.setText("开始计时")
            self.timer_status_label.setText("")
            self.stop_button.hide()
            
            if total_time > 0:
                hours = total_time // 3600
                minutes = (total_time % 3600) // 60
                seconds = total_time % 60
                if self.task_data[7]:  # 如果任务已完成
                    self.timer_time_label.setText(f"完成用时: {hours:02d}:{minutes:02d}:{seconds:02d}")
                else:
                    self.timer_time_label.setText(f"累计用时: {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.timer_time_label.setText("")

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()
        self.load_tasks()
        
        # 创建定时器用于更新计时显示
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_timers)
        self.update_timer.start(1000)  # 每秒更新一次

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f9ff;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #1976D2;
            }
            QLabel {
                color: #333;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)

    def setup_ui(self):
        self.setWindowTitle("待办事项管理器")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 创建工具栏
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("添加任务")
        self.add_btn.clicked.connect(self.add_task)
        toolbar.addWidget(self.add_btn)

        # 添加筛选选项
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "未完成", "已完成", "高优先级", "中优先级", "低优先级"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        toolbar.addWidget(QLabel("筛选:"))
        toolbar.addWidget(self.filter_combo)

        # 添加排序选项
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["截止日期", "优先级", "困难度", "创建时间"])
        self.sort_combo.currentTextChanged.connect(self.apply_sort)
        toolbar.addWidget(QLabel("排序:"))
        toolbar.addWidget(self.sort_combo)

        # 添加排序方向选项
        self.sort_direction_combo = QComboBox()
        self.sort_direction_combo.addItems(["升序", "降序"])
        self.sort_direction_combo.currentTextChanged.connect(self.apply_sort)
        toolbar.addWidget(QLabel("方向:"))
        toolbar.addWidget(self.sort_direction_combo)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 创建任务列表
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.setSpacing(5)
        layout.addWidget(self.task_list)

    def load_tasks(self):
        self.task_list.clear()
        sort_by = self.get_sort_by()
        reverse = self.sort_direction_combo.currentText() == "降序"
        tasks = self.db.get_all_tasks(sort_by, reverse)
        for task in tasks:
            self.add_task_to_list(task)

    def get_sort_by(self):
        sort_text = self.sort_combo.currentText()
        sort_map = {
            "截止日期": "due_date",
            "优先级": "priority",
            "困难度": "difficulty",
            "创建时间": "created_at"
        }
        return sort_map.get(sort_text)

    def apply_sort(self):
        self.load_tasks()

    def add_task_to_list(self, task):
        item = QListWidgetItem()
        task_widget = TaskItem(task)
        task_widget.timer_button.clicked.connect(lambda: self.handle_timer_click(task[0]))
        task_widget.stop_button.clicked.connect(lambda: self.stop_timer(task[0]))
        item.setSizeHint(task_widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, task[0])
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, task_widget)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.db.add_task(
                task_data['title'],
                task_data['description'],
                task_data['due_date'],
                task_data['priority'],
                task_data['category'],
                task_data['difficulty']
            )
            self.load_tasks()

    def edit_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        tasks = self.db.get_all_tasks()
        task_data = next((t for t in tasks if t[0] == task_id), None)
        
        if task_data:
            dialog = TaskDialog(self, task_data)
            if dialog.exec():
                new_data = dialog.get_task_data()
                self.db.update_task(
                    task_id,
                    new_data['title'],
                    new_data['description'],
                    new_data['due_date'],
                    new_data['priority'],
                    new_data['category'],
                    new_data['difficulty'],
                    task_data[7]
                )
                self.load_tasks()

    def apply_filter(self, filter_text):
        self.task_list.clear()
        if filter_text == "全部":
            tasks = self.db.get_all_tasks()
        elif filter_text == "未完成":
            tasks = self.db.get_tasks_by_filter('completed', False)
        elif filter_text == "已完成":
            tasks = self.db.get_tasks_by_filter('completed', True)
        elif filter_text == "高优先级":
            tasks = self.db.get_tasks_by_filter('priority', "高")
        elif filter_text == "中优先级":
            tasks = self.db.get_tasks_by_filter('priority', "中")
        elif filter_text == "低优先级":
            tasks = self.db.get_tasks_by_filter('priority', "低")

        for task in tasks:
            self.add_task_to_list(task)

    def show_context_menu(self, position):
        item = self.task_list.itemAt(position)
        if item:
            task_id = item.data(Qt.ItemDataRole.UserRole)
            menu = QMenu()
            
            tasks = self.db.get_all_tasks()
            task = next((t for t in tasks if t[0] == task_id), None)
            if task:
                # 根据当前状态显示不同的菜单文本
                toggle_text = "标记为未完成" if task[7] else "标记为已完成"
                toggle_action = menu.addAction(toggle_text)
                delete_action = menu.addAction("删除")
                
                # 添加计时器相关菜单项
                timer_status = task[13]  # timer_status
                if timer_status == 'running':
                    menu.addAction("结束计时")
                
                action = menu.exec(self.task_list.mapToGlobal(position))
                if action == delete_action:
                    reply = QMessageBox.question(self, '确认删除', 
                                               '确定要删除这个任务吗？',
                                               QMessageBox.StandardButton.Yes | 
                                               QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.db.delete_task(task_id)
                        self.load_tasks()
                elif action == toggle_action:
                    self.db.toggle_task_completion(task_id, not task[7])
                    self.load_tasks()
                elif action and action.text() == "结束计时":
                    self.stop_timer(task_id)

    def stop_timer(self, task_id):
        reply = QMessageBox.question(self, '任务完成确认', 
                                   '任务是否已完成？',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        completed = reply == QMessageBox.StandardButton.Yes
        self.db.stop_timer(task_id, completed)
        self.load_tasks()

    def update_timers(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task_widget = self.task_list.itemWidget(item)
            if task_widget:
                task_id = item.data(Qt.ItemDataRole.UserRole)
                timer_status = self.db.get_timer_status(task_id)
                if timer_status and timer_status[0] == 'running':
                    task_widget.update_timer_display()
                    # 检查是否达到预计时间
                    if timer_status[1] and timer_status[2] and isinstance(timer_status[2], str):  # estimated_time 和 timer_start_time
                        try:
                            start_time = datetime.fromisoformat(timer_status[2])
                            current_elapsed = (datetime.now() - start_time).total_seconds()
                            total_time = timer_status[3] if timer_status[3] else 0
                            total_elapsed = current_elapsed + total_time
                            if total_elapsed >= timer_status[1]:  # 已经是秒为单位
                                self.check_task_completion(task_id)
                        except (ValueError, TypeError, AttributeError):
                            # 如果时间格式无效，跳过检查
                            pass

    def handle_timer_click(self, task_id):
        timer_status = self.db.get_timer_status(task_id)
        if not timer_status:
            return
            
        status = timer_status[0]
        if status == 'stopped':
            dialog = TimerDialog(self)
            if dialog.exec():
                estimated_time = dialog.get_time_minutes()
                self.db.start_timer(task_id, estimated_time)
                self.load_tasks()
        elif status == 'running':
            # 计算当前累计时间
            try:
                if timer_status[2] and isinstance(timer_status[2], str):
                    start_time = datetime.fromisoformat(timer_status[2])
                    current_elapsed = int((datetime.now() - start_time).total_seconds())
                    total_time = timer_status[3] if timer_status[3] else 0
                    new_total_time = current_elapsed + total_time
                    # 更新数据库中的累计时间
                    self.db.update_total_time(task_id, new_total_time)
                    self.db.pause_timer(task_id)
                else:
                    self.db.pause_timer(task_id)
            except (ValueError, TypeError, AttributeError):
                self.db.pause_timer(task_id)
            self.load_tasks()
        elif status == 'paused':
            # 继续计时时，使用当前时间作为新的开始时间
            self.db.resume_timer(task_id)
            self.load_tasks()

    def check_task_completion(self, task_id):
        reply = QMessageBox.question(self, '任务时间提醒', 
                                   '预计时间已到，任务是否已完成？',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.toggle_task_completion(task_id, True)
            self.stop_timer(task_id)
        else:
            self.db.pause_timer(task_id)
            self.load_tasks() 