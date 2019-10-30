#!/usr/bin/python3
from subprocess import Popen, PIPE
import itertools
import sys
import os

all_fileds = ['mode', 'nlink', 'user', 'group', 'size', 'mtime', 'fname']
ls_exec = os.getenv('LS_STUDENT')
if ls_exec == None:
    ls_exec = './ls'

# ------ Helper functions ------


class FormatError(Exception):
    pass


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def run_command(cmd):
    result = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = result.communicate()
    return stdout.decode("utf-8"), stderr.decode("utf-8"), result.returncode


def assert_err(err):
    if err != '':
        print("failed:", err)
        exit(-1)


# Run student version of ls, get the output
def run_ls_student(flags, files):
    cmd = f"{ls_exec} {flags} " + ' '.join(files)
    print("[Testing] " + cmd)
    try:
        out, err, rc = run_command(cmd)
    except UnicodeDecodeError:
        print("[ERROR] decode error")
        return '', 'decodeerror'
    if err != '':
        return '', 'error'
    return out, rc

# Run ls-solution, get the output


def run_ls_solution(flags, files):
    cmd = f"./ls-solution {flags} " + ' '.join(files)
    try:
        out, err, rc = run_command(cmd)
    except UnicodeDecodeError:
        print("decode error")
        return '', -1
    assert_err(err)
    return out, rc


def parse_cs202_output(output, omit_slash, list_long=False, recursive=False):
    lines = []

    for line in output.split('\n'):
        line = line.replace('\t', ' ')
        if line.replace(' ', '') == '' or line.replace(' ', '')[-1] == ':':
            continue
        if line[:4] == 'ls: ':
            continue
        if omit_slash and line[-1] == '/':
            line = line[:-1]
        if list_long:
            words = line.split()
            if len(words) < 5:
                print(len(words))
                continue
            res = {}
            i = 0
            res['mode'] = words[i]
            i += 1
            if RepresentsInt(words[i]):
                res['nlink'] = words[i]
                i += 1
            else:
                res['nlink'] = ''
            res['user'] = words[i]
            i += 1
            res['group'] = words[i]
            i += 1
            res['size'] = words[i]
            i += 1
            res['mtime'] = ' '.join(words[i:-1])
            res['fname'] = words[-1].rstrip('\x00')

            lines.append(res)
        else:
            lines.append({'fname': line})
    return lines


def sort_by_fname(lines):
    return sorted(lines, key=lambda i: i['fname'])


def check_help_message():
    out, rc = run_ls_student("--help", [])
    if rc != 0:
        print("ERROR: return code is not 0 when calling './ls --help'")
        return 0
    flags_needed = "alR"
    for flag in flags_needed:
        if f'-{flag}' not in out:
            print(f"ERROR: -{flag} doesn't exist in ./ls --help")
            return 0
    return 1


def check_link_extra():
    out, _ = run_ls_student("-l", ['test/links'])
    out_solution, _ = run_ls_solution("-l", ['test/links'])
    arrow_diff = 0
    # very ugly. check the number of arrows
    for line in out.split('\n'):
        if '->' in line:
            arrow_diff += 1
    for line in out_solution.split('\n'):
        if '->' in line:
            arrow_diff -= 1

    if arrow_diff != 0:
        print("extra credit for link NOT granted")
        return 0
    else:
        return 1


def check_hack():
    out, rc = run_ls_student("--hack", ['test'])
    out_solution, rc_solution = run_ls_solution("--hack", ['test'])
    if rc != rc_solution:
        print("ERROR: return code is not correct when calling './ls --hack'")
        return 0
    if out != out_solution:
        print("ERROR: output not correct: './ls --hack'")
        return 0
    return 1


