import collections
from abc import ABC, abstractmethod

# Abstract base class
class SlidingWindowSolver(ABC):
    @abstractmethod
    def on_grow(self, sliding_window):
        pass
    @abstractmethod
    def on_shrink(self, element_removed, sliding_window):
        pass
    @abstractmethod
    def get_solution(self):
        pass
    def fixed_size(self):
        return None

class SlidingWindow:
    def __init__(self, array, solver):
        if not isinstance(solver, SlidingWindowSolver):
            raise TypeError("The object must be an instance of SlidingWindowSolver or its subclass.")
        self.solver = solver
        self.array = array
        self.starting_size = 0
        self.left_index = 0
        self.right_index = 0
        self.fixed = False
        if solver.fixed_size() is not None:
            self.fixed = True
            self.fixed_size = solver.fixed_size()

    def slide_right(self):
        if self.right_can_advance():
            self.right_index += 1
            return self.solver.on_grow(self)
        return False
    
    def slide_left(self):
        if self.left_can_advance():
            element = self.get_left_element()
            self.left_index += 1
            return self.solver.on_shrink(element, self)
        return False
    
    def get_right_element(self):
        return self.array[self.right_index]

    def get_left_element(self):
        return self.array[self.left_index]

    def get_right_index(self):
        return self.right_index

    def get_left_index(self):
        return self.left_index
    
    def right_can_advance(self):
        return self.right_index < len(self.array)-1

    def left_can_advance(self):
        return self.left_index < self.right_index
    
    def process(self):
        # get that first element
        self.solver.on_grow(self)

        if self.fixed:
            if self.fixed_size >= len(self.array):
                raise IndexError("The fixed size of the window is larger than the array provided.")
            while self.right_index < self.fixed_size-1:
                self.slide_right()
            self.slide_left()
        
        while self.right_can_advance():
            while self.right_can_advance() and self.slide_right():
                pass
            while self.left_can_advance() and self.slide_left():
                pass
        return self.solver.get_solution()

class SmallestSubarraySumGreaterSolver(SlidingWindowSolver):
    def __init__(self, target_sum):
        self.target_sum = target_sum
        self.current_sum = 0
        self.solution = None

    def evaluate(self, sliding_window):
        end = sliding_window.get_right_index()
        start = sliding_window.get_left_index()
        size = (end - start) + 1
        print(f"current sum {self.current_sum} is "
              f"{"greater" if self.current_sum > self.target_sum else "less than or equal"}"
              f" than {self.target_sum}")

        # save a better solution
        if ((self.current_sum > self.target_sum) and
            ((self.solution is None) or (self.solution['size'] > size))):
            old_solution = self.solution 
            self.solution = {'start': start, 'end': end, 'size': size}
            print(f"{self.solution} which is a smaller solution than {old_solution}")
        return self.current_sum > self.target_sum

    def on_grow(self, sliding_window):
        element_added = sliding_window.get_right_element()
        # self.cache.append(element_added)
        self.current_sum += element_added
        # if len(self.cache) != self.window_size:
        #     return None
        condition_met = self.evaluate(sliding_window)
        print(f"Window grew, and the evaluation is {condition_met}", end = "")
        # return here true if we are to continue growing:
        # stop growing if size is max
        if not sliding_window.right_can_advance():
            print(f", limit met will shrink")
            return False
        # stop growing if the condition is met
        # grow more if the condition is not met (need more numbers to reach larger sum)
        print(f", will {"shrink" if condition_met else "grow"}")
        return not condition_met

    def on_shrink(self, element_removed, sliding_window):
        self.current_sum -= element_removed
        condition_met = self.evaluate(sliding_window)
        print(f"Window shrank, and the evaluation is {condition_met}", end = "")
        # return here true if we are to continue shrinking
        # stop shrinking if size is minimum
        if not sliding_window.left_can_advance():
            print(f", limit met will grow")
            return False
        # stop shrinking if the condition is not met
        # shrink more if the condition is met (can we keep the sum with fewer numbers)
        print(f", will {"shrink" if condition_met else "grow"}")
        return condition_met

    def get_solution(self):
        return self.solution

