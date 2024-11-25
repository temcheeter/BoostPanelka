# project strings

# 2024.11.07 - 740
# print(115 + 1 + 29 + 190 + 5 + 120 + 90 + 190)

# ege
print('x y z w')
values = []
for x in range(2):
    for y in range(2):
        for z in range(2):
            for w in range(2):
                func = ((not(x) and (y)) or (not(z) or not(w))) and ((not(w) or x) or y)
                if func == False:
                    print(x, y, z, w)
                    # values.append((x, y, z, w))
