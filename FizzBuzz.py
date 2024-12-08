def FizzBuzz(N):
    fizz = 1 # 3
    buzz = 1 # 5

    for i in range(1, N+1):
        if fizz == 3:
            fizz = 0
        if buzz == 5:
            buzz = 0
        # counter is faster than modulus
        # fizz = (i % 3) == 0
        # buzz = (i % 5) == 0
        if fizz == 0 and buzz == 0:
            print("FizzBuzz")
        elif buzz == 0:
            print("Buzz")
        elif fizz == 0:
            print("Fizz")
        else:
            print(i)
        fizz += 1
        buzz += 1

def main():
    FizzBuzz(21)

if __name__ == "__main__":
    main()
