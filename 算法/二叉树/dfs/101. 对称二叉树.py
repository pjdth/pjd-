# 101.对称二叉树
# 给你一个二叉树的根节点root，检查它是否轴对称。
# 示例 1:
# 输入:root =[1,2,2,3,4,4,3]
# 输出：true
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        if root.left is None and root.right is None:
            return True
        l=[]
        r=[]
        def dfs1(node,sz):
            if node is None:
                sz.append(node)
                return
            sz.append(node.val)
            dfs1(node.left,sz)
            dfs1(node.right,sz)

        def dfs2(node,sz):
            if node is None:
                sz.append(node)
                return
            sz.append(node.val)
            dfs2(node.right, sz)
            dfs2(node.left,sz)

        dfs1(root.left,l)
        dfs2(root.right,r)
        return l==r
