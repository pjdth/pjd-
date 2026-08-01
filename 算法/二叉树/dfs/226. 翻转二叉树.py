# 226. 翻转二叉树
# 给你一棵二叉树的根节点root，翻转这棵二叉树，并返回其根节点。
# 示例 1:
# 输入：root =[4,2,7,1,3,6,9]
# 输出:[4,7,2,9,6,3,1]
# 示例 2:
# 输入:root =[2,1,3]
# 输出：[2,3,1]
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from idlelib.tree import TreeNode
from typing import Optional

class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return root
        def dfs(root):
            if not root:
                return
            root.left, root.right = root.right, root.left
            dfs(root.left)
            dfs(root.right)
        dfs(root)
        return root
