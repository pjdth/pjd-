# 1379. 找出克隆二叉树中的相同节点
# 输入：tree = [7,4,3,null,null,6,19]，target = 3
# 输出：3
# 解释：上图画出了树original和cloned。target节点在树original中，用绿色标记。答
# 案是树cloned中的黄颜色的节点（其他示例类似)。
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    def getTargetCopy(self, original: TreeNode, cloned: TreeNode, target: TreeNode) -> TreeNode:
        def dfs(node):
            if node is None:
                return None
            if node.val == target.val:
                return node
            return dfs(node.left) or dfs(node.right)

        return dfs(cloned)