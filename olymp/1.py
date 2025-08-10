a, b, c = map(int, input().split())
if b <= a - (a/c):
    print(-1)
else:
    print(b/((a/c) - a + b))