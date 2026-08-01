# 1721.交换链表中的节点
from typing import Optional
# 给你链表的头节点head和一个整数。
# 交换链表正数第个节点和倒数第个节点的值后，返回链表的头节点（链表从1开始索引）。
# 示例 1:
# 输入:head =[1,2,3,4,5]，k =2
# 输出：[1,4,3,2,5]
# 示例 2:
# 输入:head = [7,9,6,6,7,8,3, 0,9,5]，k = 5
# 输出：[7,9,6,6,8,7,3,0,9,5]
# 示例 3:
# 输入：head=[1]，k=1
# 输出：[1]
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def swapNodes(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if head.next is None :
            return head
        dummy = ListNode(-1, head)
        left=dummy
        right=dummy
        cur=dummy
        i=0
        while cur:
            if i>k:
                right = right.next
            if i<k:
                left = left.next
            cur = cur.next
            i+=1
        # 第1行拆分
        left_next = left.next.next
        right_next = right.next.next

        # 第2行拆分（元组解包不能分开写，必须临时存）
        temp_A = left.next
        temp_B = right.next
        left.next = temp_B
        right.next = temp_A

        # 第3行拆分
        # left.next = temp_B = B
        B = left.next
        B.next = left_next
        # right.next = temp_A = A
        A = right.next
        A.next = right_next
        return dummy.next


print(Solution().swapNodes(head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5))))), k=2))

