from typing import Optional
# 2807.在链表中插入最大公约数

# 给你一个链表的头head，每个结点包含一个整数值。
# 在相邻结点之间，请你插入一个新的结点，结点值为这两个相邻结点值的最大公约数。
# 请你返回插入之后的链表。
# 两个数的最大公约数是可以被两个数字整除的最大正整数。
# 示例 1:
# 输入：head=[18,6,10,3]
# 输出：[18,6,6,2,10,1,3]
# 解释：第一幅图是一开始的链表，第二幅图是插入新结点后的图（蓝色结点为新插入结点）。
# -18和6的最大公约数为6，插入第一和第二个结点之间。
# -6和10的最大公约数为2，插入第二和第三个结点之间。
# -10和3的最大公约数为1，插入第三和第四个结点之间。
# 所有相邻结点之间都插入完毕，返回链表。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def insertGreatestCommonDivisors(self, head: Optional[ListNode]) -> Optional[ListNode]:
        cur=head
        a=head.val
        b=0
        while cur.next:
            b=cur.next.val
            min1=min(a,b)#gcd(a,b)
            while min1>1:
                if a%min1==0 and b%min1==0:
                    break
                min1-=1

            new_node=ListNode(val=min1,next=cur.next)
            cur.next=new_node
            cur=new_node.next
            a=b
        return head


