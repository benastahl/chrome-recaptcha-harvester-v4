# Chrome ReCaptcha Harvester
_Created by Volt#9540_

***
#### **This project allows you to open multiple chrome harvesters with your chrome profiles, and call for a `g_recaptcha_token` (either v2, or v3) for use in your own project.**
### Support
If you have questions or need help setting up, please join the discord [here](https://discord.gg/2u2qCTXas5).

***
## Setup
#### 1. Run
Start by running `python harvester.py`
#### 2. Chrome Login
To open a harvester, you first need to create a browser profile (chrome profile). Select `Chrome Login` in the CLI menu. Enter a custom profile name, (I would recommend choosing one that relates to your browser profile), select a proxy from `harvester_proxies.txt` or choose the preset option `Local Host`. Following this, a browser will open where you will enter your chrome login information. Once this is done, press enter in the CLI, and your browser profile will be saved!

#### 3. Open Harvester
Select `Open Harvester` in the CLI menu. Select the browser profile you want. Following this, a chrome harvester will open with a `Waiting for Captcha` page. 

#### 4. Call for token
To call for a `g_recaptcha_token`, simply call the `harvest_captcha` function with the captcha type and URL of the captcha location. ex:
```python
g_recaptcha_token = harvest_captcha(captchaType="v2", captchaURL="https://www.google.com/recaptcha/api2/demo")
```
When called, a request will be put into a queue for the next available harvester for you to solve. Once solved, the function will return the `g_recaptcha_token`
***
### NOTES
* Proxies are formatted accordingly: `'username:password@host:port'`. To assign proxies to your browser profile, paste your proxies into `harvester_proxies.txt` row by row. 
* You may need to replace the chromedrivers in `./chromedrivers` with the latest version of chrome. The harvester does not autoupdate the chromedrivers.
* The harvester is completely thread-safe. It is compatible with running high numbers of multi-threaded tasks. 
***
## Example
Below is an example of a bot (with multi-threaded tasks) integrated with the harvester...

```python
import chTools
import threading

from harvester import chrome_login, harvest_token, open_harvester


def bot():
    # Find product code here...
    print("Product found!")
    
    print("Captcha needed for ATC!")
    g_recaptcha_token = harvest_token("v2", "URL HERE")
    
    # ATC WITH TOKEN...
    
    print("Added item to cart.")

def cli_menu():
    menu_answer = chTools.question(name="Selection", message="Main Menu",
                                   choices=["Start Tasks", 'Chrome Login', "Open Harvester",
                                             'Exit'])

    if menu_answer == "Start Tasks":
        task_count = 3
        for n in range(task_count):
            threading.Thread(target=bot, args=()).start()
    elif menu_answer == "Exit":
        exit(1)
    else:
        menu_calls = {
            "Chrome Login": chrome_login, 
            "Open Harvester": open_harvester
        }
        menu_calls[menu_answer]()  # Call menu answer func

```
***

