from selenium import webdriver

from . import exceptions

def make_simple_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--silent")
    options.add_argument("--log-level=OFF")
    options.add_argument("--disable-logging")
    return webdriver.Chrome(chrome_options=options)

def make_simple_headless_chrome_driver():    
    options = webdriver.ChromeOptions()
    options.add_argument("--silent")
    options.add_argument("--log-level=OFF")
    options.add_argument("--disable-logging")
    options.add_argument("--no-proxy-server")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--headless")
    return webdriver.Chrome(chrome_options=options)

class ScrapperConfigStaszic:
    ADDRESS = "https://sio2.staszic.waw.pl"
    USERNAME_BOX_ID = "id_username"
    PASSWORD_BOX_ID = "id_password"
    CONFIRM_LOGIN_ID = "id_submit"
    CURRENT_USERNAME_BOX = "navbar-username"
    PROBLEM_CELLS_COUNT = 4
    def get_problem_data(cells, assert_submit_data=True):
        if not cells[2].find_all("span"):
            if assert_submit_data:
                raise exceptions.PageNotLoaded("Submit info was not loaded.")
            else:
                submit_info = [float("NaN"), float("NaN")]
        else:
            submit_info = cells[2].find_all("span")[0].text.split(" / ")
            submit_info[0] = int(submit_info[0])
            submit_info[1] = int(submit_info[1])
        return (
            cells[0].text, 
            {
                "name": cells[1].find_all("a")[0].text, 
                "submits": submit_info[0],
                "total_submits": submit_info[1],
                "points": int(cells[3].text.strip()) if cells[3].text.strip() else float("NaN")
        })
    PROBLEM_SELECT_ID = "id_problem_instance_id"
    FILE_CHOICE_ID = "id_file"
    SUBMIT_BUTTON_POSSIBLE_TEXT = ("Wyślij", "Submit")
