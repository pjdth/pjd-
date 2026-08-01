# 951.翻转等价二叉树
from idlelib.tree import TreeNode
from typing import Optional


# 我们可以为二叉树T定义一个翻转操作，如下所示：选择任意节点，然后交换它的左子树和右子树。
# 只要经过一定次数的翻转操作后，能使X等于Y，我们就称二叉树X翻转等价于二叉树Y。
# 这些树由根节点root1和root2给出。如果两个二叉树是翻转等价的树，则返回true，否则返回
# false 。

# 输入:root1 =[1,2,3,4,5,6,null,null,null,7,8],root2 =
# [1,3,2,null,6,4,5,null,null,null,null,8,7]
# 输出：true
# 解释：我们翻转值为1，3以及5的三个节点。
# 示例 2:
# 输入：root1=[，root2 =[]
# 输出：true
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def flipEquiv(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        def dfs(node1, node2):
            if not node1 and not node2:
                return True

            if not node1 or not node2 or node1.val != node2.val:
                return False

            no_flip = dfs(node1.left, node2.left) and dfs(node1.right, node2.right)

            flip = dfs(node1.left, node2.right) and dfs(node1.right, node2.left)

            return no_flip or flip

        return dfs(root1, root2)
