# 94.二叉树的中序遍历
from typing import Optional, List
# 给定一个二叉树的根节点root，返回它的中序遍历。
# 示例 1:
# 输入:root =[1,null,2,3]
# 输出：[1,3,2]
# 示例 2:
# 输入：root=[]
# 输出：[]
# 示例 3:
# 输入：root =[1]
# 输出：[1]
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def __init__(self):
        self.nodes = []
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        if root is None:
            return []
        return self.inorderTraversal(root.left) + [root.val] + self.inorderTraversal(root.right)