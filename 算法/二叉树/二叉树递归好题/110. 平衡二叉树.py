# 110. 平衡二叉树
# 给定一个二叉树，判断它是否是平衡二叉树
# 示例 1:
# 输入:root =[3,9,20,null,null,15,7]
# 输出：true
# 示例 2:
# 输入:root = [1,2,2,3,3,null,null,4,4]
# 输出：false
# 示例 3:
# 输入：root=[]
# 输出：true
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        def dfs(root):
            if not root:
                return 0
            left = dfs(root.left)
            if left == -1:
                return -1
            right = dfs(root.right)
            if right == -1:
                return -1
            if abs(left - right) > 1:
                return -1
            return 1 + max(left, right)
        return dfs(root) != -1
