import threading
import time
import bcolors
import urllib3
import re
import colorama
import os
import gzip
import uuid
import shutil

from datetime import datetime
from termcolor import colored

from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from chTools import chTools

colorama.init()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
chTools = chTools()

token_lock, captcha_lock = threading.Lock(), threading.Lock(),

# Harvester
harvesters = []
token_inquirers = {}
tokens = {}


class Harvester:
    def __init__(self, proxy, profile_name):
        self.driver = None
        self.number = 0
        self.proxy = self.proxy_config(proxy)
        self.profile_name = profile_name

    def proxy_config(self, proxy):
        if not proxy or proxy == "Local Host":
            return {}

        parsed_proxy = None
        try:
            (IPv4, Port, username, password) = proxy.split(':')
            ip = IPv4 + ':' + Port
            parsed_proxy = {
                "proxy": {
                    "http": "http://" + username + ":" + password + "@" + ip,
                    "https": "http://" + username + ":" + password + "@" + ip,
                }
            }
        except ValueError:
            self.log("Invalid proxy.", "f")
            exit(1)
        return parsed_proxy

    def log(self, text, status):
        if status == 's':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [{self.number + 1}] - [Captcha Harvester] - {text}",
                'green'))
        if status == 'f':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [{self.number + 1}] - [Captcha Harvester] - {text}",
                'red'))
        if status == 'p':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [{self.number + 1}] - [Captcha Harvester] - {text}",
                'cyan'))
        if status == 'd':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [{self.number + 1}] - [Captcha Harvester] - {text}",
                'yellow'))

    @staticmethod
    def token_needed():
        global tokens
        token_lock.acquire()
        if len(token_inquirers) > 0:
            return list(token_inquirers.keys())[0]
        return False

    def waiting(self):
        waiting_html = """
        <html lang="en">

            <style>
                .waiting-title {
                    margin-top: 150px;

                }
                h1 {
                text-align: center;
                font-size: 45px;
                }
                img {
                text-align: center;
                }
            </style>

            <head>
                <meta charset="UTF-8">
                <title>Chrome Captcha Harvester</title>
            </head>

            <body>
                <h1 class="waiting-title">Waiting for Captcha...</h1>
                <h1 style="font-size: 20px;">Harvester: %s</h1>
                <h1 style="font-size: 20px;">Profile: %s</h1>
                <!-- <img src="https://thumbs.gfycat.com/AgonizingDiligentHapuka-max-1mb.gif" alt="Loading..." width="500" height="300"> -->
            </body>

        </html>


                """ % (self.number, self.profile_name)
        self.driver.get("data:text/html;charset=utf-8," + waiting_html)

    def open(self):
        executable_path = chTools.get_chromedriver_path()
        chrome_options = chTools.profile_arguments(Options(), profile_name=self.profile_name)
        self.driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options,
                                       seleniumwire_options=self.proxy)
        self.waiting()

    def wait_for_captcha(self):
        try:
            self.waiting()
            while True:

                task_id = self.token_needed()
                if task_id:
                    self.log("Token in need! Grabbing one...", "p")
                    task = token_inquirers[task_id]
                    token_inquirers.pop(task_id)
                    token_lock.release()

                    self.driver.get(task["url"])
                    g_recaptcha_token = self.get_valid_token(task["type"])
                    with token_lock:
                        tokens[task_id] = g_recaptcha_token
                    self.waiting()
                    continue
                token_lock.release()
        except InvalidArgumentException:
            menu(
                message=bcolors.FAIL + 'Make sure you do not have any browsers open with the same browser profile.' + bcolors.END)
            self.driver.quit()

    def get_valid_token(self, captcha_type):
        while True:
            self.log("Waiting for Captcha...", "p")

            try:
                version_paths = {
                    "v2": "/recaptcha/api2/userverify",
                    "v3": "/recaptcha/enterprise/reload"
                }
                request = self.driver.wait_for_request(pat=version_paths[captcha_type], timeout=10000)

                response_body = str(gzip.decompress(request.response.body)).replace('"', '')
                response_list = response_body.split(',')
                recaptcha_token = response_list[1]
                invalid_v2_token = re.findall("bgdata", response_body) and captcha_type == "v2"
                if invalid_v2_token:
                    self.log("Invalid recaptcha token.", "F")
                    del self.driver.requests
                    continue

                self.log('Valid token found', "s")
                del self.driver.requests
                return recaptcha_token

            except TimeoutError or TimeoutException:
                menu(message=bcolors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + bcolors.END)
            except Exception as exc:
                chTools.clear()
                self.log("Error occurred: " + str(exc), "F")
                time.sleep(2)


def chrome_login():
    driver = None
    try:
        while True:
            profile_name = chTools.question(name="Profile Name", message="Profile name:")
            try:
                if profile_name in os.listdir(chTools.get_profiles_path("")):
                    print(
                        bcolors.FAIL + "Failed to create new browser profile. Try a different name." + bcolors.END)
                    continue

                print(bcolors.BLUE + "Opening with new user data..." + bcolors.ENDC)
                login_args = chTools.profile_arguments(Options(), profile_name=profile_name)

                driver = webdriver.Chrome(options=login_args, executable_path=chTools.get_chromedriver_path())
                break

            except FileExistsError:
                print(bcolors.FAIL + 'That profile name already exists. Choose another.' + bcolors.END)
            # except WebDriverException:
            #     print(bcolors.FAIL + "Chromedriver version is OUT OF DATE. Replace with latest stable version." + bcolors.END)

        print(bcolors.BLUE + "Enter your login information." + bcolors.ENDC)
        driver.get('https://gmail.com')
        try:
            del driver.requests
            input("Please press enter once you have logged in: ")
        except TimeoutError or TimeoutException:
            menu(message=bcolors.FAIL + "Recaptcha Harvester Login timed out. Try again." + bcolors.ENDC)

        chTools.save_browser_profile(profile_name)
        driver.quit()
        menu(
            message=bcolors.OK + 'Profile Save "' + bcolors.BOLD + bcolors.UNDERLINE + profile_name + bcolors.ENDC + bcolors.OK + '" completed!' + bcolors.ENDC)
    except InvalidArgumentException:
        menu(
            message=bcolors.FAIL + "Make sure you do not have any browsers open with the same browser profile." + bcolors.ENDC)


