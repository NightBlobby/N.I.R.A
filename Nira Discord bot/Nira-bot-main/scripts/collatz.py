def is_collatz_conjecture(number):
    steps = []
    while number > 1:
        steps.append(number)
        if number % 2 == 0:
            number //= 2
        else:
            number = 3 * number + 1
    return number == 1
