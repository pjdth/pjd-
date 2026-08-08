"""
    @Author:th
    @Time:2026/8/8
    @Desc:
"""
from typing import Optional


# 865. 具有所有最深节点的最小子树
# 给定一个根为root的二叉树，每个节点的深度是该节点到根的最短距离。
# 返回包含原始树中所有最深节点的最小子树。
# 如果一个节点在整个树的任意节点之间具有最大的深度，则该节点是最深的。
# 一个节点的子树是该节点加上它的所有后代的集合。
# 示例 1:
# 输入:root =[3,5,1,6,2,0,8,null,null,7,4]
# 输出：[2,7,4]
# 解释：
# 我们返回值为2的节点，在图中用黄色标记。
# 在图中用蓝色标记的是树的最深的节点。
# 注意，节点5、3和2包含树中最深的节点，但节点2的子树最小，因此我们返回它。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def subtreeWithAllDeepest(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        def dfs(node):
            if node is None:
                return 0,None

            left_len,left_node=dfs(node.left)
            right_len,right_node=dfs(node.right)

            if left_len==right_len:
                return left_len+1,node

            if left_len>right_len:
                return left_len+1,left_node
            else:
                return right_len+1,right_node
        return dfs(root)[1]






