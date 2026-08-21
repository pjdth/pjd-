# 1457. 二叉树中的伪回文路径
# 给你一棵二叉树，每个节点的值为1到9。我们称二叉树中的一条路径是「伪回文」的，当它满足：路径
# 经过的所有节点值的排列中，存在一个回文序列。
# 请你返回从根到叶子节点的所有路径中伪回文路径的数目。
# 示例 1:
# 输入:root =[2,3,1,3,1,null,1]
# 输出：2
# 解释：上图为给定的二叉树。总共有3条从根到叶子的路径：红色路径[2，3,3]，绿色路径
# [2,1,1]和路径[2,3,1]。
# 在这些路径中，只有红色和绿色的路径是伪回文路径，因为红色路径[2，3，3]存在回文排列
# [3,2,3]，绿色路径[2,1,1]存在回文排列[1,2,1]。
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def pseudoPalindromicPaths (self, root: Optional[TreeNode]) -> int:
        def dfs(root,mark):
            mark ^= 1 << root.val
            if not root.left and not root.right:
                #只有一个数时，减1异或自己为0，说明只有一个数
                return 1 if mark & (mark - 1) == 0 else 0
            left = dfs(root.left, mark) if root.left else 0
            right = dfs(root.right, mark) if root.right else 0
            return left + right
        return dfs(root,0)

