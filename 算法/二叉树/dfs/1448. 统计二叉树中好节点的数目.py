# 1448.统计二叉树中好节点的数目
import math
from typing import Optional

# 给你一棵根为root的二叉树，请你返回二叉树中好节点的数目。
# 「好节点」X定义为：从根到该节点X所经过的节点中，没有任何节点的值大于X的值。
# 示例 1:

# 输入:root =[3,1,4,3,null,1,5]
# 输出：4
# 解释：图中蓝色节点为好节点。
# 根节点（3）永远是个好节点。
# 节点4->（3,4）是路径中的最大值。
# 节点5->（3,4,5）是路径中的最大值。
# 节点3->（3,1,3）是路径中的最大值。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def goodNodes(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        max1=-math.inf
        cnt=0
        def dfs(node):
            nonlocal max1,cnt
            if node.val>=max1:
                max1=node.val
                cnt+=1
            node.val = max1
            if node.left:
                dfs(node.left)
            max1=node.val
            if node.right:
                dfs(node.right)
        dfs(root)
        return cnt
