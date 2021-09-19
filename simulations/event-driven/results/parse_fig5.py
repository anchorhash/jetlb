"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

with open("anchor_fig_5.txt") as f:

    lines = f.readlines()

    sline = lines[1].split()
    for arg in sline[1:]:
        sarg = arg.split(":")
        print(sarg[0], end=",")
    print("JET broken connections", end=",")
    print("FCT broken connections", end=",")
    print("maximum over-subscription", end=",")
    print("total connections")

    for line in lines:
        if line.startswith("Parameters"):
            sline = line.split()
            for arg in sline:
                sarg = arg.split(":")
                print(sarg[1], end="")

        if line.startswith("JET broken connections"):
            sarg = line.split(":")
            print(sarg[1].strip(), end=",")

        if line.startswith("FCT broken connections"):
            sarg = line.split(":")
            print(sarg[1].strip(), end=",")

        if line.startswith("maximum over-subscription"):
            sarg = line.split()
            print(sarg[3].strip(), end=",")

        if line.startswith("total connections"):
            sarg = line.split()
            print(sarg[2].strip())
