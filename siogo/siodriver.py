import os

from selenium import webdriver
import bs4

from . import exceptions
from .utility import with_retries
from . import configs

class SIODriver:
    def __init__(self, config, get_driver):
        self.config = config

        self.driver = get_driver()

        self.is_logged_in = False
        self.username = None

    def get_soup(self):
        return bs4.BeautifulSoup(self.driver.page_source, "html.parser")    

    def path_to(self, *path):
        return "/".join((self.config.ADDRESS,) + path)

    def login(self, get_username, get_password):
        self.driver.get(self.path_to("login"))
        username_box = self.driver.find_element_by_id(self.config.USERNAME_BOX_ID)
        username_box.clear()
        self.username = get_username()
        username_box.send_keys(self.username)

        password_box = self.driver.find_element_by_id(self.config.PASSWORD_BOX_ID)
        password_box.clear()
        password_box.send_keys(get_password())

        confirm_button = self.driver.find_element_by_id(self.config.CONFIRM_LOGIN_ID)
        confirm_button.click()

        if self.driver.find_element_by_id(self.config.CURRENT_USERNAME_BOX).text != self.username:
            raise exceptions.LoginFailed("Login failed.")
        self.is_logged_in = True
        print("Login successful!")

    def list_contests(self):
        assert self.is_logged_in
        self.driver.get(self.path_to())
        soup = self.get_soup()
        result = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href.startswith("/c/"):
                result.append(href[len("/c/"):])
        return result

    def list_problems(self, contest):
        assert self.is_logged_in
        self.driver.get(self.path_to("c", contest, "p"))
        def get():
            soup = self.get_soup()

            result = {}
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) != 4:
                    continue
                key, value = self.config.get_problem_data(cells, assert_submit_data=True)
                result[key] = value

            return result
        return with_retries(get, (exceptions.PageNotLoaded, ), 3, delay=0.66)

    def get_problem_text_path(self, contest, problem_code):
        assert self.is_logged_in
        return self.path_to("c", contest, "p", problem_code)

    def submit_solution(self, contest, problem_code, filename):
        assert self.is_logged_in
        if not os.path.exists(filename):
            raise FileNotFoundError("Solution file was not found.")

        self.driver.get(self.path_to("c", contest, "submit"))

        soup = self.get_soup()
        problem_code_par = "({})".format(problem_code)
        problem_select_soup = soup.find(id=self.config.PROBLEM_SELECT_ID)
        for opt in problem_select_soup.find_all("option"):
            if opt.text.strip().endswith(problem_code_par):
                problem_name = opt.text
                break
        else:
            raise KeyError("Problem with given code was not found.")

        problem_select = self.driver.find_element_by_id(self.config.PROBLEM_SELECT_ID)
        problem_select.send_keys(problem_name)

        file_choice = self.driver.find_element_by_id(self.config.FILE_CHOICE_ID)
        file_choice.send_keys(filename)

        submit_button = [btn for btn in self.driver.find_elements_by_tag_name("button") if btn.text.strip() in self.config.SUBMIT_BUTTON_POSSIBLE_TEXT][0]

        confirm = input("Are you sure you want to submit file <{}> to problem <{}>? [Y]: ".format(filename, problem_name))
        if confirm.strip().lower() == "y":
            submit_button.click()
        else:
            raise exceptions.NotUserApproved("User did not approve submission.")

