# 1022. 从根到叶的二进制数之和
# 给出一棵二叉树，其上每个结点的值都是或。每一条从根到叶的路径都代表一个从最高有效位开始的
# 二进制数。
# ●例如，如果路径为◎->1->1->◎->1，那么它表示二进制数01101，也就是13。
# 对树上的每一片叶子，我们都要找出从根到该叶子的路径所表示的数字。
# 返回这些数字之和。题目数据保证答案是一个32位整数。
# 示例 1:
# 输入:r00t =[1,0,1,0,1,0,1]
# 输出：22
# 解释：（100）+ （101）+ （110）+ （111）= 4 + 5 + 6 + 7 = 22
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def sumRootToLeaf(self, root: Optional[TreeNode]) -> int:
        res=0
        def dfs(node,letter):
            nonlocal res
            if node is None:
                return
            letter+=str(node.val)
            if node.left is None and node.right is None:
                res = res + int(letter, 2)
            dfs(node.left,letter)
            dfs(node.right,letter)
        dfs(root,"")
        return res