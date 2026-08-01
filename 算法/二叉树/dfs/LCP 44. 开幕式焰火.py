# LCP44.开幕式焰火

# 「力扣挑战赛」开幕式开始了，空中绽放了一颗二叉树形的巨型焰火。给定一棵二叉树root代表焰
# 火，节点值表示巨型焰火这一位置的颜色种类。请帮小扣计算巨型焰火有多少种不同的颜色。
# 示例 1:
# 输入：
# root =[1,3,2,1,null,2]
# 输出：
# 3
# 解释：焰火中有3个不同的颜色，值分别为1、2、3
# 示例 2:
# 输入：
# root=[3,3,3]
# 输出：
# 1
# 解释：焰火中仅出现1个颜色，值为3

class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
class Solution:
    def numColor(self, root: TreeNode) -> int:
        a=set()
        def dfs(root):
            if root is None:
                return
            a.add(root.val)
            dfs(root.left)
            dfs(root.right)
        dfs(root)
        return len(a)
