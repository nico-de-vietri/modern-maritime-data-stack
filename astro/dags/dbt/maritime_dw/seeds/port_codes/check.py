with open("port_codes.csv", "r") as f:
    for i, line in enumerate(f, 1):
        cols = line.strip().split(",")
        if len(cols) != 4:
            print(f"Line {i} has {len(cols)} columns: {line}")
