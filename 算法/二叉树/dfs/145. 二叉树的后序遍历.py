# 145.二叉树的后序遍历
from typing import Optional, List
# 给你一棵二叉树的根节点root，返回其节点值的后序遍历。
# 示例 1:
# 输入：root=[1,null,2,3]
# 输出：[3,2,1]

# 示例 2:
# 输入:root =[1,2,3,4,5,null,8,null,null,6,7,9]
# 输出：[4,6,7,5,2,9,8,3, 1]
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def __init__(self):
        self.result = []
    def postorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
        self.postorderTraversal(root.left)
        self.postorderTraversal(root.right)
        self.result.append(root.val)
        return self.result

