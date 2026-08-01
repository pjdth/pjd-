# 206.反转链表
from typing import Optional

# 给你单链表的头节点head，请你反转链表，并返回反转后的链表。
# 示例 1:
# 输入:head=[1,2,3,4,5]
# 输出：[5,4,3,2,1]
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        cur=head
        pre=None
        while cur:
            cur_next=cur.next
            cur.next=pre
            pre=cur
            cur=cur_next
        return pre


