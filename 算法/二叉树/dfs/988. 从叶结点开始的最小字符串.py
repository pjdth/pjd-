# 988. 从叶结点开始的最小字符串
# 给定一颗根结点为root的二叉树，树中的每一个结点都有一个[0，25]范围内的值，分别代表字母a
# 到「z’。
# 返回按字典序最小的字符串，该字符串从这棵树的一个叶结点开始，到根结点结束。
# 注：字符串中任何较短的前缀在字典序上都是较小的：
# ●例如，在字典序上"ab"比"aba"要小。叶结点是指没有子结点的结点。
# 节点的叶节点是没有子节点的节点。
# 示例 1:
# 输入：root =[0,1,2,3,4,3,4]
# 输出：“dba"
import math
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def smallestFromLeaf(self, root: Optional[TreeNode]) -> str:
        if not root:
            return ""

        ans = None
        path = ""

        def dfs(node):
            nonlocal ans, path
            # 正确转为字符
            path = chr(node.val + ord('a')) + path

            if not node.left and not node.right:
                # 直接字符串比较（字典序）
                if ans is None or path < ans:
                    ans = path
            else:
                if node.left:
                    dfs(node.left)
                if node.right:
                    dfs(node.right)

            # 回溯
            path = path[1:]

        dfs(root)
        return ans

