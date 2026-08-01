"""
    @Author:th
    @Time:2026/7/27
    @Desc:
"""
# 20. 有效的括号
# 给定一个只包括，，，，，的字符串，判断字符串是否有效。
# 有效字符串需满足：
# 1.左括号必须用相同类型的右括号闭合。
# 2.左括号必须以正确的顺序闭合。
# 3.每个右括号都有一个对应的相同类型的左括号。
# 示例 1:
# 输入：s ="（)"
# 输出：true
# 示例 2:
# 输入:s = "()[]{}"
# 输出：true
# 示例 3:
# 输入:s="（]"
# 输出：false
# 示例 4:
# 输入：s="（[])"
# 输出：true
class Solution:
    def isValid(self, s: str) -> bool:
        if len(s) % 2 != 0:
            return False
        stack = []
        for s1 in s:
            if s1=='(':
                stack.append(')')
            elif s1=='[':
                stack.append(']')
            elif s1=='{':
                stack.append('}')
            elif not stack or stack.pop()!=s1:
                return False
        return True if not stack else False
