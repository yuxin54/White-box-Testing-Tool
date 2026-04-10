# 白盒测试基本路径生成工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

#项目简介

本工具基于**基本路径测试法**，自动生成程序控制流图的基本路径集，并使用**最短复用路径机制**优化路径长度，帮助测试人员高效完成白盒测试用例设计。

### 核心功能

- 🔍 **控制流图输入**：支持4种输入方式
- 📐 **圈复杂度计算**：自动计算 V(G) = E - N + 2
- 🛤️ **基本路径生成**：基于深度优先搜索算法
- ⚡ **路径优化**：使用最短复用路径机制缩短测试序列
- 🖥️ **图形化界面**：基于 tkinter，操作直观

---

## 🚀 快速开始

### 运行环境

| 项目 | 要求 |
|------|------|
| Python | 3.8 或更高版本 |
| 操作系统 | Windows / macOS / Linux |
| 依赖库 | 仅使用 Python 标准库，无需额外安装 |

### 下载与运行

```bash
# 1. 克隆项目
git clone https://github.com/yuxin54/White-box-Testing-Tool.git
cd White-box-Testing-Tool

# 2. 运行程序
python gui.py
