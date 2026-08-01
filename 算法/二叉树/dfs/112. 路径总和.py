# 112.路径总和
# 给你二叉树的根节点root和一个表示目标和的整数targetSum。判断该树中是否存在根节点到叶子节点
# 的路径，这条路径上所有节点值相加等于目标和targetSum。如果存在，返回true；否则，返回false
# 叶子节点是指没有子节点的节点。
# 示例 1:
# 输入:root = [5,4,8,11,null,13,4,7,2,null,null,null,1]，targetSum = 22
# 输出：true
# 解释：等于目标和的根节点到叶节点路径如上图所示。
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        sum1=0
        pd=False
        def dfs(root):
            if root is None:
                return False
            nonlocal sum1,pd
            sum1+=root.val
            if sum1==targetSum and root.left is None and root.right is None:
                pd=True
                return pd
            if root.left:
                dfs(root.left)
            if root.right:
                dfs(root.right)
            sum1-=root.val
        dfs(root)
        return pd

