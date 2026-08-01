# 876.链表的中间结点
from typing import Optional
# 给你单链表的头结点head，请你找出并返回链表的中间结点。
# 如果有两个中间结点，则返回第二个中间结点。
# 示例 1:
# 输入:head=[1,2,3,4,5]
# 输出：[3,4,5]
# 解释：链表只有一个中间结点，值为3。
# 示例 2:
# 输入:head=[1,2,3,4,5,6]
# 输出：[4,5,6]
# 解释：该链表有两个中间结点，值分别为3和4，返回第二个结点。
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        left=right=head
        while right and right.next:
            right=right.next.next
            left=left.next
        return left
