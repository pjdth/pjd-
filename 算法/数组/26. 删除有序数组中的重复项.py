"""
    @Author:th
    @Time:2026/7/29
    @Desc:
"""
from typing import List

from aiofiles.tempfile import _


# 26. 删除有序数组中的重复项
# 给你一个 非严格递增排列 的数组 nums ，请你 原地 删除重复出现的元素，使每个元素 只出现一次 ，返回删除后数组的新长度。元素的 相对顺序 应该保持 一致 。然后返回 nums 中唯一元素的个数。
#
# 考虑 nums 的唯一元素的数量为 k。去重后，返回唯一元素的数量 k。
#
# nums 的前 k 个元素应包含 排序后 的唯一数字。下标 k - 1 之后的剩余元素可以忽略。
# 示例 1：
#
# 输入：nums = [1,1,2]
# 输出：2, nums = [1,2,_]
# 解释：函数应该返回新的长度 2 ，并且原数组 nums 的前两个元素被修改为 1, 2 。不需要考虑数组中超出新长度后面的元素。
# 示例 2：
#
# 输入：nums = [0,0,1,1,1,2,2,3,3,4]
# 输出：5, nums = [0,1,2,3,4,_,_,_,_,_]
# 解释：函数应该返回新的长度 5 ， 并且原数组 nums 的前五个元素被修改为 0, 1, 2, 3, 4 。不需要考虑数组中超出新长度后面的元素。
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if not nums:
            return 0

        left = 0
        for right in range(1, len(nums)):
            if nums[right] != nums[left]:
                left += 1
                nums[left] = nums[right]

        for i in range(left + 1, len(nums)):
            nums[i] = '_'

        return left + 1