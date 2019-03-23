# siogo
`siogo` is a simple SIO2 text-based client under development.

Right now, the driver (`siogo.siodriver.SIODriver`), based on Selenium, works and supports the following:
* Navigating the page (`path_to(*path)`, arguments are strings) and extracting the HTML (`get_soup()`). More complicated HTML handling implemented with `bs4`, aka Beautiful Soup.
* Logging in (`login(get_username, get_password)`, both arguments are functions). Credentials may be supplied in any way, for example Python's `getpass`, but a function that returns them must be passed.
  * The login is checked by seeing if the username on the navbar is correct. If it is not, `exceptions.LoginFailed` is raised.
* Listing visible contests (`list_contests()`). This is done by navigating to the main page and looking for all links leading to a `/c/whatever` path.
* Listing contest problems (`list_problems(contest)`, `contest` is the path name, not the visible name). All data that can be harvested is returned. This is done by looking at the problem list under `/p/` and checking table rows with the correct number of cells. 
  * Because SIO2 may load additional data after the page is declared ready, this function is executed up to three times with 0.66 second delays. If all tries fail because of a `exceptions.PageNotLoaded` exception, `exceptions.TooManyTries` is raised.
* Submitting solutions (`submit_solution(contest, problem_code, filename)`, `contest` is the contest path, `problem_code` is the short (commonly 3-letter) code, `filename` is an **absolute** path to the solution). 
  * This is **not** implemented with the `submit.py` script that some SIO2's use. 
  * Exceptions:
    * If the solution file doesn't exist, `FileNotFoundError` is raised. 
    * If the problem with the given code doesn't exist, `KeyError` is raised. 
    * A submission must be approved via user interaction: if it is not approved, `exceptions.NotUserApproved` is raised.
* Getting problem text (`get_problem_text_path`). Further extraction may be done with `requests` or similar.

A `SIODriver` instance is constructed via `SIODriver(config, get_driver)`, where `config` is an object implementing the same attributes as the example `configs.DriverConfigStaszic`, and `get_driver` is a function constructing `selenium`'s webdriver.

Example usage of the driver is presented in `main.py`.

Requirements:
- Selenium
- A webdriver and the ability to configure it (`configs` include a simple chromedriver configuration)
- Beautiful Soup
- Python 3

