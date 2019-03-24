# siogo
`siogo` is a simple SIO2 text-based client under development.

The console command `siogo` has the following syntax:
```siogo [host] [-L/--login] [-B/--notable] {subcommand}```
* `host` is either the full hostname or an abbreviation, if it is specified in `driverconfig`.
* `-L/--login`: make the driver log in before handling the requests.
* `-B/--notable`: do not use `texttable` to format output.

`subcommand` is one of: `contests`, `problems`, `submit`.
* `contests` has no additional arguments. It lists the visible contests.
* `problems` requires one positional argument: `contest`, which is the contest page path. Lists the visible problems from `contest`.
* `submit` submits a given solution and requires three positional arguments:
  * `contest`, which is the contest page path,
  * `code`, which is the short problem code,
  * `filename`, the solution filename.
  * There is one optional argument: `-f/--force`, that makes the command not require confirmation from the user.

All the data is pretty-printed using the `texttable` module. If it is not available, it will still work, but it ain't pretty. You can force it to not be used with `-B/--notable`.

The driver (`siogo.siodriver.SIODriver`), based on `requests`, works and supports the following:
* Navigating the page (`path_to(*path)`, arguments are strings) and extracting the HTML (`get_soup(*path)`). More complicated HTML handling is implemented with `bs4`, aka Beautiful Soup.
* Logging in (`login(get_username, get_password)`, both arguments are functions). Credentials may be supplied in any way, for example Python's `getpass`, but a function that returns them must be passed.
  * The login is checked by seeing if the username on the navbar is correct. If it is not, `ValueError` is raised.
* Listing visible contests (`list_contests()`). This is done by navigating to the main page and looking for all links leading to a `/c/whatever/` path, using regexes.
* Listing contest problems (`list_problems(contest)`, `contest` is the path name, not the visible name). All data that can be harvested is returned. This is done by looking at the problem list under `/p/` and checking table rows with the correct number of cells. 
  * This process is somewhat slow because of the extra requests to gather the submit info (on https://sio2.staszic.waw.pl) -- this is not the case on, for example, https://szkopul.edu.pl/, where the submit info is sent directly.
* Submitting solutions (`submit_solution(contest, problem_code, filename)`, `contest` is the contest path, `problem_code` is the short (commonly 3-letter) code, `filename` is the solution file).
  * This is **not** implemented with the `submit.py` script that some SIO2's use. 
  * Exceptions:
    * If the solution file doesn't exist, `FileNotFoundError` is raised. 
    * If the problem with the given code doesn't exist, `KeyError` is raised.
* Getting problem text (`get_problem_text(contest, problem_code)`).

In order to use `SIODriver` you must inherit from it and implement supply the following class attributes: `host` (the base URL), `current_username_box_id` (the ID of the navbar username box), `problem_selection_id` (the ID of the problem selection list in the submit menu), `problem_cells_count` (the count of cells in a table row in the problem list for an actual problem). `StaszicSIODriver` is provided. If you want to, you can implement additional problem data extraction from the problem list with `extract_problem_data(contest, cells)`.

Example usage of the driver is presented in `main.py`.

*Previously the driver was implemented with Selenium. The old, unsupported implementation is available in `/siogo/old_selenium/`. `main.py` still includes example usage.*

Requirements:
- Python 3,
- Requests (`requests`),
- Beautiful Soup (`bs4`),
- (Optional) `texttable`.

