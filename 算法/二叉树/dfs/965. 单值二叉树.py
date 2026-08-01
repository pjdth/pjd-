# 965. 单值二叉树
# 如果二叉树每个节点都具有相同的值，那么该二叉树就是单值二叉树。
# 只有给定的树是单值二叉树时，才返回true；否则返回false。
# 示例 1:
# 输入：[1,1,1,1,1,null,1]
# 输出：true
# 示例 2:
# 输入：[2,2,2,5,2]
# 输出：false
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def isUnivalTree(self, root: Optional[TreeNode]) -> bool:
        i=root.val
        b=True
        def dfs(root):
            nonlocal b
            if root is None:
                return
            if root.val != i:
                b=False
            if root.left:
                dfs(root.left)
            if root.right:
                dfs(root.right)
        dfs(root)
        return b


