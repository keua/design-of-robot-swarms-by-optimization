#!/usr/bin/env python

import sys

def convert_file(source_file_name, target_file_name):
    with open(target_file_name, 'w') as target:
        with open(source_file_name, 'r') as source:
            # read header
            header = source.readline().split(" ")
            # print(header)
            for line in source:
                elements = line.split(" ")
                # print(elements)
                for i in range(2, len(elements)):
                    if "NA" not in elements[i]:  # should cover NA, <NA> and NA\r\n
                        target.write("--{} {} ".format(header[i-1].lower(), elements[i]))
                target.write("\n")


if __name__ == "__main__":
    convert_file(sys.argv[1], sys.argv[2])
