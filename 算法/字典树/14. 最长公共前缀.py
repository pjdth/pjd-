# 14.最长公共前缀
from typing import List


# 编写一个函数来查找字符串数组中的最长公共前缀。
# 如果不存在公共前缀，返回空字符串
# 示例 1:
# 输入：strs =["flower","flow","flight"]
# 输出："fl"
# 示例 2:
# 输入：strs =["dog","racecar","car"]
# 输出：…
# 解释：输入不存在公共前缀。
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""

        # 构建字典树
        root = TrieNode()
        for word in strs:
            if not word:  # 如果存在空字符串，公共前缀只能是 ""
                return ""
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True

        # 从根节点开始找唯一路径
        prefix = []
        node = root
        while len(node.children) == 1 and not node.is_end:
            # 唯一子节点的字符
            ch = next(iter(node.children))
            prefix.append(ch)
            node = node.children[ch]

        return "".join(prefix)
