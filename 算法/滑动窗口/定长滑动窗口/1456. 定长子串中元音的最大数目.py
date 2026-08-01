"""
    @Author:th
    @Time:2026/5/21
    @Desc:
"""
# 1456.定长子串中元音的最大数目

# 给你字符串和整数。
# 请返回字符串中长度为的单个子字符串中可能包含的最大元音字母数。
# 英文中的元音字母为（,1◎）。
# 示例 1:
# 输入:s="abciiidef"，k=3
# 输出：3
# 解释：子字符串“iii"包含3个元音字母。
# 示例 2:
# 输入:s="aeiou"，k =2
# 输出：2
# 解释：任意长度为2的子字符串都包含2个元音字母。
# 示例3:
# 输入：s="leetcode"，k=3
# 输出：2
# 解释:"lee"、"eet"和"ode"都包含2个元音字母。
# 示例 4:
# 输入：s="rhythms"，k = 4
# 输出：0
# 解释：字符串s中不含任何元音字母。
class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        max_count = 0
        current_count = 0

        for i, v in enumerate(s):
            # 添加新字符到窗口
            if v in 'aeiou':
                current_count += 1

            # 当窗口大小超过k时，移除左边的字符
            if i >= k:
                if s[i - k] in 'aeiou':
                    current_count -= 1

            # 更新最大值（窗口大小达到k后才开始记录）
            if i >= k - 1:
                max_count = max(max_count, current_count)

        return max_count


print(Solution().maxVowels("abciiidef", 3))