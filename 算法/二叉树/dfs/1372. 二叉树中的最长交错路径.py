# 1372. 二叉树中的最长交错路径
# 给你一棵以root为根的二叉树，二叉树中的交错路径定义如下：
# ●选择二叉树中任意节点和一个方向（左或者右）。
# ·如果前进方向为右，那么移动到当前节点的的右子节点，否则移动到它的左子节点。
# ●改变前进方向：左变右或者右变左。
# ·重复第二步和第三步，直到你在树中无法继续移动。
# 交错路径的长度定义为：访问过的节点数目-1（单个节点的路径长度为0）。
# 请你返回给定树中最长交错路径的长度。
# 示例 1:
# 输入:root = [1,null,1,1,1,null,null,1,1,null,1,null,null,null,1,null,1]
# 输出：3
# 解释：蓝色节点为树中最长交错路径（右->左->右）。
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        max_cnt=0
        def dfs(root,left,cnt):
            nonlocal max_cnt
            if root is None:
                return
            max_cnt = max(max_cnt, cnt)
            if left==1:
                if root.left:
                    dfs(root.left,0,cnt+1)
                if root.right:
                    dfs(root.right,1,1)
            else:
                if root.right:
                    dfs(root.right,1,cnt+1)
                if root.left:
                    dfs(root.left,0,1)
        if root.left:
            dfs(root,0,0)
        if root.right:
            dfs(root,1,0)
        return max_cnt