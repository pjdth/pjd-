"""
    @Author:th
    @Time:2026/7/9
    @Desc:
"""
from typing import Optional, List
# 144. 二叉树的前序遍历
# 示例 1:
# 输入:root =[1,null,2,3]root=[1,null,2,3]
# 输出：[1,2,3]
#
# 示例 2:
# 输入:root =[1,2,3,4,5,null,8,null,null,6,7,9]
# 输出:[1,2,4,5,6,7,3,8,9]
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def __init__(self):
        self.l1 = []

    def preorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        if root is None:
            return []
        return self.l1[root.val]+self.preorderTraversal(root.left) + self.preorderTraversal(root.right)

