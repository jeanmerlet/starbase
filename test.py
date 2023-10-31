class A:
    def __init__(self):
        print('A')

class B:
    def __init__(self):
        print('B')

class C(A):
    def __init__(self):
        super().__init__()

    def perform(self):
        pass


test = C()
