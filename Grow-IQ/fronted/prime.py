n = int(input("num : "))
for i in range(2, n//2):
    if n % i == 0:
        print("Not a Prime")
        break
else:
    print("Prime")