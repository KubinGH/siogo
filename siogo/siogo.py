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
import tableutils
import siodriver

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
    parser.add_argument("-B", "--notable", action="store_true", help="Print without a table. Don't use `texttable`, even if it is available.")

    subparsers = parser.add_subparsers(dest="subparser", help="Available commands: \"contests\", \"problems\", \"submit\"")
    
    parser_contests = subparsers.add_parser("contests", add_help=False, help="List visible contests")

    parser_problems = subparsers.add_parser("problems", add_help=False, help="List visible contest problems")
    parser_problems.add_argument("contest", help="The contest to list problems from")

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
        if not args.notable and TEXTTABLE_ENABLED:
            print(tableutils.table_formatted_list(driver.list_contests()))
        else:
            print("\n".join("* " + c for c in driver.list_contests()))

    elif method == "problems":
        problems = driver.list_problems(args.contest)
        if not args.notable and TEXTTABLE_ENABLED:
            columns = os.get_terminal_size().columns
            table = texttable.Texttable(max_width=columns - 2)
            table.set_cols_align(["c", "l", "l", "c"])
            table.set_cols_width([10, 30, 20, 4])
            table.header(["code", "name", "extra", "score"])
            for code, data in problems.items():
                row = [code, data["name"], driver.format_extra_problem_data(data), data["score"] if data["score"] is not None else "?"]
                table.add_row(row)
            print(table.draw())
        else:
            for code, data in problems.items():
                extra = driver.format_extra_problem_data(data)
                print("{}: '{}'. {}[{}]".format(code, data["name"], (extra + ". ") if extra else "", data["score"] if data["score"] is not None else "?"))

    elif method == "submit":
        assert args.login, "Must be logged in to submit"
        resp = ""
        while resp.lower() not in ("y", "n"):
            resp = input("Are you sure you want to submit solution <{}> to problem <{}> @ <{}>? [Y/n]: ".format(args.filename, args.code, args.contest))
        if resp.lower() == "y":
            print("Submitting...")
            driver.submit_solution(args.contest, args.code, args.filename)
            print("Done.")
        else:
            print("Aborting submission.")
