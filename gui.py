"""
白盒测试基本路径生成工具 - 图形界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import re

# 导入核心算法模块
from core import BasicPathGenerator, parse_natural_language, get_builtin_examples


class BasicPathGeneratorGUI:
    """白盒测试基本路径生成工具 - 图形化界面版"""

    def __init__(self, root):
        self.root = root
        self.root.title("白盒测试基本路径生成工具")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # 设置样式
        self.setup_styles()

        # 创建主框架
        self.create_widgets()

        # 当前控制流图数据
        self.current_matrix = None
        self.current_node_names = None
        self.generator = None

    def setup_styles(self):
        """设置界面样式"""
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        self.create_toolbar()

        # 主内容区域
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：输入区域
        self.create_input_panel()

        # 右侧：输出区域
        self.create_output_panel()

        # 底部状态栏
        self.create_statusbar()

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = tk.Frame(self.root, bg=self.primary_color, height=50)
        toolbar.pack(fill=tk.X)

        title_label = tk.Label(toolbar, text="白盒测试基本路径生成工具",
                               font=("微软雅黑", 16, "bold"),
                               fg="white", bg=self.primary_color)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        help_btn = tk.Button(toolbar, text="帮助", font=("微软雅黑", 10),
                             bg=self.secondary_color, fg="white",
                             command=self.show_help, cursor="hand2")
        help_btn.pack(side=tk.RIGHT, padx=20)

    def create_input_panel(self):
        """创建左侧输入面板"""
        input_frame = tk.Frame(self.main_paned, bg=self.bg_color)
        self.main_paned.add(input_frame, weight=1)

        # 输入方式选择
        input_method_frame = tk.LabelFrame(input_frame, text="输入方式",
                                           font=("微软雅黑", 12, "bold"),
                                           bg=self.bg_color, fg=self.primary_color)
        input_method_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_frame = tk.Frame(input_method_frame, bg=self.bg_color)
        btn_frame.pack(pady=10)

        buttons = [
            ("手动输入矩阵", self.show_manual_input),
            ("从文件读取", self.load_from_file),
            ("自然语言描述", self.show_natural_input),
            ("内置示例", self.show_example_selector),
        ]

        for text, command in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                            bg=self.secondary_color, fg="white",
                            font=("微软雅黑", 10), cursor="hand2", width=15)
            btn.pack(side=tk.LEFT, padx=5)

        # 控制流图显示区域
        cfg_frame = tk.LabelFrame(input_frame, text="控制流图",
                                  font=("微软雅黑", 12, "bold"),
                                  bg=self.bg_color, fg=self.primary_color)
        cfg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 矩阵显示表格
        self.matrix_tree = ttk.Treeview(cfg_frame, show="headings")
        self.matrix_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 滚动条
        matrix_scroll_y = ttk.Scrollbar(cfg_frame, orient=tk.VERTICAL, command=self.matrix_tree.yview)
        matrix_scroll_x = ttk.Scrollbar(cfg_frame, orient=tk.HORIZONTAL, command=self.matrix_tree.xview)
        self.matrix_tree.configure(yscrollcommand=matrix_scroll_y.set, xscrollcommand=matrix_scroll_x.set)
        matrix_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        matrix_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 操作按钮
        action_frame = tk.Frame(input_frame, bg=self.bg_color)
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_generate = tk.Button(action_frame, text="生成基本路径",
                                      command=self.generate_paths,
                                      bg=self.success_color, fg="white",
                                      font=("微软雅黑", 12, "bold"), cursor="hand2",
                                      width=20, height=1)
        self.btn_generate.pack(pady=10)

    def create_output_panel(self):
        """创建右侧输出面板"""
        output_frame = tk.Frame(self.main_paned, bg=self.bg_color)
        self.main_paned.add(output_frame, weight=1)

        # 路径显示区域
        path_frame = tk.LabelFrame(output_frame, text="生成的基本路径",
                                   font=("微软雅黑", 12, "bold"),
                                   bg=self.bg_color, fg=self.primary_color)
        path_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.path_listbox = tk.Listbox(path_frame, font=("Consolas", 10),
                                       bg="white", fg="black",
                                       selectmode=tk.SINGLE)
        self.path_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        path_scroll = ttk.Scrollbar(path_frame, orient=tk.VERTICAL, command=self.path_listbox.yview)
        self.path_listbox.configure(yscrollcommand=path_scroll.set)
        path_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 详细信息显示
        info_frame = tk.LabelFrame(output_frame, text="详细信息",
                                   font=("微软雅黑", 12, "bold"),
                                   bg=self.bg_color, fg=self.primary_color)
        info_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.info_text = scrolledtext.ScrolledText(info_frame, font=("Consolas", 10),
                                                   height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = tk.Frame(self.root, bg=self.primary_color, height=30)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(self.statusbar, text="就绪",
                                     font=("微软雅黑", 9),
                                     fg="white", bg=self.primary_color)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

    def show_manual_input(self):
        """显示手动输入矩阵对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手动输入控制流图矩阵")
        dialog.geometry("600x500")
        dialog.resizable(False, False)

        tk.Label(dialog, text="结点数量:", font=("微软雅黑", 11)).pack(pady=10)

        n_entry = tk.Entry(dialog, font=("微软雅黑", 11), width=10)
        n_entry.pack()

        matrix_frame = tk.Frame(dialog)
        matrix_frame.pack(pady=10)

        entries = []

        def create_matrix_input():
            for widget in matrix_frame.winfo_children():
                widget.destroy()
            entries.clear()

            try:
                n = int(n_entry.get())
                if n <= 0 or n > 20:
                    messagebox.showerror("错误", "结点数量应在1-20之间")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                return

            # 创建输入表格
            for i in range(n):
                row_entries = []
                for j in range(n):
                    entry = tk.Entry(matrix_frame, width=5, font=("Consolas", 10),
                                     justify="center")
                    entry.grid(row=i, column=j, padx=2, pady=2)
                    entry.insert(0, "0")
                    row_entries.append(entry)
                entries.append(row_entries)

        def confirm():
            n = len(entries)
            matrix = []
            for i in range(n):
                row = []
                for j in range(n):
                    try:
                        val = int(entries[i][j].get())
                        row.append(1 if val != 0 else 0)
                    except:
                        row.append(0)
                matrix.append(row)

            self.current_matrix = matrix
            self.current_node_names = None
            self.display_matrix()
            self.update_status(f"已加载 {n}x{n} 控制流图矩阵")
            dialog.destroy()

        tk.Button(dialog, text="创建矩阵", command=create_matrix_input,
                  bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(pady=5)
        tk.Button(dialog, text="确认加载", command=confirm,
                  bg="#27ae60", fg="white", font=("微软雅黑", 10)).pack(pady=5)

    def load_from_file(self):
        """从文件加载矩阵"""
        filename = filedialog.askopenfilename(
            title="选择控制流图文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            matrix = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    row = list(map(int, line.split()))
                    matrix.append(row)

            n = len(matrix)
            for row in matrix:
                if len(row) != n:
                    messagebox.showerror("错误", "文件格式不正确，不是方阵")
                    return

            self.current_matrix = matrix
            self.current_node_names = None
            self.display_matrix()
            self.update_status(f"已从文件加载 {n}x{n} 控制流图矩阵")

        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")

    def show_natural_input(self):
        """显示自然语言输入对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("自然语言描述流程图")
        dialog.geometry("700x400")

        tk.Label(dialog, text="请输入边的关系:", font=("微软雅黑", 11)).pack(pady=10)
        tk.Label(dialog, text="格式: 结点->结点，多个边用逗号或空格分隔",
                 font=("微软雅黑", 9), fg="gray").pack()

        example_frame = tk.Frame(dialog, bg="#f0f0f0", relief=tk.GROOVE, bd=1)
        example_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(example_frame, text="示例:", font=("微软雅黑", 9, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        examples = [
            "• 0->1, 0->2, 1->3, 2->3, 3->4",
            "• A->B, A->C, B->D, C->D",
            "• start->a, a->b, a->c, b->end, c->end"
        ]
        for ex in examples:
            tk.Label(example_frame, text=ex, font=("Consolas", 9)).pack(anchor=tk.W, padx=20)

        text_area = scrolledtext.ScrolledText(dialog, height=8, font=("Consolas", 10))
        text_area.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        def parse_and_load():
            desc = text_area.get("1.0", tk.END).strip()
            if not desc:
                messagebox.showwarning("警告", "请输入边的关系")
                return

            matrix, node_names = parse_natural_language(desc)

            if matrix is None:
                messagebox.showerror("错误", "无法解析输入，请使用正确格式")
                return

            self.current_matrix = matrix
            self.current_node_names = node_names
            self.display_matrix()
            self.update_status(f"已解析 {len(matrix)} 个结点的控制流图")
            dialog.destroy()

        tk.Button(dialog, text="解析并加载", command=parse_and_load,
                  bg="#27ae60", fg="white", font=("微软雅黑", 11)).pack(pady=10)

    def show_example_selector(self):
        """显示内置示例选择器"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择内置示例")
        dialog.geometry("400x350")

        examples = get_builtin_examples()

        tk.Label(dialog, text="选择一个示例程序:", font=("微软雅黑", 12)).pack(pady=10)

        for name, data in examples.items():
            btn = tk.Button(dialog, text=name,
                            command=lambda d=data, dia=dialog: self.load_example(d['matrix'], d['names'], dia),
                            bg="#3498db", fg="white", font=("微软雅黑", 10),
                            cursor="hand2", width=30)
            btn.pack(pady=5)

    def load_example(self, matrix, names, dialog):
        """加载示例"""
        self.current_matrix = matrix
        self.current_node_names = names
        self.display_matrix()
        self.update_status(f"已加载示例: {len(matrix)}个结点")
        dialog.destroy()

    def display_matrix(self):
        """在表格中显示控制流图矩阵"""
        if self.current_matrix is None:
            return

        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)

        n = len(self.current_matrix)

        columns = ["结点"] + [f"→{i}" for i in range(n)]
        self.matrix_tree["columns"] = columns

        self.matrix_tree.heading("结点", text="结点/目标", anchor="center")
        for i, col in enumerate(columns[1:]):
            self.matrix_tree.heading(col, text=col, anchor="center")
            self.matrix_tree.column(col, width=50, anchor="center")
        self.matrix_tree.column("结点", width=80, anchor="center")

        for i in range(n):
            row_data = [f"结点{i}"] + [str(self.current_matrix[i][j]) for j in range(n)]
            self.matrix_tree.insert("", tk.END, values=row_data)

    def generate_paths(self):
        """生成基本路径"""
        if self.current_matrix is None:
            messagebox.showwarning("警告", "请先输入控制流图")
            return

        self.path_listbox.delete(0, tk.END)
        self.info_text.delete("1.0", tk.END)

        # 创建生成器并运行
        self.generator = BasicPathGenerator(self.current_matrix)
        if self.current_node_names:
            self.generator.set_node_names(self.current_node_names)

        paths, logs = self.generator.run()

        # 显示结果
        for path in paths:
            path_str = ' → '.join([self.generator.node_names.get(n, str(n)) for n in path])
            self.path_listbox.insert(tk.END, path_str)

        # 显示日志
        self.info_text.insert(tk.END, '\n'.join(logs))

        self.update_status(f"生成完成，共 {len(paths)} 条基本路径")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
白盒测试基本路径生成工具 - 使用帮助

1. 输入控制流图
   - 手动输入矩阵: 手动输入结点数量和邻接矩阵
   - 从文件读取: 读取文本格式的矩阵文件
   - 自然语言描述: 使用 "A->B, B->C" 格式描述边
   - 内置示例: 选择预置的示例程序结构

2. 控制流图矩阵说明
   - 矩阵大小 n x n，n为结点数
   - matrix[i][j] = 1 表示从结点i到结点j有边
   - matrix[i][j] = 0 表示无边

3. 生成基本路径
   - 点击"生成基本路径"按钮
   - 工具自动计算圈复杂度
   - 自动生成并优化基本路径集

4. 结果说明
   - 路径数量应等于圈复杂度
   - 每条路径覆盖至少一条独特边
   - 所有边都被至少一条路径覆盖
        """

        dialog = tk.Toplevel(self.root)
        dialog.title("帮助")
        dialog.geometry("600x500")

        text_area = scrolledtext.ScrolledText(dialog, font=("Consolas", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, help_text)
        text_area.configure(state=tk.DISABLED)

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = BasicPathGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()