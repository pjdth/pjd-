# 111. 二叉树的最小深度
# 给定一个二叉树，找出其最小深度。
# 最小深度是从根节点到最近叶子节点的最短路径上的节点数量。
# 说明：叶子节点是指没有子节点的节点。
# 示例 1:
# 输入:root =[3,9,20,null,null,15,7]
# 输出：2
#
# 示例 2:
# 输入:root =[2,null,3,null,4,null,5,null,6]
# 输出：5
import math
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        cnt=1
        min_cnt=math.inf
        def dfs(node,cnt):
            nonlocal min_cnt
            if node.left:
                dfs(node.left,cnt+1)
            if node.right:
                dfs(node.right,cnt+1)
            if node.left is None and node.right is None:
                min_cnt=min(min_cnt,cnt)
                return
        dfs(root,cnt)
        return min_cnt