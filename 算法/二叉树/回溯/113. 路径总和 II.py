# 给你二叉树的根节点 root 和一个整数目标和 targetSum ，找出所有 从根节点到叶子节点 路径总和等于给定目标和的路径。
#
# 叶子节点 是指没有子节点的节点。
#
# 示例 1：
#
# 输入：root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
# 输出：[[5,4,11,2],[5,8,4,5]]
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        res=[]
        def dfs(root,sz,sum1):
            nonlocal targetSum,res
            if root is None:
                return
            sz.append(root.val)
            sum1 += root.val
            if root.left is None and root.right is None and sum1 == targetSum:
                res.append(sz[:])
            if root.left:
                dfs(root.left,sz,sum1)
            if root.right:
                dfs(root.right,sz,sum1)
            sz.pop()
        dfs(root,[],0)
        return res
