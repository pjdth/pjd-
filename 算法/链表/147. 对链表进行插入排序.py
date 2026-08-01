# 147.对链表进行插入排序
#
# 给定单个链表的头head，使用插入排序对链表进行排序，并返回排序后链表的头。
# 插入排序算法的步骤：
# 1.插入排序是迭代的，每次只移动一个元素，直到所有元素可以形成一个有序的输出列表。
# 2.每次迭代中，插入排序只从输入数据中移除一个待排序的元素，找到它在序列中适当的位置，并将其
# 插入。
# 3.重复直到所有输入数据插入完为止。
# 下面是插入排序算法的一个图形示例。部分排序的列表（黑色）最初只包含列表中的第一个元素。每次迭代
# 时，从输入数据中删除一个元素（红色），并就地插入已排序的列表中。
# 对链表进行插入排序。
# 输入: head = [4,2,1,3]
# 输出: [1,2,3,4]
from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def insertionSortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(-1)
        cur=head
        while cur:
            cur_next = cur.next
            h=dummy
            while h.next and cur.val>h.next.val :
                h=h.next
            cur.next=h.next
            h.next=cur
            cur=cur_next
        return dummy.next
