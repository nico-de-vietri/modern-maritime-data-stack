import csv

input_file = "port_codes.csv"
output_file = "port_codes_fixed.csv"

with open(input_file, "r", newline="", encoding="utf-8") as infile, open(
    output_file, "w", newline="", encoding="utf-8"
) as outfile:

    # Read the CSV with a basic split (not robust, but for fixing this specific problem)
    lines = infile.readlines()
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    for line in lines:
        # Split on comma first, naive approach
        parts = line.strip().split(",")

        # If more than 4 parts, some commas inside fields
        if len(parts) > 4:
            # The first two columns: country_code, location
            first_two = parts[0:2]

            # The last column is coordinates (optional, might be empty)
            last = parts[-1]

            # Everything between is part of the port name but split by commas
            middle = parts[2:-1]

            # Join middle back with comma, then strip spaces
            name = ",".join(middle).strip()

            # Write row with 4 columns: country_code, location, name, coordinates
            writer.writerow([first_two[0], first_two[1], name, last])
        else:
            # Normal row, just write as is
            writer.writerow(parts)
