#!/bin/env python3

import os

def main():
    # env variables from k8s
    kdp_input = os.getenv('KDP_INPUT')

    with open('kdp_output.json', 'w') as f:
        f.write(kdp_input)

if __name__ == "__main__":
    main()