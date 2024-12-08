from collections import Counter
from itertools import combinations_with_replacement
import bisect

def arithmeticSequenceSum(terms, start = 1, increment = 1):
    return int((terms/2) * ((2*start)+(terms-1)*increment))

# given a sequence of numbers determine if it is possible to have a strictly increasing array
# by only removing one element
def is_strictly_increasing_array_removing_one_element(array):
    removed_index = -1
    failed = False
    N = len(array)
    if N < 2:
        return not failed
   
    for i in range(2, N):
        a = array[i-2]
        b = array[i-1]
        c = array[i]

        if  i-2 <= removed_index <= i:
            a = array[i-3]
            if removed_index == i-1:
                b = array[i-2]
            if removed_index == i:
                c = array[i-1]
            
        if a < b < c:   # 1, 2, 3
            continue
        if a >= b >= c: # 3, 2, 1
            failed = True
            break
        if a < b >= c: # 1, 3, 2 or 2, 3, 1
            if removed_index != -1:
                failed = True
                break
            removed_index = i-1
        if a >= b < c: # 2, 1, 3 or 3, 1, 2
            if removed_index != -1:
                failed = True
                break
            removed_index = i-2
    return not failed, removed_index
        
def print_is_strictly_increasing_array_removing_one_element( array ):
    success, index = is_strictly_increasing_array_removing_one_element(array)
    print(array)
    if success:
        if index != -1:
            print(f"increasing array worked by removing {array[index]} at index:{index}")
        else:
            print(f"increasing array worked on its own")
    else:
        if index != -1:
            print(f"increasing array failed, even by removing {array[index]} at index:{index}")
        else:
            print(f"increasing array failed")

# Given an integer array arr, and an integer target, return the number of tuples (i, j, k) 
# such that i < j < k and arr[i] + arr[j] + arr[k] == target.
#
# As the answer can be very large, return it modulo 109 + 7.
def threeSumMulti( arr, target):
    """
    :type arr: List[int]
    :type target: int
    :rtype: int
    """
    MOD = 10**9 + 7

    count = Counter(arr)
    keys = sorted(count.keys())
    result = 0

    for i, x in enumerate(keys):
        for j, y in enumerate(keys[i:], start=i):  # Ensure y >= x
            z = target - x - y
            if z < y:  # Ensure z >= y
                break  # ensuring the order of the values removes the duplicate combinations
            if z in count:
                if x == y == z:  # All three numbers are the same
                    result += count[x] * (count[x] - 1) * (count[x] - 2) // 6
                elif x == y:  # First two numbers are the same
                    result += count[x] * (count[x] - 1) // 2 * count[z]
                elif y == z:  # Last two numbers are the same
                    result += count[x] * count[y] * (count[y] - 1) // 2
                else:  # All three numbers are different
                    result += count[x] * count[y] * count[z]
    # m = {}
    # result = 0
    # N = len(arr)
    # for i in range(N):
    #     result = result + m.get( target - arr[i], 0)
    #     for j in range(i):
    #         d = m.get(arr[i] + arr[j], 0) + 1
    #         m[arr[i] + arr[j]] = d
    return result % MOD


def findPairs(nums, k):
    """
    :type nums: List[int]
    :type k: int
    :rtype: int
    """
    count = Counter(nums)
    keys = sorted(count.keys())
    result = 0
    if k == 0:
        for i, x in enumerate(keys):
            if count.get(x, 0) > 1: # any duplicate counts
                result += 1
    else:
        for i, x in enumerate(keys):
            y = x + k
            if y in count: #I have an x and a y so count the unique solution
                result += 1
    return result


class SnapshotArray:
    SNAP =0
    
    def __init__(self, length: int):
        # Initialize an array where each index has a list of (snap_id, value) tuples.
        # Initially, every index starts with the value 0 at snap_id 0.
        self.array = [[(0, 0)] for _ in range(length)]  # [(snap_id, value)] starting with (0, 0)
        self.snap_id = 0  # Counter for the snapshots

    def set(self, index: int, val: int) -> None:
        # We append a tuple (snap_id, value) for each set operation
        # Check the last snap_id in the list of tuples for this index
        if self.array[index][-1][self.SNAP] != self.snap_id:
            self.array[index].append((self.snap_id, val))
        else:
            self.array[index][-1] = (self.snap_id, val)

    def snap(self) -> int:
        # Increment the snap_id and return the current snap_id.
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index: int, snap_id: int) -> int:
        # We perform a binary search to find the largest snap_id <= requested snap_id
        # Using bisect_right to find the first element that is strictly greater than snap_id
        snapshots = self.array[index]
        # Find the position where snap_id would go, and get the previous snapshot if it exists.
        pos = bisect.bisect_right(snapshots, (snap_id, float('inf'))) - 1
        return snapshots[pos][1]

