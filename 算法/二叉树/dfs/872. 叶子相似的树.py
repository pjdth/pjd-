# 872. 叶子相似的树
# 示例 1:
# 输入:root1 =[3,5,1,6,2,9,8,null,null,7,4]，
# root2 =[3,5,1,6,7,4,2,null,null,null,null,null,null,9,8]
# 输出：true

# 示例 2:
# 输入：root1 =[1,2,3]，root2 =[1,3,2]
# 输出：false
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def __init__(self):
        self.left = []
        self.right = []

    def bianli_left(self, tree):
        # 添加空节点检查
        if tree is None:
            return

        if tree.left is None and tree.right is None:
            self.left.append(tree.val)
        else:
            self.bianli_left(tree.left)
            self.bianli_left(tree.right)

    def bianli_right(self, tree):
        # 添加空节点检查
        if tree is None:
            return

        if tree.left is None and tree.right is None:
            self.right.append(tree.val)
        else:
            self.bianli_right(tree.left)
            self.bianli_right(tree.right)

    def leafSimilar(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        if root1 is None and root2 is None:
            return True
        if root1 is None or root2 is None:  # 简化写法
            return False

        # 清空之前的数据（防止多次调用时累积）
        self.left = []
        self.right = []

        self.bianli_left(root1)
        self.bianli_right(root2)

        # 直接比较列表即可
        return self.left == self.right