def browser_profiles():
    try:
        # Choose browser profile to edit list
        profiles = os.listdir(chTools.get_profiles_path(""))
        profile_name = chTools.question(name="Browser Profile List", message="Select a browser profile:",
                                        choices=profiles)

        # Edit options
        edit_answer = chTools.question(name="EditOptions", message="Select an edit option:",
                                       choices=['Change name', 'Delete', 'Go back'])

        if edit_answer == "Go back":
            chTools.clear()
            browser_profiles()

        if edit_answer == 'Change name':
            while True:
                profile_rename = chTools.question(name="Rename",
                                                  message='Enter a new name for the browser profile:')

                if profile_rename in os.listdir(chTools.get_profiles_path("")):
                    print(bcolors.FAIL + 'That profile name already exists. Choose another.' + bcolors.END)
                    continue

                og_path = chTools.get_profiles_path(profile_name)
                rename_path = chTools.get_profiles_path(profile_rename)

                # Rename
                os.rename(og_path, rename_path)

                menu(
                    message=bcolors.OK + 'Browser Profile: "' + profile_name + '" has been renamed to: "' + profile_rename + '"' + bcolors.ENDC)
                break
        if edit_answer == 'Delete':
            shutil.rmtree(chTools.get_profiles_path(profile_name))
            menu(
                message=bcolors.OK + 'Browser profile: "' + profile_name + '" has been deleted.' + bcolors.ENDC)
    except InvalidArgumentException:
        menu(
            message=bcolors.FAIL + 'Make sure you do not have any browsers open with the same browser profile.' + bcolors.ENDC)
    except TimeoutError or TimeoutException:
        menu(message=bcolors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + bcolors.END)


def open_harvester():
    browser_profiles = os.listdir(chTools.get_profiles_path(""))
    browser_profiles.remove("bp-proxies.json")
    profile_name = chTools.question(name="Profile Choice", message="Choose a browser profile:",
                                    choices=browser_profiles)

    proxy_choices = ["Local Host"]
    proxy_choices.extend(chTools.get_formatted_proxies())
    saved_proxy = chTools.get_bp_proxy(profile_name)
    if saved_proxy:
        proxy_choices.insert(0, saved_proxy + " (SAVED)")
    proxy = chTools.question(name="Proxy Choice", message="Proxy options:", choices=proxy_choices).replace(
        " (IN USE BY ANOTHER PROFILE)", "").replace(" (SAVED)", "")
    if saved_proxy != proxy:
        save_proxy = chTools.question(name="Save Proxy?", message="Save Proxy/LH option?",
                                      choices=["Yes", "No"])
        if save_proxy == "Yes":
            chTools.save_bp_proxy(profile_name, proxy)

    harvester = Harvester(
        proxy=proxy,
        profile_name=profile_name
    )
    harvesters.append(harvester)
    harvester.number = harvesters.index(harvester)
    harvester.open()
    threading.Thread(target=harvester.wait_for_captcha, args=()).start()
    menu()


def harvest_token(captchaType, captchaURL):
    print("In queue for captcha token...")
    global tokens
    with token_lock:
        task_id = uuid.uuid4()
        token_inquirers[task_id] = {
            "type": captchaType,
            "url": captchaURL,
        }

    # Enter queue to get token
    with captcha_lock:
        while not tokens.get(task_id):
            continue
        g_recaptcha_token = tokens[task_id]
        print("Task received token:", g_recaptcha_token)
        with token_lock:
            tokens.pop(task_id)

    return g_recaptcha_token


def menu(message=None):
    chTools.clear()
    print(message)
    menu_answer = chTools.question(name="Selection", message="Main Menu",
                                   choices=["Start Tasks", 'Chrome Login', "Open Harvester",
                                            'Your Browser Profiles', 'Test the Captcha Harvester', 'Exit'])

    if menu_answer == "Start Tasks":
        print("Nothing here lol. Call your own function. -line329")
    elif menu_answer == "Test the Captcha Harvester":
        if not harvesters:
            menu(message=bcolors.FAIL + "No open harvesters." + bcolors.ENDC)

        ReCaptchaType = chTools.question(name="ReCaptcha Type", message="ReCaptcha Type:",
                                         choices=["v2"])

        tokenAmount = int(chTools.question(name="Token Amount", message="Enter token amount:"))

        for harvester in harvesters:
            threading.Thread(target=harvester.wait_for_captcha, args=()).start()

        threads = []
        for n in range(tokenAmount):
            thread = threading.Thread(target=harvest_token, args=(ReCaptchaType, "https://www.google.com/recaptcha/api2/demo"))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        menu(message=bcolors.OKMSG + "Finished captcha token collection." + bcolors.ENDC)
    elif menu_answer == "Exit":
        for harvester in harvesters:
            harvester.driver.quit()
        exit(1)
    else:
        menu_calls = {"Chrome Login": chrome_login, "Open Harvester": open_harvester, "Your Browser Profiles": browser_profiles}
        menu_calls[menu_answer]()  # Call menu answer func


if __name__ == "__main__":
    menu()
