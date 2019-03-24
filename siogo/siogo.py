import itertools
import argparse
import getpass
import os

try:
    import texttable
except ImportError:
    TEXTTABLE_ENABLED = False
else:
    TEXTTABLE_ENABLED = True

import driverconfig
import siodriver

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def contest_list_table(driver, contests):
    columns = os.get_terminal_size().columns
    t_columns = 36
    n = max(1, columns // t_columns)
    table = texttable.Texttable(max_width=columns - 2)
    table.set_cols_align(["l"] * n)
    table.set_cols_width([t_columns - 4] * n)
    rows = [list(g) for g in grouper(contests, n, fillvalue="")]
    table.add_rows(rows, header=False)
    return table.draw()

def problem_list_table(driver, problems):
    columns = os.get_terminal_size().columns
    table = texttable.Texttable(max_width=columns - 2)
    table.set_cols_align(["l", "l", "l", "r"])
    table.set_cols_width([10, 30, 20, 5])
    table.header(["code", "name", "extra", "score"])
    for code, data in problems.items():
        row = [code, data["name"], driver.format_extra_problem_data(data), data["score"] if data["score"] is not None else "?"]
        table.add_row(row)
    return table.draw()

class MultiParserHelpAction(argparse._HelpAction):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                print("\n-- Subcommand '{}' --".format(choice))
                print(subparser.format_help())

        parser.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="siogo", description="Simple text-based SIO2 client.", add_help=False)
    parser.add_argument("-h", "--help", action=MultiParserHelpAction, help="Show this help message and exit")  # add custom help

    parser.add_argument("host", help="Specify the SIO2 host. Either a link or an abbreviation, if it is specified in `driverconfig.abbreviations`")
    parser.add_argument("-L", "--login", action="store_true", help="Log into a user account")
    parser.add_argument("-B", "--notable", action="store_true", help="Print without a table. Don't use `texttable`, even if it is available")

    subparsers = parser.add_subparsers(dest="subparser", help="Available commands: \"contests\", \"problems\", \"submit\"")
    
    parser_contests = subparsers.add_parser("contests", add_help=False, help="List visible contests")

    parser_problems = subparsers.add_parser("problems", add_help=False, help="List visible contest problems")
    parser_problems.add_argument("contest", help="The contest to list problems from")

    parser_problemtext = subparsers.add_parser("problemtext", add_help=False, help="Get the problem text")
    parser_problemtext.add_argument("contest", help="The contest the problem belongs to")
    parser_problemtext.add_argument("code", help="The problem's code")
    parser_problemtext.add_argument("filename", help="The file to write the problem text to. The file extension is added automatically")

    parser_submit = subparsers.add_parser("submit", add_help=False, help="Submit a solution")
    parser_submit.add_argument("contest", help="The contest to submit the solution to")
    parser_submit.add_argument("code", help="The problem's code")
    parser_submit.add_argument("filename", help="Solution filename")
    parser_submit.add_argument("-f", "--force", action="store_true", help="Disable confirmation")

    args = parser.parse_args()
    method = args.subparser

    host = driverconfig.abbreviations[args.host] \
            if args.host in driverconfig.abbreviations else args.host
    Driver = siodriver.drivers[host]
    driver = Driver()
    if args.login:
        driver.login(lambda: input("Username: "), lambda: getpass.getpass())    

    if method == "contests":
        contests = driver.list_contests()
        if not args.notable and TEXTTABLE_ENABLED:
            print(contest_list_table(driver, contests))
        else:
            print("\n".join("* " + c for c in contests))

    elif method == "problems":
        problems = driver.list_problems(args.contest)
        if not args.notable and TEXTTABLE_ENABLED:
            print(problem_list_table(driver, problems))
        else:
            for code, data in problems.items():
                extra = driver.format_extra_problem_data(data)
                print("{}: '{}'. {}[{}]".format(code, data["name"], (extra + ". ") if extra else "", data["score"] if data["score"] is not None else "?"))

    elif method == "problemtext":
        response = driver.get_problem_text(args.contest, args.code)
        t = response.headers["Content-Type"]
        if t == "application/pdf":
            filename = args.filename + ".pdf"
        elif t == "application/x-dvi":
            filename = args.filename + ".dvi"
        elif "text/html" in t:
            link = driver.get_problem_text_path(args.contest, args.code)
            print("! Got redirected to text in HTML, only partial text is available. A web browser will be needed. Link: {}".format(link))
            filename = args.filename + ".html"
        else:
            print("! Don't know the extension for 'Content-Type: {}'".format(t))
            filename = args.filename
        with open(filename, "wb") as file:
            file.write(response.content)

    elif method == "submit":
        assert args.login, "Must be logged in to submit"
        resp = "" if not args.force else "y"
        while resp.lower() not in ("y", "n"):
            resp = input("Are you sure you want to submit solution <{}> to problem <{}> @ <{}>? [Y/n]: ".format(args.filename, args.code, args.contest))
        if resp.lower() == "y":
            print("Submitting...")
            driver.submit_solution(args.contest, args.code, args.filename)
            print("Done.")
        else:
            print("Aborting submission.")
