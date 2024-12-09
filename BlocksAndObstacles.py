'''Given an infinite integer number line, you would like to build some blocks and obstacles on it. Specifically, you have to implement code which supports two types of operations:

[1, x] - builds an obstacle at coordinate x along the number line. It is guaranteed that coordinate x does not contain any obstacles when the operation is performed.
[2, x, size] - checks whether it's possible to build a block of size size which ends immediately before x on the number line. For example, if x = 6 and size = 2, this operation checks coordinates 4 and 5. Produces "1" if it is possible, i.e. if there are no obstacles at the specified coordinates, or produces "0" otherwise. Please note that this operation does not actually build the block, it only checks whether a block can be built.
Given an array of operations containing both types of operations described above, your task is to return a binary string representing the outputs for all [2, x, size] operations.

Example

For

operations = [[1, 2],
              [1, 5],
              [2, 5, 2],
              [2, 6, 3],
              [2, 2, 1],
              [2, 3, 2]]
the output should be solution(operations) = "1010".

Explanation:

Let's consider all operations:

[1, 2] - builds an obstacle at coordinate 2.
[1, 5] - builds an obstacle at coordinate 5.
[2, 5, 2] - checks and produces "1" as it is possible to build a block occupying coordinates 3 and 4.
[2, 6, 3] - checks and produces "0" as it is not possible to build a block occupying coordinates 3, 4, and 5, because there is an obstacle at coordinate 5.
[2, 2, 1] - checks and produces "1" as it is possible to build a block occupying coordinate 1.
[2, 3, 2] - checks and produces "0" as it is not possible to build a block occupying coordinates 1 and 2 because there is an obstacle at coordinate 2.
So the output is "1010".

Expand to see the example video.

Note: If you are not able to see the video, use this link to access it.

Input/Output

[execution time limit] 4 seconds (py)

[memory limit] 1 GB

[input] array.array.integer operations

An array of integer arrays representing one of the two types of operations described above. All coordinates within operations are within the interval [-109, 109]. The size from the second type of operations are positive integers which do not exceed 109.

Guaranteed constraints:
1 ≤ operations.length ≤ 105.

[output] string

A binary string representing the outputs for all [2, x, size] operations.

[Python 2] Syntax Tips
'''
# Prints help message to the console
# Returns a string
def helloWorld(name):
    print "This prints to the console when you Run Tests"
    return "Hello, " + name

