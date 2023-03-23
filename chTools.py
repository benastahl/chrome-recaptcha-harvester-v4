import os
import sys
import bcolors
import json

from datetime import datetime
from termcolor import colored
from PyInquirer import prompt


class chTools:
    def __init__(self):
        self.clear_method = None
        if sys.platform == "win32":
            self.clear_method = "cls"
            self.fd = "\\"
        else:
            self.clear_method = "clear"
            self.fd = "/"

    def clear(self):
        os.system(self.clear_method)

    def get_chromedriver_path(self):
        fileName = f"{sys.platform}_chromedriver"
        return f"{os.getcwd()}{self.fd}chromedrivers{self.fd}{fileName}"

    def get_profiles_path(self, profile_name):
        return os.getcwd() + self.fd + "browser-profiles" + self.fd + profile_name

    @staticmethod
    def get_formatted_proxies():
        with open("harvester_proxies.txt", "r") as f:
            proxies = [line.replace("\n", "") for line in f.readlines()]
        with open("browser-profiles/bp-proxies.json", "r") as f:
            bp_proxies = [data["proxy"] for data in json.load(f).values()]

        for proxyNum in range(len(proxies)):
            if proxies[proxyNum] in bp_proxies:
                proxies[proxyNum] += " (IN USE BY ANOTHER PROFILE)"
        return proxies

    @staticmethod
    def get_bp_proxy(profile_name):
        with open("browser-profiles/bp-proxies.json", "r") as f:
            bp_proxies = json.load(f)
        return bp_proxies[profile_name]["proxy"]

    @staticmethod
    def save_bp_proxy(profile_name, proxy):
        with open("browser-profiles/bp-proxies.json", "r") as f:
            bp_proxies = json.load(f)
        bp_proxies[profile_name]["proxy"] = proxy
        with open("browser-profiles/bp-proxies.json", "w") as f:
            json.dump(bp_proxies, f, indent=2)

    @staticmethod
    def save_browser_profile(profile_name):
        with open("browser-profiles/bp-proxies.json", "r") as f:
            bp_proxies = json.load(f)
        bp_proxies[profile_name] = {"proxy": None}
        with open("browser-profiles/bp-proxies.json", "w") as f:
            json.dump(bp_proxies, f, indent=2)

    @staticmethod
    def console_log(text, status):
        if status == 's':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - {text}",
                'green'))
        if status == 'f':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - {text}",
                'red'))
        if status == 'p':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - {text}",
                'cyan'))
        if status == 'd':
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - {text}",
                'yellow'))
        if status == "S":
            print(
                bcolors.OK + f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - " + bcolors.OKMSG + f"{text}" + bcolors.ENDC)
        if status == "F":
            print(
                bcolors.ERR + f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - " + bcolors.ERRMSG + f"{text}" + bcolors.ENDC)

    # FRONTEND
    @staticmethod
    def question(name, message, **kwargs):
        answer = None
        choices = kwargs.get("choices")
        prompter = [
            {
                'type': "",
                'name': name,
                'message': message,
            }
        ]

        if choices:
            prompter[0]["type"] = "list"
            prompter[0]["choices"] = kwargs.get("choices")
        else:
            prompter[0]["type"] = "input"

        try:
            answer = prompt(prompter)[name]
        except KeyError:
            pass
        return answer

    def profile_arguments(self, opts, **kwargs):
        profile_name = kwargs.get("profile_name")
        if profile_name:
            opts.add_argument("--user-data-dir=" + self.get_profiles_path(profile_name))
        opts.add_argument('--allow-insecure-localhost')
        opts.add_argument('--ignore-ssl-errors')
        opts.add_argument('--ignore-certificate-errors-spki-list')
        opts.add_argument('--ignore-certificate-errors')
        opts.add_argument("user-agent=Chrome")
        opts.add_argument("--disable-blink-features")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_argument('--disable-extensions')
        opts.add_argument('disable-infobars')
        opts.add_argument('--window-size=500,645')
        opts.add_argument('--allow-profiles-outside-user-dir')
        # opts.add_argument('--blink-settings=imagesEnabled=false')  # DISABLES IMAGES
        opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        return opts
