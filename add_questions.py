import json

new_problems = [
    {
        "title": "Search Insert Position", "difficulty": "easy", "topic": "Binary Search",
        "tags": ["array", "binary search"], "acceptance": "43.5%", "solved": False,
        "description": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.",
        "examples": [{"input": "nums = [1,3,5,6], target = 5", "output": "2"}],
        "constraints": ["1 <= nums.length <= 10^4", "-10^4 <= nums[i] <= 10^4"],
        "starter_code": "def search_insert(nums, target):\n    pass",
        "solution_hint": "Use binary search.",
        "test_cases": [{"input": {"nums": [1,3,5,6], "target": 5}, "output": 2}]
    },
    {
        "title": "Maximum Depth of Binary Tree", "difficulty": "easy", "topic": "Trees",
        "tags": ["tree", "dfs", "bfs"], "acceptance": "74.0%", "solved": False,
        "description": "Given the root of a binary tree, return its maximum depth.",
        "examples": [{"input": "root = [3,9,20,null,null,15,7]", "output": "3"}],
        "constraints": ["The number of nodes in the tree is in the range [0, 10^4]."],
        "starter_code": "def max_depth(root):\n    pass",
        "solution_hint": "Use recursion or BFS.",
        "test_cases": [{"input": {"root": [3,9,20,-1,-1,15,7]}, "output": 3}]
    },
    {
        "title": "Single Number", "difficulty": "easy", "topic": "Bit Manipulation",
        "tags": ["array", "bit manipulation"], "acceptance": "71.0%", "solved": False,
        "description": "Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.",
        "examples": [{"input": "nums = [2,2,1]", "output": "1"}],
        "constraints": ["1 <= nums.length <= 3 * 10^4"],
        "starter_code": "def single_number(nums):\n    pass",
        "solution_hint": "XOR all elements.",
        "test_cases": [{"input": {"nums": [2,2,1]}, "output": 1}]
    },
    {
        "title": "Intersection of Two Linked Lists", "difficulty": "easy", "topic": "Linked List",
        "tags": ["linked list", "two pointers"], "acceptance": "53.0%", "solved": False,
        "description": "Given the heads of two singly linked-lists headA and headB, return the node at which the two lists intersect.",
        "examples": [{"input": "intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5]", "output": "Intersected at '8'"}],
        "constraints": ["The number of nodes of listA is in the m.", "The number of nodes of listB is in the n."],
        "starter_code": "def get_intersection_node(headA, headB):\n    pass",
        "solution_hint": "Use two pointers, reset to the other head when reaching the end.",
        "test_cases": [{"input": {"headA": [4,1,8,4,5], "headB": [5,6,1,8,4,5]}, "output": 8}]
    },
    {
        "title": "Min Stack", "difficulty": "medium", "topic": "Stack",
        "tags": ["stack", "design"], "acceptance": "52.5%", "solved": False,
        "description": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.",
        "examples": [{"input": "[\"MinStack\",\"push\",\"push\",\"push\",\"getMin\",\"pop\",\"top\",\"getMin\"]", "output": "[null,null,null,null,-3,null,0,-2]"}],
        "constraints": ["Methods pop, top and getMin operations will always be called on non-empty stacks."],
        "starter_code": "class MinStack:\n    def __init__(self):\n        pass\n    def push(self, val: int) -> None:\n        pass\n    def pop(self) -> None:\n        pass\n    def top(self) -> int:\n        pass\n    def getMin(self) -> int:\n        pass",
        "solution_hint": "Keep track of the minimum value along with each pushed element.",
        "test_cases": []
    },
    {
        "title": "Invert Binary Tree", "difficulty": "easy", "topic": "Trees",
        "tags": ["tree", "dfs", "bfs"], "acceptance": "75.0%", "solved": False,
        "description": "Given the root of a binary tree, invert the tree, and return its root.",
        "examples": [{"input": "root = [4,2,7,1,3,6,9]", "output": "[4,7,2,9,6,3,1]"}],
        "constraints": ["The number of nodes in the tree is in the range [0, 100]."],
        "starter_code": "def invert_tree(root):\n    pass",
        "solution_hint": "Swap the left and right children recursively.",
        "test_cases": [{"input": {"root": [4,2,7,1,3,6,9]}, "output": [4,7,2,9,6,3,1]}]
    },
    {
        "title": "Merge k Sorted Lists", "difficulty": "hard", "topic": "Linked List",
        "tags": ["linked list", "divide and conquer", "heap (priority queue)"], "acceptance": "50.5%", "solved": False,
        "description": "You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.",
        "examples": [{"input": "lists = [[1,4,5],[1,3,4],[2,6]]", "output": "[1,1,2,3,4,4,5,6]"}],
        "constraints": ["k == lists.length", "0 <= k <= 10^4"],
        "starter_code": "def merge_k_lists(lists):\n    pass",
        "solution_hint": "Use a min-heap to keep track of the smallest node among the k lists.",
        "test_cases": [{"input": {"lists": [[1,4,5],[1,3,4],[2,6]]}, "output": [1,1,2,3,4,4,5,6]}]
    },
    {
        "title": "Rotate Image", "difficulty": "medium", "topic": "Matrix",
        "tags": ["array", "math", "matrix"], "acceptance": "72.0%", "solved": False,
        "description": "You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).",
        "examples": [{"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[[7,4,1],[8,5,2],[9,6,3]]"}],
        "constraints": ["n == matrix.length == matrix[i].length", "1 <= n <= 20"],
        "starter_code": "def rotate(matrix):\n    pass",
        "solution_hint": "Transpose the matrix, then reverse each row.",
        "test_cases": [{"input": {"matrix": [[1,2,3],[4,5,6],[7,8,9]]}, "output": [[7,4,1],[8,5,2],[9,6,3]]}]
    },
    {
        "title": "Group Anagrams", "difficulty": "medium", "topic": "Arrays & Hashing",
        "tags": ["array", "hash table", "string", "sorting"], "acceptance": "66.5%", "solved": False,
        "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
        "examples": [{"input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]"}],
        "constraints": ["1 <= strs.length <= 10^4"],
        "starter_code": "def group_anagrams(strs):\n    pass",
        "solution_hint": "Use a hash map where the key is the sorted string and the value is a list of anagrams.",
        "test_cases": [{"input": {"strs": ["eat","tea","tan","ate","nat","bat"]}, "output": [["eat","tea","ate"],["tan","nat"],["bat"]]}]
    },
    {
        "title": "Maximum Subarray", "difficulty": "medium", "topic": "Dynamic Programming",
        "tags": ["array", "divide and conquer", "dynamic programming"], "acceptance": "50.0%", "solved": False,
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "examples": [{"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6"}],
        "constraints": ["1 <= nums.length <= 10^5"],
        "starter_code": "def max_sub_array(nums):\n    pass",
        "solution_hint": "Kadane's algorithm: track the current sum and max sum.",
        "test_cases": [{"input": {"nums": [-2,1,-3,4,-1,2,1,-5,4]}, "output": 6}]
    },
    {
        "title": "Jump Game", "difficulty": "medium", "topic": "Greedy",
        "tags": ["array", "dynamic programming", "greedy"], "acceptance": "38.5%", "solved": False,
        "description": "You are given an integer array nums. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position. Return true if you can reach the last index, or false otherwise.",
        "examples": [{"input": "nums = [2,3,1,1,4]", "output": "true"}],
        "constraints": ["1 <= nums.length <= 10^4"],
        "starter_code": "def can_jump(nums):\n    pass",
        "solution_hint": "Keep track of the furthest index reachable.",
        "test_cases": [{"input": {"nums": [2,3,1,1,4]}, "output": True}]
    },
    {
        "title": "Merge Intervals", "difficulty": "medium", "topic": "Arrays & Hashing",
        "tags": ["array", "sorting"], "acceptance": "46.0%", "solved": False,
        "description": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "examples": [{"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]"}],
        "constraints": ["1 <= intervals.length <= 10^4"],
        "starter_code": "def merge(intervals):\n    pass",
        "solution_hint": "Sort intervals by start time, then merge overlapping ones.",
        "test_cases": [{"input": {"intervals": [[1,3],[2,6],[8,10],[15,18]]}, "output": [[1,6],[8,10],[15,18]]}]
    },
    {
        "title": "Insert Interval", "difficulty": "medium", "topic": "Arrays & Hashing",
        "tags": ["array"], "acceptance": "39.5%", "solved": False,
        "description": "You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi] represent the start and the end of the ith interval and intervals is sorted in ascending order by starti. You are also given an interval newInterval = [start, end] that represents the start and end of another interval. Insert newInterval into intervals such that intervals is still sorted in ascending order by starti and intervals still does not have any overlapping intervals (merge overlapping intervals if necessary). Return intervals after the insertion.",
        "examples": [{"input": "intervals = [[1,3],[6,9]], newInterval = [2,5]", "output": "[[1,5],[6,9]]"}],
        "constraints": ["0 <= intervals.length <= 10^4"],
        "starter_code": "def insert(intervals, new_interval):\n    pass",
        "solution_hint": "Find the correct position, merge overlapping intervals.",
        "test_cases": [{"input": {"intervals": [[1,3],[6,9]], "new_interval": [2,5]}, "output": [[1,5],[6,9]]}]
    },
    {
        "title": "Unique Paths", "difficulty": "medium", "topic": "Dynamic Programming",
        "tags": ["math", "dynamic programming", "combinatorics"], "acceptance": "63.0%", "solved": False,
        "description": "There is a robot on an m x n grid. The robot is initially located at the top-left corner. The robot tries to move to the bottom-right corner. The robot can only move either down or right at any point in time. Given the two integers m and n, return the number of possible unique paths.",
        "examples": [{"input": "m = 3, n = 7", "output": "28"}],
        "constraints": ["1 <= m, n <= 100"],
        "starter_code": "def unique_paths(m, n):\n    pass",
        "solution_hint": "Use dynamic programming: dp[i][j] = dp[i-1][j] + dp[i][j-1].",
        "test_cases": [{"input": {"m": 3, "n": 7}, "output": 28}]
    },
    {
        "title": "Climbing Stairs", "difficulty": "easy", "topic": "Dynamic Programming",
        "tags": ["math", "dynamic programming", "memoization"], "acceptance": "52.0%", "solved": False,
        "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "examples": [{"input": "n = 2", "output": "2"}],
        "constraints": ["1 <= n <= 45"],
        "starter_code": "def climb_stairs(n):\n    pass",
        "solution_hint": "Fibonacci sequence.",
        "test_cases": [{"input": {"n": 2}, "output": 2}]
    },
    {
        "title": "Set Matrix Zeroes", "difficulty": "medium", "topic": "Matrix",
        "tags": ["array", "hash table", "matrix"], "acceptance": "50.5%", "solved": False,
        "description": "Given an m x n integer matrix matrix, if an element is 0, set its entire row and column to 0's. You must do it in place.",
        "examples": [{"input": "matrix = [[1,1,1],[1,0,1],[1,1,1]]", "output": "[[1,0,1],[0,0,0],[1,0,1]]"}],
        "constraints": ["m == matrix.length", "n == matrix[0].length"],
        "starter_code": "def set_zeroes(matrix):\n    pass",
        "solution_hint": "Use the first row and column to store states.",
        "test_cases": [{"input": {"matrix": [[1,1,1],[1,0,1],[1,1,1]]}, "output": [[1,0,1],[0,0,0],[1,0,1]]}]
    },
    {
        "title": "Search a 2D Matrix", "difficulty": "medium", "topic": "Binary Search",
        "tags": ["array", "binary search", "matrix"], "acceptance": "48.0%", "solved": False,
        "description": "Write an efficient algorithm that searches for a value target in an m x n integer matrix matrix. This matrix has the following properties: Integers in each row are sorted from left to right. The first integer of each row is greater than the last integer of the previous row.",
        "examples": [{"input": "matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3", "output": "true"}],
        "constraints": ["m == matrix.length", "n == matrix[i].length"],
        "starter_code": "def search_matrix(matrix, target):\n    pass",
        "solution_hint": "Treat the 2D matrix as a 1D sorted array and use binary search.",
        "test_cases": [{"input": {"matrix": [[1,3,5,7],[10,11,16,20],[23,30,34,60]], "target": 3}, "output": True}]
    },
    {
        "title": "Sort Colors", "difficulty": "medium", "topic": "Two Pointers",
        "tags": ["array", "two pointers", "sorting"], "acceptance": "58.5%", "solved": False,
        "description": "Given an array nums with n objects colored red, white, or blue, sort them in-place so that objects of the same color are adjacent, with the colors in the order red, white, and blue. We will use the integers 0, 1, and 2 to represent the color red, white, and blue, respectively.",
        "examples": [{"input": "nums = [2,0,2,1,1,0]", "output": "[0,0,1,1,2,2]"}],
        "constraints": ["n == nums.length"],
        "starter_code": "def sort_colors(nums):\n    pass",
        "solution_hint": "Dutch National Flag algorithm using three pointers.",
        "test_cases": [{"input": {"nums": [2,0,2,1,1,0]}, "output": [0,0,1,1,2,2]}]
    },
    {
        "title": "Word Search", "difficulty": "medium", "topic": "Backtracking",
        "tags": ["array", "backtracking", "matrix"], "acceptance": "40.0%", "solved": False,
        "description": "Given an m x n grid of characters board and a string word, return true if word exists in the grid.",
        "examples": [{"input": "board = [[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]], word = \"ABCCED\"", "output": "true"}],
        "constraints": ["m == board.length"],
        "starter_code": "def exist(board, word):\n    pass",
        "solution_hint": "Use DFS with backtracking.",
        "test_cases": [{"input": {"board": [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], "word": "ABCCED"}, "output": True}]
    },
    {
        "title": "Remove Duplicates from Sorted Array", "difficulty": "easy", "topic": "Two Pointers",
        "tags": ["array", "two pointers"], "acceptance": "53.5%", "solved": False,
        "description": "Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. The relative order of the elements should be kept the same. Then return the number of unique elements in nums.",
        "examples": [{"input": "nums = [1,1,2]", "output": "2, nums = [1,2,_]"}],
        "constraints": ["1 <= nums.length <= 3 * 10^4"],
        "starter_code": "def remove_duplicates(nums):\n    pass",
        "solution_hint": "Use two pointers, one for iterating and one for placing unique elements.",
        "test_cases": [{"input": {"nums": [1,1,2]}, "output": 2}]
    },
    {
        "title": "Decode Ways", "difficulty": "medium", "topic": "Dynamic Programming",
        "tags": ["string", "dynamic programming"], "acceptance": "32.5%", "solved": False,
        "description": "A message containing letters from A-Z can be encoded into numbers using the following mapping: 'A' -> \"1\", 'B' -> \"2\", ... 'Z' -> \"26\". To decode an encoded message, all the digits must be grouped then mapped back into letters using the reverse of the mapping above. Given a string s containing only digits, return the number of ways to decode it.",
        "examples": [{"input": "s = \"12\"", "output": "2"}],
        "constraints": ["1 <= s.length <= 100"],
        "starter_code": "def num_decodings(s):\n    pass",
        "solution_hint": "Dynamic programming: dp[i] = ways to decode s[:i].",
        "test_cases": [{"input": {"s": "12"}, "output": 2}]
    },
    {
        "title": "Binary Tree Inorder Traversal", "difficulty": "easy", "topic": "Trees",
        "tags": ["stack", "tree", "depth-first search", "binary tree"], "acceptance": "74.0%", "solved": False,
        "description": "Given the root of a binary tree, return the inorder traversal of its nodes' values.",
        "examples": [{"input": "root = [1,null,2,3]", "output": "[1,3,2]"}],
        "constraints": ["The number of nodes in the tree is in the range [0, 100]."],
        "starter_code": "def inorder_traversal(root):\n    pass",
        "solution_hint": "Use recursion or an iterative approach with a stack.",
        "test_cases": [{"input": {"root": [1,-1,2,3]}, "output": [1,3,2]}]
    },
    {
        "title": "Unique Binary Search Trees", "difficulty": "medium", "topic": "Dynamic Programming",
        "tags": ["math", "dynamic programming", "tree", "binary search tree", "binary tree"], "acceptance": "60.0%", "solved": False,
        "description": "Given an integer n, return the number of structurally unique BST's (binary search trees) which has exactly n nodes of unique values from 1 to n.",
        "examples": [{"input": "n = 3", "output": "5"}],
        "constraints": ["1 <= n <= 19"],
        "starter_code": "def num_trees(n):\n    pass",
        "solution_hint": "Catalan numbers or DP: dp[i] = sum(dp[j-1] * dp[i-j]).",
        "test_cases": [{"input": {"n": 3}, "output": 5}]
    },
    {
        "title": "Validate Binary Search Tree", "difficulty": "medium", "topic": "Trees",
        "tags": ["tree", "depth-first search", "binary search tree", "binary tree"], "acceptance": "32.0%", "solved": False,
        "description": "Given the root of a binary tree, determine if it is a valid binary search tree (BST).",
        "examples": [{"input": "root = [2,1,3]", "output": "true"}],
        "constraints": ["The number of nodes in the tree is in the range [1, 10^4]."],
        "starter_code": "def is_valid_bst(root):\n    pass",
        "solution_hint": "Use DFS, keeping track of min and max valid values for each node.",
        "test_cases": [{"input": {"root": [2,1,3]}, "output": True}]
    },
    {
        "title": "Symmetric Tree", "difficulty": "easy", "topic": "Trees",
        "tags": ["tree", "depth-first search", "breadth-first search", "binary tree"], "acceptance": "54.5%", "solved": False,
        "description": "Given the root of a binary tree, check whether it is a mirror of itself (i.e., symmetric around its center).",
        "examples": [{"input": "root = [1,2,2,3,4,4,3]", "output": "true"}],
        "constraints": ["The number of nodes in the tree is in the range [1, 1000]."],
        "starter_code": "def is_symmetric(root):\n    pass",
        "solution_hint": "Recursively check if left.left == right.right and left.right == right.left.",
        "test_cases": [{"input": {"root": [1,2,2,3,4,4,3]}, "output": True}]
    },
    {
        "title": "Binary Tree Level Order Traversal", "difficulty": "medium", "topic": "Trees",
        "tags": ["tree", "breadth-first search", "binary tree"], "acceptance": "64.5%", "solved": False,
        "description": "Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).",
        "examples": [{"input": "root = [3,9,20,null,null,15,7]", "output": "[[3],[9,20],[15,7]]"}],
        "constraints": ["The number of nodes in the tree is in the range [0, 2000]."],
        "starter_code": "def level_order(root):\n    pass",
        "solution_hint": "Use BFS with a queue, processing nodes level by level.",
        "test_cases": [{"input": {"root": [3,9,20,-1,-1,15,7]}, "output": [[3],[9,20],[15,7]]}]
    },
    {
        "title": "Construct Binary Tree from Preorder and Inorder Traversal", "difficulty": "medium", "topic": "Trees",
        "tags": ["array", "hash table", "divide and conquer", "tree", "binary tree"], "acceptance": "61.0%", "solved": False,
        "description": "Given two integer arrays preorder and inorder where preorder is the preorder traversal of a binary tree and inorder is the inorder traversal of the same tree, construct and return the binary tree.",
        "examples": [{"input": "preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]", "output": "[3,9,20,null,null,15,7]"}],
        "constraints": ["1 <= preorder.length <= 3000"],
        "starter_code": "def build_tree(preorder, inorder):\n    pass",
        "solution_hint": "First element of preorder is root. Find its index in inorder to split left and right subtrees.",
        "test_cases": [{"input": {"preorder": [3,9,20,15,7], "inorder": [9,3,15,20,7]}, "output": [3,9,20,-1,-1,15,7]}]
    },
    {
        "title": "Flatten Binary Tree to Linked List", "difficulty": "medium", "topic": "Trees",
        "tags": ["linked list", "stack", "tree", "depth-first search", "binary tree"], "acceptance": "62.5%", "solved": False,
        "description": "Given the root of a binary tree, flatten the tree into a 'linked list'.",
        "examples": [{"input": "root = [1,2,5,3,4,null,6]", "output": "[1,null,2,null,3,null,4,null,5,null,6]"}],
        "constraints": ["The number of nodes in the tree is in the range [0, 2000]."],
        "starter_code": "def flatten(root):\n    pass",
        "solution_hint": "Use DFS (post-order traversal reversed) to update right pointers and set left to null.",
        "test_cases": [{"input": {"root": [1,2,5,3,4,-1,6]}, "output": [1,-1,2,-1,3,-1,4,-1,5,-1,6]}]
    },
    {
        "title": "Best Time to Buy and Sell Stock II", "difficulty": "medium", "topic": "Greedy",
        "tags": ["array", "dynamic programming", "greedy"], "acceptance": "64.0%", "solved": False,
        "description": "You are given an integer array prices where prices[i] is the price of a given stock on the ith day. On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any time. However, you can buy it then immediately sell it on the same day. Find and return the maximum profit you can achieve.",
        "examples": [{"input": "prices = [7,1,5,3,6,4]", "output": "7"}],
        "constraints": ["1 <= prices.length <= 3 * 10^4"],
        "starter_code": "def max_profit(prices):\n    pass",
        "solution_hint": "Greedy approach: add up all positive differences between consecutive days.",
        "test_cases": [{"input": {"prices": [7,1,5,3,6,4]}, "output": 7}]
    },
    {
        "title": "Longest Consecutive Sequence", "difficulty": "medium", "topic": "Arrays & Hashing",
        "tags": ["array", "hash table", "union find"], "acceptance": "48.5%", "solved": False,
        "description": "Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence. You must write an algorithm that runs in O(n) time.",
        "examples": [{"input": "nums = [100,4,200,1,3,2]", "output": "4"}],
        "constraints": ["0 <= nums.length <= 10^5"],
        "starter_code": "def longest_consecutive(nums):\n    pass",
        "solution_hint": "Use a hash set. For each num, if num - 1 not in set, count consecutive numbers starting from num.",
        "test_cases": [{"input": {"nums": [100,4,200,1,3,2]}, "output": 4}]
    }
]

with open('data/assessment/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The highest ID is 35, let's start from 36
start_id = max([p.get('id', 0) for p in data]) + 1

for i, p in enumerate(new_problems):
    p['id'] = start_id + i
    data.append(p)

with open('data/assessment/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_problems)} new problems to questions.json")
