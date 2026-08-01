# 1026. 节点与其祖先之间的最大差值
# 给定二叉树的根节点root，找出存在于不同节点A和B之间的最大值，其中=|A.val-
# B.vall，且A是B的祖先。
# （如果A的任何子节点之一为B，或者A的任何子节点是B的祖先，那么我们认为A是B的祖先）
# 示例 1:
# 输入:root =[8,3,10,1,6,null,14,null,null,4,7,13]
# 输出：7
# 解释:
# 我们有大量的节点与其祖先的差值，其中一些如下：
# |8 - 1| = 7
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def maxAncestorDiff(self, root: Optional[TreeNode]) -> int:
        cnt = 0
        def dfs(root,max1,min1):
            nonlocal cnt
            if root is None:
                return
            max1=max(max1,root.val)
            min1=min(min1,root.val)
            cnt=max(max1-min1,cnt)
            dfs(root.left,max1,min1)
            dfs(root.right,max1,min1)
        dfs(root,root.val,root.val)
        return cnt

