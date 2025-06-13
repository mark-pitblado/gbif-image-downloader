def read_integers_to_set(filename):
    with open(filename, "r") as file:
        return {int(line.strip()) for line in file}
