import abc
import os
import re

import requests
import bs4

drivers = {}

class SIODriver(abc.ABC):
    host = None
    current_username_box_id = None
    problem_selection_id = None
    problem_cells_count = None
    def __init__(self):
        assert self.host is not None
        
        self.session = requests.Session()

        self.is_logged_in = False
        self.username = None

    def path_to(self, *path):
        return "/".join((self.host,) + path) + "/"

    def get_soup(self, *path):
        return bs4.BeautifulSoup(self.session.get(self.path_to(*path)).text, "html.parser")

    def login(self, get_username, get_password):
        cnt = self.list_contests()[0]
        self.session.get(self.path_to("c", cnt, "login"))
        username = get_username()
        response = self.session.post(
            self.path_to("c", cnt, "login"),
            data={
                "csrfmiddlewaretoken": self.session.cookies["csrftoken"],
                "username": username,
                "password": get_password()
        },
            headers={
                "Referer": self.path_to("c", cnt, "login"),
        })
        main = self.get_soup()
        if main.find(id=self.current_username_box_id).text.strip() != username:
            raise ValueError("Login failed")
        self.is_logged_in = True
        self.username = username

    def list_contests(self):
        soup = self.get_soup()
        result = []
        for link in soup.find_all("a"):
            match = re.match(r"/c/(.*)/", link.get("href"))
            if match:
                s = match.group(1)
                if s in result:
                    result.remove(s)
                result.append(s)
        return result

    def extract_problem_data(self, contest, cells):
        return {
            "name": cells[1].find_all("a")[0].text, 
            "score": int(cells[3].text.strip()) if cells[3].text.strip() else None
        }

    def list_problems(self, contest):
        soup = self.get_soup("c", contest, "p")

        result = {}
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 4:
                continue
            key = cells[0].text
            value = self.extract_problem_data(contest, cells)
            result[key] = value
        return result

    def format_extra_problem_data(self, data):
        return ""

    def get_problem_text_path(self, contest, problem_code):
        return self.path_to("c", contest, "p", problem_code)

    def get_problem_text(self, contest, problem_code):
        return self.session.get(self.get_problem_text_path(contest, problem_code))

    def submit_solution(self, contest, problem_code, filename):
        assert self.is_logged_in, "User must be logged in to submit"

        soup = self.get_soup("c", contest, "submit")
        problem_code_par = "({})".format(problem_code)
        problem_select_soup = soup.find(id=self.problem_selection_id)
        for opt in problem_select_soup.find_all("option"):
            if opt.text.strip().endswith(problem_code_par):
                problem_name = opt.text
                problem_value = opt.get("value")
                break
        else:
            raise KeyError("Problem with given code was not found in selection")

        response = self.session.post(
            self.path_to("c", contest, "submit"),
            data={
                "csrfmiddlewaretoken": self.session.cookies["csrftoken"],
                "problem_instance_id": problem_value
            },
            headers={
                "Referer": self.path_to("c", contest, "submit")
            },
            files={
                "file": open(filename, "rb")
            }
        )
    def configure_problem_table(self, table, problems):
        table.set_cols_align(["l", "l", "r"])
        table.set_cols_width([7, 52, 5])
        table.header(["Code", "Name", "Score"])
    def make_problem_table_row(self, problems, code):
        data = problems[code]
        return [code, data["name"], data["score"] if data["score"] is not None else " ? "]

class StaszicSIODriver(SIODriver):
    host = "https://sio2.staszic.waw.pl"
    current_username_box_id = "navbar-username"
    problem_selection_id = "id_problem_instance_id"
    def extract_problem_data(self, contest, cells):
        value = super().extract_problem_data(contest, cells)
        no = cells[2].find("div").get("id")[len("limits_"):]
        submit_info_t = self.get_soup("c", contest, "limits", no).text
        submit_info = submit_info_t.split(" / ")
        value.update({
            "submits_used": int(submit_info[0]),
            "submit_limit": int(submit_info[1])
        })
        return value
    def configure_problem_table(self, table, problems):
        submitW = min(4, max((len(str(x["submit_limit"])) for x in problems.values()), default=4))
        codeW = min(11, max(4, max((len(str(k)) for k in problems.keys()), default=4)))
        table.set_cols_align(["l", "l", "c", "r"])
        table.set_cols_width([codeW, 40 + (11 - (3+2*submitW)) + (11 - codeW), 3 + 2*submitW, 5])
        table.header(["Code", "Name", "Submits", "Score"])
    def make_problem_table_row(self, problems, code):
        data = problems[code]
        submitW = max(len(str(x["submit_limit"])) for x in problems.values())
        tpl = "{{: ^{}}} / {{: ^{}}}".format(submitW, submitW)
        return [code, data["name"], tpl.format(data["submits_used"], data["submit_limit"]), data["score"] if data["score"] is not None else " ? "]


drivers[StaszicSIODriver.host] = StaszicSIODriver
