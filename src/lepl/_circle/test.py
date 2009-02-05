
from first import First
from second import Second

if __name__ == '__main__':
    f1 = First(1)
    print(f1)
    s2 = Second(2)
    print(s2)
    f3 = f1.first(3)
    print(f3)
    s4 = f1.second(4)
    print(s4)
    