def check_files(files, list_long=False, show_all=False, recursive=False, human=False, fields=[], check_rc=False, omit_slash=True):
    # returns 1 if the student's answer is correct, return 0 otherwise.
    flags = []
    if list_long:
        flags.append('-l')
    if recursive:
        flags.append('-R')
    if show_all:
        flags.append('-a')
    if human:
        flags.append('-h')

    flags = ' '.join(flags)
    out, rc_student = run_ls_student(flags, files)
    if rc_student == "decodeerror":
        return 0

    try:
        student_res = parse_cs202_output(out, list_long=list_long, omit_slash=omit_slash)
    except FormatError:
        print("An error occurred while parsing your output. Please check the output format.")
        return 0
    student_res = sort_by_fname(student_res)

    out, rc_solution = run_ls_solution(flags, files)

    # out = run_ls_system(flags, files)
    solution_res = parse_cs202_output(out, list_long=list_long, omit_slash=omit_slash)
    solution_res = sort_by_fname(solution_res)

    if check_rc:
        if rc_student != rc_solution:
            print(f"wrong return code {rc_student}, should be {rc_solution}")
            return 0

    if len(solution_res) > len(student_res):
        print("missing output lines")
        return 0

    for i in range(len(solution_res)):
        name = student_res[i]['fname'].replace(' ', '')
        if name != solution_res[i]['fname']:
            print("Divergence versus our solution")
            return 0

        if human:
            return 1 if student_res[i]['size'][-1] == solution_res[i]['size'][-1] else 0

        if list_long:
            for field in fields:
                if student_res[i][field] != solution_res[i][field]:
                    print(
                        "Divergence versus our solution. Hint: check the field " + field)
                    return 0

    return 1

# check whether the student forget the slash after the folder.
# return 0 if the student is correct. return -1 if the answer is not correct.
def check_slash():
    show_all = True
    for list_long in [True, False]:
        if (check_files(['test/hidden'], show_all=show_all, list_long=list_long, omit_slash=False) == 0 and
            check_files(['test/hidden'], show_all=show_all, list_long=list_long, omit_slash=True) == 1):
            print("Divergence versus our solution about the '/' at the end of a folder, deduct 5 points")
            return -1
    return 0


