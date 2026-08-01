# 404.左叶子之和
from typing import Optional

# 给定二叉树的根节点root，返回所有左叶子之和。
# 示例 1:
# 输入：root =[3,9,20,null,null,15,7]
# 输出：24
# 解释：在这个二叉树中，有两个左叶子，分别是9和15，所以返回24

# 示例 2:
# 输入：root =[1]
# 输出：0
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def __init__(self):
        self.sum1 = 0

    def bl(self,root):
        if root.left is not None:
            self.bl(root.left)
        if root.left is None and root.right is None:
            self.sum1 += root.val
            return

        if root.right is not None and (root.right.left is not None or root.right.right is not None ):
            self.bl(root.right)

    def sumOfLeftLeaves(self, root: Optional[TreeNode]) -> int:
        if root is None or (root.left is None and root.right is None):
            return 0
        self.bl(root)
        return self.sum1
        


