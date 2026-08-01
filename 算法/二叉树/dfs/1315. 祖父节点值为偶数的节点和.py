# 1315.祖父节点值为偶数的节点和
from idlelib.tree import TreeNode
from typing import Optional
# 给你一棵二叉树，请你返回满足以下条件的所有节点的值之和：
# ·该节点的祖父节点的值为偶数。（一个节点的祖父节点是指该节点的父节点的父节点。）
# 如果不存在祖父节点值为偶数的节点，那么返回。
# 示例：
# 输入:root =[6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]
# 输出：18
# 解释：图中红色节点的祖父节点的值为偶数，蓝色节点为这些红色节点的祖父节点。
# class TreeNode:
def __init__(self, val=0, left=None, right=None):
    self.val = val
    self.left = left
    self.right = right

class Solution:
    def sumEvenGrandparent(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        sum1 = 0
        def dfs(root, f=None, ff=None):
            nonlocal sum1
            if ff and ff.val % 2 == 0:
                sum1 += root.val
            ff = f
            f = root
            if root.left:
                dfs(root.left, f, ff)
            if root.right:
                dfs(root.right, f, ff)

        dfs(root)
        return sum1


