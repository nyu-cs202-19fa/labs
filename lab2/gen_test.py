#!/usr/bin/python3
# Author: Changgeng Zhao <changgeng@nyu.edu>
"""
Usage: ./gen_test.py

This file generates a folder called "test" that contains all testcases we need.

test
├── files           # contains 2 folders, each of which contains 10 files
├── dirs            # contains a tree-structured folders, used for ./ls -R
├── error           # used to test different type of error and return value
│   ├── noerror         # return 0
│   ├── deniedaccess    # 0-bit
│   ├── notfound        # 1-bit. This folder contains nothing so searching for anything
|   |                   #        in this folder will result an erro
│   └── userid          # 2-bit. Contains unknown userIDs and groupIDs
├── hidden          # contains hidden files and folders
├── links           # soft links, used for extra credit
├── recursive       # recursive self cycle
└── ls-l            # testcases for ./ls -l
    ├── easy            # easy case, for checking the output format
    ├── mode            # all kinds of modes from 000 to 777
    ├── nlink           # check number of hard link
    ├── size            # check file size
    └── userid          # check username

"""

from subprocess import Popen, PIPE
import time
import random

random.seed(202)


def run_command(cmd, ignore_err=False):
    result = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = result.communicate()
    out, err = stdout.decode("utf-8"), stderr.decode("utf-8")
    if not ignore_err and err != "":
        print(err)
        assert(0)
        exit(-1)
    return out


def gen_modes(prefix):
    run_command("mkdir {}".format(prefix))
    for user in range(8):
        for group in range(8):
            for guest in range(8):
                mod = f"{user}{group}{guest}"
                filename = f"{prefix}/test_mod_{mod}"
                run_command(f"touch {filename} && chmod {mod} {filename}")


def gen_dirs(prefix, depth=5):
    if depth <= 0:
        return
    run_command("mkdir {}".format(prefix))
    folder_names = "abcde"
    for name in folder_names:
        # with 30% of possibility we end here, to make a random tree
        if random.randint(0, 99) < 30:
            continue
        gen_dirs(f"{prefix}/folder-{name}", depth-1)


def gen_files(prefix):
    run_command("mkdir {}".format(prefix))
    run_command(f"mkdir {prefix}/folder1")
    for name in range(10):
        run_command(f"echo foobarfoobar > {prefix}/folder1/file-{name}.txt")
    run_command(f"mkdir {prefix}/folder2")
    for name in range(100,120):
        run_command(f"echo foobarfoobar > {prefix}/folder2/file-{name}.txt")


def gen_links(prefix):
    run_command(f"mkdir {prefix}")
    run_command(f"touch {prefix}/file1")
    run_command(f"touch {prefix}/file2")
    run_command(f"touch {prefix}/file3")
    run_command(f"ln -s file3 {prefix}/link1")
    run_command(f"ln -s /dev/null {prefix}/link2")
    run_command(f"ln -s link2 {prefix}/link3")
    run_command(f"ln -s /dev/zero {prefix}/link4")
    run_command(f"ln -s $PWD/{prefix}/link1 $PWD/{prefix}/link5")
    run_command(f"ln $PWD/{prefix}/file2 {prefix}/hardlink")


def gen_ls_l(prefix):
    run_command(f"mkdir {prefix}")

    gen_modes(f"{prefix}/mode")

    run_command(f"mkdir {prefix}/easy")
    run_command(f"touch {prefix}/easy/file1.txt")
    run_command(f"mkdir {prefix}/easy/folder1")

    # folder that contains different users and groups
    run_command(f"mkdir {prefix}/userid")
    run_command(f"touch {prefix}/userid/user1")
    run_command(f"touch {prefix}/userid/user2")
    run_command(f"sudo chown nobody {prefix}/userid/user2")
    run_command(f"touch {prefix}/userid/user3")
    run_command(f"sudo chown www-data {prefix}/userid/user3")
    run_command(f"touch {prefix}/userid/group1")
    run_command(f"touch {prefix}/userid/group2")
    run_command(f"sudo chgrp nogroup {prefix}/userid/group2")
    run_command(f"touch {prefix}/userid/group3")
    run_command(f"sudo chgrp www-data {prefix}/userid/group3")

    run_command(f"mkdir {prefix}/size")
    fname = f"{prefix}/size/test_small.txt"
    run_command(
        f"dd if=/dev/urandom of={fname} bs=512 count=1", ignore_err=True)
    for i in range(10):
        size = random.randint(5 << i, 10 << i)
        fname = f"{prefix}/size/test_{i}.txt"
        run_command(
            f"dd if=/dev/urandom of={fname} bs=1024 count={size}", ignore_err=True)

    run_command(f"mkdir {prefix}/nlink")
    link_folder = f"{prefix}/nlink/links"
    run_command(f"mkdir {link_folder}")
    for i in range(10):
        fname = f"n_{i}.tmp"
        run_command(f"touch {prefix}/nlink/{fname}")
        for j in range(i):
            # hard link
            run_command(
                f"ln {prefix}/nlink/{fname} {link_folder}/{fname}_{j}.link")


def gen_hidden(prefix):
    run_command(f"mkdir {prefix}")
    run_command(f"touch {prefix}/file1")
    run_command(f"touch {prefix}/.file2")
    run_command(f"mkdir {prefix}/dir1")
    run_command(f"mkdir {prefix}/.dir2")
    run_command(f"touch {prefix}/.dir2/.file3")
    run_command(f"touch {prefix}/.dir2/file4")


def gen_recursive(prefix):
    run_command(f"mkdir {prefix}")
    run_command(f"mkdir {prefix}/dir1")
    run_command(f"ln -s .. {prefix}/dir1/dir2")


def gen_error(prefix):
    run_command(f"mkdir {prefix}")

    # no error
    run_command(f"mkdir {prefix}/noerror")
    run_command(f"touch {prefix}/noerror/dummy.txt")

    # empty folder, so anything should not be found in it
    run_command(f"mkdir {prefix}/notfound")

    # change the mod to 000 so access will be denied
    run_command(f"mkdir {prefix}/deniedaccess")
    for mod in ['000', '111', '666', '555']:
        run_command(f"mkdir {prefix}/deniedaccess/{mod}")
        run_command(f"touch {prefix}/deniedaccess/{mod}/foo.txt")
        run_command(f"chmod {mod} {prefix}/deniedaccess/{mod}")

    # arbitrary userID and groupID that shouldn't exist
    run_command(f"mkdir {prefix}/userid")
    run_command(f"touch {prefix}/userid/whoisthis")
    run_command(f"sudo chown 3321:2212 {prefix}/userid/whoisthis")
    run_command(f"touch {prefix}/userid/whoisthis-1")
    run_command(f"sudo chown 8761:1203 {prefix}/userid/whoisthis-1")


def main():
    print("generating test files...")
    test_folder_name = "test"
    run_command(f"sudo rm -rf {test_folder_name} || true")
    run_command(f"mkdir {test_folder_name}")

    gen_dirs(test_folder_name + "/dirs")
    gen_files(test_folder_name + "/files")
    gen_links(test_folder_name + "/links")
    gen_ls_l(test_folder_name + "/ls-l")
    gen_hidden(test_folder_name + "/hidden")
    gen_error(test_folder_name + "/error")
    gen_recursive(test_folder_name + "/recursive")

    # print(run_command("tree test -a"))
    print("[Done] generating test files")


if __name__ == "__main__":
    main()
