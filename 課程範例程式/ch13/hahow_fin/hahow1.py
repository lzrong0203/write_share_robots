def function1():
    print("FUN1")


def function2():
    print("FUN2")


class Class1:

    def __init__(self, str1=None):
        print("CLASS1", str1)


if __name__ == "__main__":
    function1()
    function2()
    cls1 = Class1()
