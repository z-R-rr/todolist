# 待办事项管理器

一个功能完善的待办事项管理工具，支持任务管理、时间追踪和进度监控。

## 功能特点

### 任务管理
- 创建、编辑和删除任务
- 设置任务优先级（高、中、低）
- 设置任务难度（困难、中等、简单）
- 设置任务分类（工作、学习、生活、其他）
- 设置任务截止日期
- 任务完成状态标记

### 时间追踪
- 精确到秒的计时功能
- 支持暂停和继续计时
- 显示累计用时和预计时间
- 到达预计时间时提醒
- 任务完成后显示总用时

### 界面功能
- 任务列表显示
- 支持按不同条件筛选任务
- 支持按不同条件排序任务
- 右键菜单快捷操作
- 美观的界面设计

## 安装步骤

1. 确保已安装 Python 3.6 或更高版本
2. 克隆或下载本项目
3. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 添加任务：
   - 点击"添加任务"按钮
   - 填写任务信息（标题、描述、截止日期等）
   - 点击"保存"按钮

3. 管理任务：
   - 双击任务可以编辑
   - 右键点击任务可以：
     - 标记完成/未完成
     - 删除任务
     - 结束计时

4. 使用计时器：
   - 点击"开始计时"按钮开始计时
   - 设置预计完成时间
   - 可以随时暂停/继续计时
   - 点击"结束计时"按钮结束计时

5. 筛选和排序：
   - 使用顶部的筛选下拉框筛选任务
   - 使用排序下拉框和方向选择器排序任务

## 技术特点

- 使用 PyQt6 构建现代化界面
- SQLite 数据库存储任务数据
- 精确的时间计算和显示
- 响应式设计，支持窗口大小调整

## 注意事项

- 所有时间都精确到秒
- 暂停时会保存累计时间
- 继续时会从累计时间开始计时
- 任务完成后不再显示开始计时按钮

## 开发环境

- Python 3.6+
- PyQt6 6.6.1
- SQLite3