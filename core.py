"""
白盒测试基本路径生成工具 - 核心算法模块
"""
import re


class BasicPathGenerator:
    """白盒测试基本路径生成工具"""

    def __init__(self, flow_matrix):
        """初始化
        Args:
            flow_matrix: 控制流图矩阵，FCM[i][j]=1表示从i到j有边
        """
        self.FCM = flow_matrix
        self.n = len(flow_matrix)

        # 边访问标志 EVF[i][j]: 0未访问 1已访问 2未访问(回滚后)
        self.EVF = [[0] * self.n for _ in range(self.n)]

        # 复用路径 DP[node] = [结点序列]
        self.DP = [[] for _ in range(self.n)]
        self.DPL = [0] * self.n

        # 结点访问标志
        self.NVF = [0] * self.n

        # 结点出度数
        self.NON = [0] * self.n
        for i in range(self.n):
            self.NON[i] = sum(self.FCM[i])

        # 基本路径集合
        self.BPS = []
        self.BPL = []

        # 堆栈
        self.stack = []

        # 起始结点(默认0)和终止结点
        self.start_node = 0
        self.end_nodes = [i for i in range(self.n) if self.NON[i] == 0]

        # 圈复杂度
        self.edge_count = sum(sum(row) for row in self.FCM)
        self.VG = self.edge_count - self.n + 2

        # 结点名称映射（用于输出）
        self.node_names = {i: str(i) for i in range(self.n)}

        # 运行日志
        self.run_logs = []

    def log(self, message):
        """记录日志"""
        self.run_logs.append(message)
        print(message)

    def set_node_names(self, names):
        """设置结点名称（用于更好的输出）"""
        self.node_names = names

    def find_unvisited_edge(self, node):
        """查找结点node是否存在未访问的边"""
        for j in range(self.n):
            if self.FCM[node][j] == 1 and self.EVF[node][j] == 0:
                return j, 0
        return None, -1

    def find_edge_with_dp(self, node):
        """查找未访问边且后继有复用路径"""
        for j in range(self.n):
            if self.FCM[node][j] == 1 and self.EVF[node][j] == 0 and self.DPL[j] > 0:
                return j
        return -1

    def find_edge_without_dp(self, node):
        """查找未访问边且后继无复用路径"""
        for j in range(self.n):
            if self.FCM[node][j] == 1 and self.EVF[node][j] == 0 and self.DPL[j] == 0:
                return j
        return -1

    def update_duplicate_path(self):
        """更新当前栈中所有结点的复用路径(最短)"""
        path_nodes = self.stack.copy()

        for idx, node in enumerate(path_nodes):
            sub_path = path_nodes[idx:]
            if self.DPL[node] == 0 or len(sub_path) < self.DPL[node]:
                self.DP[node] = sub_path.copy()
                self.DPL[node] = len(sub_path)

    def output_path(self):
        """输出当前路径"""
        path = self.stack.copy()
        self.BPS.append(path)
        self.BPL.append(len(path))

        # 格式化输出
        path_str = ' → '.join([self.node_names.get(n, str(n)) for n in path])
        self.log(f"  路径{len(self.BPS)}: {path_str}")

        self.update_duplicate_path()

    def rollback(self, target_node):
        """回滚到target_node访问前的状态"""
        while len(self.stack) > 0 and self.stack[-1] != target_node:
            rolled_node = self.stack.pop()
            for j in range(self.n):
                if self.FCM[rolled_node][j] == 1 and self.EVF[rolled_node][j] == 1:
                    self.EVF[rolled_node][j] = 2  # 标记为回滚未访问

    def traverse(self):
        """主遍历算法"""
        self.stack = [self.start_node]
        self.NVF[self.start_node] = 1

        while len(self.stack) > 0:
            nodeH = self.stack[-1]

            if nodeH in self.end_nodes:
                self.output_path()

                # 回溯直到遇到有未访问边的结点
                while len(self.stack) > 0:
                    top = self.stack[-1]
                    has_unvisited = any(
                        self.FCM[top][j] == 1 and self.EVF[top][j] == 0
                        for j in range(self.n)
                    )
                    if has_unvisited:
                        break
                    self.stack.pop()
                continue

            # 步骤6: 未访问边 + 后继未访问
            next_node, _ = self.find_unvisited_edge(nodeH)
            if next_node != -1 and next_node is not None:
                if self.NVF[next_node] == 0:
                    self.EVF[nodeH][next_node] = 1
                    self.stack.append(next_node)
                    self.NVF[next_node] = 1
                    continue

            # 步骤7: 未访问边 + 后继有复用路径
            next_node = self.find_edge_with_dp(nodeH)
            if next_node != -1:
                self.EVF[nodeH][next_node] = 1
                if self.DPL[next_node] > 0:
                    for j in range(1, len(self.DP[next_node])):
                        self.stack.append(self.DP[next_node][j])
                continue

            # 步骤8: 未访问边 + 后继无复用路径 -> 回滚
            next_node = self.find_edge_without_dp(nodeH)
            if next_node != -1:
                self.rollback(next_node)
                continue

            self.stack.pop()

        self.log(f"\n✓ 共生成 {len(self.BPS)} 条路径")

    def optimize_paths(self):
        """基本路径集优化模块"""
        self.log("\n========== 路径优化 ==========")
        optimized_paths = []

        for path_idx, path in enumerate(self.BPS):
            optimized = path.copy()

            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])

                # 检查这条边是否在其他路径中出现过
                is_unique = True
                for other_idx, other_path in enumerate(self.BPS):
                    if other_idx == path_idx:
                        continue
                    for j in range(len(other_path) - 1):
                        if (other_path[j], other_path[j + 1]) == edge:
                            is_unique = False
                            break
                    if not is_unique:
                        break

                if is_unique:
                    next_node = path[i + 1]
                    if self.DPL[next_node] > 0 and len(self.DP[next_node]) < len(path[i + 1:]):
                        optimized = path[:i + 1] + self.DP[next_node][1:]
                        self.log(f"  路径{path_idx + 1}优化: 使用结点{next_node}的最短复用路径")
                    break

            optimized_paths.append(optimized)

        self.BPS = optimized_paths
        self.BPL = [len(p) for p in self.BPS]

    def run(self):
        """运行完整流程"""
        self.log("========== 开始生成基本路径 ==========")
        self.log(f"✓ 结点数: {self.n}")
        self.log(f"✓ 边数: {self.edge_count}")
        self.log(f"✓ 圈复杂度 V(G) = {self.VG}")
        self.log(f"✓ 预期基本路径数: {self.VG}")

        self.traverse()

        if len(self.BPS) > 0:
            self.optimize_paths()
            self.log("\n========== 最终基本路径集 ==========")
            for i, path in enumerate(self.BPS):
                path_str = ' → '.join([self.node_names.get(n, str(n)) for n in path])
                self.log(f"  基本路径{i + 1}: {path_str}")

            self.log(f"\n✓ 实际生成路径数: {len(self.BPS)}")
            self.log(f"✓ 圈复杂度理论值: {self.VG}")
            if len(self.BPS) == self.VG:
                self.log("✓ 路径数量符合理论值")
            else:
                self.log(f"⚠ 路径数量与理论值不符（理论{self.VG}，实际{len(self.BPS)}）")
        else:
            self.log("⚠ 未生成任何路径，请检查控制流图")

        return self.BPS, self.run_logs


