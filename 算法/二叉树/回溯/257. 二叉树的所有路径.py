"""
    @Author:th
    @Time:2026/8/15
    @Desc:
"""
from typing import Optional, List


# 257.二叉树的所有路径
# 给你一个二叉树的根节点
# root ，按
# 任意顺序 ，返回所有从根节点到叶子节点的路径。
#
# 叶子节点
# 是指没有子节点的节点。
#
# 示例
# 1：
# 输入：root = [1, 2, 3, null, 5]
# 输出：["1->2->5", "1->3"]
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def binaryTreePaths(self, root: Optional[TreeNode]) -> List[str]:
        sz = []

        def dfs(root, str1):
            str1 += str(root.val)
            if root.left is None and root.right is None:
                sz.append(str1)
            str1 += '->'
            if root.left:
                dfs(root.left, str1)
            if root.right:
                dfs(root.right, str1)

        dfs(root, '')
        return sz