def main():
    # the score of this student!!
    score = 0

    # MW: for style, I would move the number to the front of the line, so it becomes a bit
    # clearer. But that's just me...

    print("\n---------------- required credits ---------------\n")
    # [5  points]  check "./ls --help"
    score += check_help_message() * 5

    # [10 points] ./ls
    score += check_files([], show_all=False, list_long=False) * 10

    # [18 points] ./ls a b
    score += check_files(['test/files/folder1'], show_all=False, list_long=False) * 3
    score += check_files(['test/files/folder1', 'test/files/folder2'], show_all=False, list_long=False) * 3
    score += check_files(['test/files/folder1', 'test/files/folder2', 'test/files/folder1/file-0.txt',
                          'test/files/folder2/file-103.txt'], show_all=False, list_long=False) * 4
    score += check_files(['test/error/deniedaccess/111']) * 2
    score += check_files(['test/error/deniedaccess/555']) * 2
    score += check_files(['test/error/deniedaccess/666']) * 2

    # [10 points] ./ls -a
    score += check_files([], list_long=False, show_all=True) * 2
    score += check_files(['test/hidden'], list_long=False, show_all=False) * 4
    score += check_files(['test/hidden'], list_long=False, show_all=True) * 4

    # [20 points] ./ls -l
    ls_l_score = 0
    show_all = False
    ls_l_score += check_files([], list_long=True, show_all=show_all) * 2
    ls_l_score += check_files(['test/files/folder1'], list_long=True, show_all=show_all) * 2
    ls_l_score += check_files(['test/files/folder1', 'test/files/folder2'], list_long=True, show_all=show_all) * 2
    ls_l_score += check_files(['.', '..', '.', '..'], show_all=show_all, list_long=True) * 2
    # check all fields for ls -l
    ls_l_score += check_files(['test/ls-l/easy'], show_all=show_all, list_long=True, fields=all_fileds) * 2
    # try to be generous and give them some points by each field
    ls_l_score += check_files(['test/ls-l/easy'], show_all=show_all, list_long=True, fields=[]) * 1
    ls_l_score += check_files(['test/ls-l/mode'], show_all=show_all, list_long=True, fields=["mode"]) * 1
    ls_l_score += check_files(['test/ls-l/nlink'], show_all=show_all, list_long=True, fields=["nlink"]) * 1
    ls_l_score += check_files(['test/ls-l/userid'], show_all=show_all, list_long=True, fields=["user"]) * 1
    ls_l_score += check_files(['test/ls-l/userid'], show_all=show_all, list_long=True, fields=["group"]) * 1
    ls_l_score += check_files(['test/ls-l/size'], show_all=show_all, list_long=True, fields=["size"]) * 1
    ls_l_score += check_files(['test/ls-l/easy'], show_all=show_all, list_long=True, fields=["mtime"]) * 1
    # special case: unknown user/group should be printed correctly
    ls_l_score += check_files(['test/error/userid'], show_all=show_all, list_long=True, fields=[]) * 1
    ls_l_score += check_files(['test/error/userid'], show_all=show_all, list_long=True, fields=["user"]) * 1
    ls_l_score += check_files(['test/error/userid'], show_all=show_all, list_long=True, fields=["group"]) * 1
    assert(ls_l_score <= 20)
    score += ls_l_score

    # [12 points] ./ls -R
    score += check_files(['test/ls-l/easy'], show_all=show_all, recursive=True) * 5
    score += check_files(['test/dirs'], show_all=show_all, recursive=True) * 5
    score += check_files(['test/error/deniedaccess'], show_all=show_all, recursive=True) * 2

    # [10 points] flag combiniaions
    score += check_files(['test/hidden'], list_long=True, show_all=True, recursive=True) * 2
    score += check_files(['test/hidden'], list_long=True, show_all=True, recursive=False) * 2
    score += check_files(['test/hidden'], list_long=True, show_all=False, recursive=True) * 2
    score += check_files(['test/hidden'], list_long=False, show_all=True, recursive=True) * 2
    score += check_files(['test/dirs'], list_long=True, show_all=True, recursive=True) * 2

    # [10  points] error code
    score += check_files(['test/error/noerror'], check_rc=True) * 2
    score += check_files(['test/error/deniedaccess/000'], check_rc=True) * 1
    score += check_files(['test/error/deniedaccess/111'], check_rc=True) * 1
    score += check_files(['test/error/deniedaccess/555'], check_rc=True) * 1
    score += check_files(['test/error/deniedaccess/666'], check_rc=True) * 1
    score += check_files(['test/error/notfound/foo'], check_rc=True) * 2
    score += check_files(['test/error/userid'], check_rc=True) * 1
    score += check_files(['test/error/userid'], list_long=True, check_rc=True) * 1

    # [17 points] error code combinations
    error_comb_score = 0
    dirs = ['test/error/deniedaccess', 'test/error/notfound/foo', 'test/error/userid', 'test/error/noerror']
    for files in itertools.combinations(dirs, 2):
        error_comb_score += check_files(files, check_rc=True) * 2
    for files in itertools.combinations(dirs, 3):
        error_comb_score += check_files(files, check_rc=True) * 1
    error_comb_score += check_files(dirs, check_rc=True) * 1
    score += error_comb_score

    # penalties 

    # deduct 5 points if the student forget to print '/'
    score += 5 * check_slash()
    
    print(f"Score: {score}")
    print("\n------------- extra credits ---------------")
    extra_score = 0
    # ls -lh
    extra_score += check_files(['test/ls-l/size'], list_long=True, human=True, fields=['size']) * 1
    # link
    extra_score += check_files(['test/links'], list_long=True, fields=['mode']) * 1
    extra_score += check_link_extra() * 1
    # this one has a self-cycle on symbolic link: dir1->dir2->dir1->dir2->...
    extra_score += check_files(['test/recursive'], list_long=True, recursive=True, fields=all_fileds) * 1
    # check --hack
    extra_score += check_hack() * 2

    print(f"Extra score: {extra_score}")
    print("------------------------------------------\n")
    print(f"{ls_exec} {score} {extra_score}", file=sys.stderr)


if __name__ == "__main__":
    main()
