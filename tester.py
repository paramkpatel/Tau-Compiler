import sys
import re
import subprocess


def run_test_commands(
    pickle_path=None, verbose=False, crash=False, name=False, test_case_path=None
):
    # Parser regenerate
    # subprocess.run(
    #     [
    #         "python",
    #         "-m",
    #         "rdgen.main",
    #         "create",
    #         "--input",
    #         "tau.ebnf",
    #         "--output",
    #         "parse.py",
    #     ]
    # )

    cmd = ["python", "-m", "testerator.main", "run"]
    if verbose:
        cmd.append("--verbose")
    if crash:
        cmd.append("--crash")
    if pickle_path:
        cmd.append(pickle_path)
    if name:
        cmd.extend(["--name", test_case_path])

    with open("result.txt", "w") as f:
        subprocess.run(cmd, stdout=f)


def passed_or_failed():
    line_count = 0
    passed_count = 0
    failed_testcase = []
    pattern = r"t\d+\.tau"

    with open("result.txt", "r") as f:
        for line in f:
            line_count += 1
            if "'passed': 'True'}" in line:
                passed_count += 1
            elif "'passed': 'False'}" in line:
                match = re.search(pattern, line)
                if match:
                    failed_testcase.append(match.group())
    return failed_testcase, line_count, passed_count


def center_with_hyphens(text, width):
    remaining_space = width - len(text)
    each_side = remaining_space // 2
    return "-" * each_side + text + "-" * each_side


def main():
    if len(sys.argv) < 2:
        print("Usage: python tester.py <pickle-path> [<test-case>] [<v> | <c>]")
        sys.exit(1)

    subprocess.run(["python3", "-m", "black", "."])

    # Access command-line arguments
    pickle_path = "tau/milestones/" + sys.argv[1] + ".pickle"

    verbose = False
    crash = False
    name = False
    test_case = None

    if len(sys.argv) > 2:
        name = True
        test_case = "tau/tests/" + sys.argv[2] + ".tau"
        if len(sys.argv) > 3:
            if sys.argv[3] == "v":
                verbose = True
            elif sys.argv[3] == "c":
                crash = True
            elif sys.argv[3] == "b":
                verbose = True
                crash = True

    run_test_commands(
        pickle_path=pickle_path,
        verbose=verbose,
        crash=crash,
        name=name,
        test_case_path=test_case,
    )

    failed_testcase, test_count, passed_count = passed_or_failed()

    print("==================================================")
    print(center_with_hyphens("TESTING", 50))
    print("==================================================")

    if len(failed_testcase) > 0:
        print("\n" + center_with_hyphens("Failed Test Cases", 50))
        for i, testcase in enumerate(failed_testcase):
            print(f"{testcase:15}", end=" ")
            if (i + 1) % 5 == 0:
                print()

        print("\n" + center_with_hyphens("Summary", 50))
        print(f"Total Tests    : {test_count}")
        print(f"Tests Passed   : {passed_count}")
        print(f"Tests Failed   : {test_count - passed_count}")
        print(f"Pass Percentage: {'{:.2f}'.format((passed_count / test_count) * 100)}%")
        print("==================================================")

    else:
        print("\n" + center_with_hyphens("PASSED", 50))
        print("==================================================")


if __name__ == "__main__":
    main()
