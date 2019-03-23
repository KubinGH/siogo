import traceback
import getpass
import os

from siogo import configs
from siogo.siodriver import SIODriver

try:
    s_config = configs.DriverConfigStaszic
    get_driver = configs.make_simple_headless_chrome_driver
    sio = SIODriver(s_config, get_driver)
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
