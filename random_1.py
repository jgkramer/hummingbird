

for m in range(2022):
    for n in range(m):
        if (m*m - m*n - n*n)**2 == 1:
            print(m, n, m*m + n*n)
