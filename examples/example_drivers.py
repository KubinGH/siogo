import traceback
import getpass
import os
from siogo.siodriver import StaszicSIODriver

def run_selenium_driver():
    from siogo.old_selenium.selenium_siodriver import SeleniumSIODriver
    try:
        config = configs.DriverConfigStaszic
        get_driver = configs.make_simple_headless_chrome_driver
        sio = SeleniumSIODriver(config, get_driver)
        sio.login(lambda: input("Username: "), lambda: getpass.getpass(prompt="Password: |"))
        print(sio.list_contests())
        for code, info in sio.list_problems("matex_k18_a").items():
            print(code, info)

        code = input("Problem code: ")
        sol = input("Solution absolute path: ")
        sio.submit_solution("matex_k18_a", code, sol)
        os.system("pause")
    except:
        traceback.print_exc()
    finally:
        sio.driver.close()
        sio.driver.quit()

def run_requests_driver():
    sio = StaszicSIODriver()
    print(sio.list_contests())
    sio.login(lambda: input("Username: "), lambda: getpass.getpass(prompt="Password: |"))
    print(sio.list_contests())
    for code, info in sio.list_problems("matex_k18_a").items():
        print(code, info)

run_requests_driver()