# You are given an array of strings words. Each element of words consists of two lowercase English letters.
# 
# Create the longest possible palindrome by selecting some elements from words and concatenating them in any order. 
# Each element can be selected at most once.
# 
# Return the length of the longest palindrome that you can create. If it is impossible to create any palindrome, return 0.
# 
# A palindrome is a string that reads the same forward and backward.
def longest_palindrome(words):
    solution = 0
    # find frequencies of the 'words'
    count = Counter(words)
    keys = list(count.keys())
    mirrors = {}
    palindrome = set()
    def find_mirrors(word):
        word_reverse = word[1] + word[0]
        if word_reverse == word:
            palindrome.add(word)
        elif word_reverse in keys and word_reverse not in mirrors:
            mirrors[word] = word_reverse

    list(map(find_mirrors, keys))
    for p in palindrome:
        if count[p] & 1:
            solution += 1
            break
    for p in palindrome:
        solution += count[p] & ~1
    for m in mirrors:
        size = min(count[m], count[mirrors[m]])
        solution += size*2 # count each word, mirror and original
    return solution *2 # words are 2 long
    
    
def main():

    words = ["dd","aa","bb","dd","aa","dd","bb","dd","aa","cc","bb","cc","dd","cc"]
    print(f"longest_palindrome of {words} is {longest_palindrome(words)}")

    words = ["cc","ll","xx"]
    print(f"longest_palindrome of {words} is {longest_palindrome(words)}")

    words = ["lc","cl","gg"]
    print(f"longest_palindrome of {words} is {longest_palindrome(words)}")

    # Create SnapshotArray of length 3
    snapshotArr = SnapshotArray(3)
    
    # Set values
    snapshotArr.set(0, 5)    # Set index 0 to 5
    snapshotArr.set(1, 10)   # Set index 1 to 10
    
    # Take a snapshot
    snap_id_1 = snapshotArr.snap()  # snap_id_1 = 0
    
    # Set new values
    snapshotArr.set(0, 6)    # Set index 0 to 6
    snapshotArr.set(2, 15)   # Set index 2 to 15
    
    # Take another snapshot
    snap_id_2 = snapshotArr.snap()  # snap_id_2 = 1
    
    # Get values at certain snapshots
    print(snapshotArr.get(0, snap_id_1))  # Output: 5 (value at index 0 in snap 0)
    print(snapshotArr.get(1, snap_id_1))  # Output: 10 (value at index 1 in snap 0)
    print(snapshotArr.get(2, snap_id_2))  # Output: 15 (value at index 2 in snap 1)
    
    # Get value at a non-existent snap_id (should return the most recent value before snap_id 2)
    print(snapshotArr.get(0, 3))  # Output: 6 (the most recent value for index 0)

    nums = [3,1,4,1,5]
    k = 2
    # findPairs(nums, k)


    nums = [1,3,1,5,4]
    k = 0
    findPairs(nums, k)
    N = 3
    print(f"sum 1-{N} {arithmeticSequenceSum(N)}")
    N = 10
    print(f"sum 1-{N} {arithmeticSequenceSum(N)}")
    N = 9
    print(f"sum 1-{N} {arithmeticSequenceSum(N)}")

    array = [n for n in range(10)]
    print_is_strictly_increasing_array_removing_one_element(array)

    array = [10-n for n in range(10)]
    print_is_strictly_increasing_array_removing_one_element(array)

    array = [1,2,3,4,7,5,6,7,8,9]
    print_is_strictly_increasing_array_removing_one_element(array)



    array = [1,2,3,4,7,5,6,7,8,9,0]
    print_is_strictly_increasing_array_removing_one_element(array)

    array = [1,1,2,2,3,3,4,4,5,5]
    target = 8
    print(f"\nthreeSumMulti")
    print(array)
    print(f"target {target}")
    print(threeSumMulti( array, target))

    array = [0, 0, 0]
    target = 0
    print(f"\nthreeSumMulti")
    print(array)
    print(f"target {target}")
    print(threeSumMulti( array, target))

    
if __name__ == "__main__":
    main()