# 辅助函数：自然语言解析
def parse_natural_language(description):
    """
    将自然语言描述转换为CFG矩阵
    支持格式:
    - "0->1, 0->2, 1->3, 2->3, 3->4"
    - "A->B, A->C, B->D, C->D"
    """
    pattern = r'([A-Za-z0-9]+)\s*->\s*([A-Za-z0-9]+)'
    matches = re.findall(pattern, description)

    if not matches:
        return None, None

    # 收集所有结点
    nodes = set()
    for from_node, to_node in matches:
        nodes.add(from_node)
        nodes.add(to_node)

    # 结点排序并建立映射
    sorted_nodes = sorted(nodes, key=lambda x: (isinstance(x, str), x))
    node_to_idx = {node: i for i, node in enumerate(sorted_nodes)}
    idx_to_node = {i: node for i, node in enumerate(sorted_nodes)}

    n = len(nodes)
    matrix = [[0] * n for _ in range(n)]

    for from_node, to_node in matches:
        matrix[node_to_idx[from_node]][node_to_idx[to_node]] = 1

    return matrix, idx_to_node


# 内置示例
def get_builtin_examples():
    """获取内置示例"""
    return {
        "顺序结构": {
            'matrix': [[0, 1, 0], [0, 0, 1], [0, 0, 0]],
            'names': {0: '开始', 1: '处理', 2: '结束'}
        },
        "if-else分支结构": {
            'matrix': [[0, 1, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]],
            'names': {0: '开始', 1: '条件真', 2: '条件假', 3: '汇合', 4: '结束'}
        },
        "while循环结构": {
            'matrix': [[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
            'names': {0: '开始', 1: '循环条件', 2: '循环体', 3: '结束'}
        },
        "复杂结构": {
            'matrix': [[0, 1, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]],
            'names': {0: '开始', 1: '判断', 2: '分支A', 3: '分支B', 4: '汇合', 5: '结束'}
        }
    }