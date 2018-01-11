#!/bi//python
message = raw_input("Enter a message: ")
count = raw_input("Number of repeats [1]: ").strip()

if count:
    count = int(count)
else:
    count = 1

def multi_echo(message, count):
    while count > 0:
        print(message)
        count -= 1

multi_echo(message, count)