class LargestSubarraySumSmallerSolver(SmallestSubarraySumGreaterSolver):
    def evaluate(self, sliding_window):
        end = sliding_window.get_right_index()
        start = sliding_window.get_left_index()
        size = (end - start) + 1
        print(f"current sum {self.current_sum} is "
              f"{"greater than or equal" if self.current_sum >= self.target_sum else "less"}"
              f" than {self.target_sum}")

        # save a better solution
        if ((self.current_sum < self.target_sum) and
                ((self.solution is None) or (self.solution['size'] < size))):
            old_solution = self.solution
            self.solution = {'start': start, 'end': end, 'size': size}
            print(f"{self.solution} which is a longer solution than {old_solution}")
        return not (self.current_sum < self.target_sum)

class FixedSizeSlidingWindowAdapter(SlidingWindowSolver):
    def __init__(self, window_size):
        self.window_size = window_size
        self.cache = collections.deque()

    def fixed_size(self):
        return self.window_size

    @abstractmethod
    def evaluate(self, sliding_window):
        pass

    @abstractmethod
    def on_slide(self, element_added, sliding_window):
        pass

    def on_grow(self, sliding_window):
        element_added = sliding_window.get_right_element()
        if len(self.cache) < self.window_size-1:
            self.on_slide(element_added, sliding_window)
            self.cache.append(element_added)
            return True # keep growing
        elif sliding_window.get_left_index() == 0:
            self.on_slide(element_added, sliding_window)
            self.cache.append(element_added)
            return False #start sliding
        else:
            condition_met = self.on_slide(element_added, sliding_window)
            self.cache.append(element_added)
            print(f"Window slid, and the evaluation is {condition_met}")
            return False # slide

    def on_shrink(self, element_removed, sliding_window):
        self.cache.popleft() # I can see if the element popped is the one removed for a sanity check
        return False # 'grow' (a grow then a shrink is a slide)

# Given an array of integers a, your task is to find how many of its 
# contiguous subarrays of length m contain a pair of integers with a sum equal to k.
class CountSubarrayWithSumSolver(FixedSizeSlidingWindowAdapter):
        def __init__(self, window_size, target_sum):
            super().__init__(window_size)
            self.target_sum = target_sum
            self.solution = []
            
        def evaluate(self, sliding_window):
            return None
        
        def on_slide(self, element_added, sliding_window):
            # the cache has all but the element added
            target_dif = self.target_sum - element_added
            if self.cache.count(target_dif) > 0:
                target_index = self.cache.index(target_dif)
                self.solution.append((target_index + sliding_window.get_left_index(), sliding_window.get_right_index()))
            return False

        def get_solution(self):
            return self.solution


def main():
    # Code to execute
    print("Running Sliding Window function...")
    # Given an array arr[] of integers and a number k, the task is to find the 
    # smallest subarray with a sum greater than the given value.
    a = [2, 3, 5, 3, 5, 8, 5, 11, 7]
    k = 10

    solver = SmallestSubarraySumGreaterSolver(k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"The solution found is {solution}\n")

    k = 1000
    solver = SmallestSubarraySumGreaterSolver(k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"The solution found is {solution}\n")

    a = [2, 11, 5, 3, 5, 8, 5, 2, 7]
    k = 25

    solver = LargestSubarraySumSmallerSolver(k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"The solution found is {solution}\n")


    # Given an array of integers a, your task is to find how many of its 
    # contiguous subarrays of length m contain a pair of integers with a sum equal to k.
    a = [2, 4, 7, 5, 3, 5, 8, 5, 1, 7]
    m = 4
    k = 10

    solver = CountSubarrayWithSumSolver(m, k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"For {a}, length {m}\nthe solution found is: {solution}")
    for s in solution:
        x = s[0]
        y = s[1]
        print(f"a[{x}] {a[x]} + a[{y}] {a[y]} = {k}")

    a = [2, 8, 5, 5, 3, 7, 3, 5, 1, 7]
    m = 4
    k = 10

    solver = CountSubarrayWithSumSolver(m, k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"For {a}, length {m}\nthe solution found is: {solution}")
    for s in solution:
        x = s[0]
        y = s[1]
        print(f"a[{x}] {a[x]} + a[{y}] {a[y]} = {k}")

    a = [5, 2, 8, 5, 5, 3, 7, 3, 5, 1, 7]
    m = 4
    k = 10

    solver = CountSubarrayWithSumSolver(m, k)
    sw = SlidingWindow(a, solver)
    solution = sw.process()
    print(f"For {a}, length {m}\nthe solution found is: {solution}")
    for s in solution:
        x = s[0]
        y = s[1]
        print(f"a[{x}] {a[x]} + a[{y}] {a[y]} = {k}")
    
if __name__ == "__main__":
    main()
