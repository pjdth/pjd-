"""
    @Author:th
    @Time:2026/7/15
    @Desc:
"""
from typing import Optional


# 129. 求根节点到叶节点数字之和
# 给你一个二叉树的根节点root，树中每个节点都存放有一个到之间的数字。
# 每条从根节点到叶节点的路径都代表一个数字：
# ●例如，从根节点到叶节点的路径1→>2→>3表示数字123。
# 计算从根节点到叶节点生成的所有数字之和。
# 叶节点是指没有子节点的节点。

# 示例 1:
# 输入：root =[1,2,3]
# 输出：25
# 解释:
# 从根到叶子节点路径1->2代表数字12
# 从根到叶子节点路径1->3代表数字13
# 因此，数字总和=12+13=25
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        sum1=0
        i=''
        def dfs(root):
            nonlocal sum1,i
            i=i+str(root.val)
            if root.left:
                dfs(root.left)
            if root.right:
                dfs(root.right)
            if root.left is None and root.right is None:
                sum1+=int(i)
            i=i[0:-1]
        dfs(root)
        return sum1
