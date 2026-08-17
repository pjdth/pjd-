"""
    @Author:th
    @Time:2026/8/14
    @Desc:
"""
from typing import Optional

# 687. 最长同值路径
# 给定一个二叉树的root，返回最长的路径的长度，这个路径中的每个节点具有相同值。这条路径可以
# 经过也可以不经过根节点。
# 两个节点之间的路径长度由它们之间的边数表示。
#
# 输入:root =[5,4,5,1,1,5]
# 输出：2
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def longestUnivaluePath(self, root: Optional[TreeNode]) -> int:
        cnt=0
        def dfs(root):
            if not root:
                return -1
            left_len = dfs(root.left)+1
            right_len = dfs(root.right)+1
            if root.left and root.left.val != root.val:
                left_len = 0
            if root.right and root.right.val != root.val:
                right_len = 0
            nonlocal cnt
            cnt = max(cnt,left_len+right_len)
            return max(left_len,right_len)
        dfs(root)
        return cnt





