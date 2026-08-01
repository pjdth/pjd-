# 199.二叉树的右视图
#
# 给定一个二叉树的根节点root，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看
# 到的节点值。
# 示例 1:
# 输入：root =[1,2,3,null,5,null,4]
# 输出：[1,3,4]
#
# 示例 2:
# 输入:root =[1,2,3,4,null,null,null,5]
# 输出：[1,3,4,5]
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
        l1=[]
        def dfs(root,i):
            if i==len(l1):
                l1.append(root.val)
            if root.right:
                dfs(root.right,i+1)
            if root.left:
                dfs(root.left,i+1)
            return
        dfs(root,0)
        return l1





