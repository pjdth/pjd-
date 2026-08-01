# 623.在二叉树中增加一行

# 给定一个二叉树的根root和两个整数val和depth，在给定的深度depth处添加一个值为val的节点
# 行。
# 注意，根节点root位于深度。
# 加法规则如下：
# ●给定整数depth，对于深度为depth-1的每个非空树节点cur，创建两个值为val的树节点作
# 为cur的左子树根和右子树根。
# ·cur原来的左子树应该是新的左子树根的左子树。
# cur原来的右子树应该是新的右子树根的右子树。
# ●如果depth=1意味着depth-1根本没有深度，那么创建一个树节点，值val作为整个原始树
# 的新根，而原始树就是新根的左子树。
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def addOneRow(self, root: Optional[TreeNode], val: int, depth: int) -> Optional[TreeNode]:
        if depth == 1:
            return TreeNode(val, left=root)

        def dfs(node, curr_depth):
            if not node:
                return
            if curr_depth == depth - 1:
                node.left = TreeNode(val, left=node.left)
                node.right = TreeNode(val, right=node.right)
                return

            dfs(node.left, curr_depth + 1)
            dfs(node.right, curr_depth + 1)
        dfs(root, 1)
        return root
