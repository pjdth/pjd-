"""
    @Author:th
    @Time:2026/5/21
    @Desc:
"""
from typing import List


# 643.子数组最大平均数1

# 给你一个由个元素组成的整数数组nums和一个整数k。
# 请你找出平均数最大且长度为的连续子数组，并输出该最大平均数。
# 任何误差小于10一的答案都将被视为正确答案。
# 示例 1:
# 输入：nums =[1,12,-5,-6,50,3]，k = 4
# 输出：12.75
# 解释：最大平均数 （12-5-6+50)/4 =51/4 =12.75
# 示例 2:
# 输入：nums=[5]，k=1
# 输出：5.00000
class Solution:
    class Solution:
        def findMaxAverage(self, nums: List[int], k: int) -> float:
            sum1 = 0
            max1 = float('-inf')

            for i, V in enumerate(nums):
                sum1 += V

                # 当窗口大小达到k时，开始更新max1
                if i >= k - 1:  # 关键修改：i >= k-1 表示已经有k个元素
                    if i >= k:  # 当i>=k时，需要减去窗口最左边的元素
                        sum1 -= nums[i - k]
                    max1 = max(max1, sum1)

            return max1 / k