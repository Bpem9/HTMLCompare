import pandas as pd
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire import webdriver as sw_webdriver
from selenium.webdriver.common.by import By
import pathlib
import platform
import os
from urllib.parse import urlparse

from tqdm import tqdm


class SeleniumFirefoxLocalAdapter:
    def __init__(self, html_comparer=None, *args, **kwargs):
        self.driver = sw_webdriver.Firefox

        self.command_executor = 'http://selenium:4444/wd/hub'

        self.proxy = sw_webdriver.Proxy()
        self.proxy.http_proxy = 'selenium:4444'
        self.proxy.ssl_proxy = 'selenium:4444'

        self.options = webdriver.FirefoxOptions()
        self.options.proxy = self.proxy
        self.options.add_argument('--headless')

        self.options.binary_location = '/usr/bin/firefox'
        driver_path = pathlib.Path(__file__).parent.resolve() / 'geckodriver'
        if platform.system() == 'Windows':
            self.options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
            driver_path = str(driver_path) + '.exe'
        proxy = os.environ.get('PROXY', None)

        self.seleniumwire_options = {
            'addr': '127.0.0.1',
        }
        if proxy:
            self.seleniumwire_options.update(
                {
                    'proxy': {
                        'http': f'http://{proxy}',
                        'https': f'https://{proxy}',
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                }
            )

        self.service = Service(executable_path=driver_path)
        self.html_comparer = html_comparer

    def get_slots(self, ref_urls: List[str]) -> dict[str, bool]:
        """
        :param ref_urls: The list of URIs to compare
        :return: The dictionary with comparison result indexed by the name of the website
        """
        results = dict()
        with sw_webdriver.Firefox(
            options=self.options,
            service=self.service,
            seleniumwire_options=self.seleniumwire_options
        ) as wd:
            for i in tqdm(range(len(ref_urls))):
                # wd.switch_to.new_window('tab')
                wd.get(ref_urls[i] + f'/slots?subcategory=-1&products=[887]')

                wd.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);'
                )

                slots = wd.execute_script(
                    'return document.getElementsByClassName("slots-games__item-wrap")'
                )
                results[ref_urls[i]] = self.html_comparer.check_slots_html_tree(slots)

                # wd.close()

        return results


class HTMLComparer:
    @staticmethod
    def check_slots_html_tree(slots: List[WebElement]) -> bool | str:
        for slot in slots:
            play_button = slot.find_element(By.CLASS_NAME, 'slots-games__playfree')
            if not play_button:
                return 'There\'s no expected button'
            if not play_button.get_attribute('href'):
                return 'There\'s an element with expected class_name, but it\'s not a button'

        return True


class UtilityClass:
    def __init__(self):
        self.file_dir = pathlib.Path(__file__).parent.resolve() / 'list_of_projects.xlsx'
        self.new_file_dir = pathlib.Path(__file__).parent.resolve() / 'list_of_projects2.xlsx'
        self.projects_list = list()

    def get_list(self) -> List[str]:
        data_frame = pd.read_excel(self.file_dir)[['URL']]

        for value in data_frame.values:
            value = self.normalize_strings(*value)
            self.projects_list.append(value)

        return self.projects_list

    def normalize_strings(self, url: str) -> str:
        url_obj = urlparse(url)
        if url_obj.path == '/':
            url_obj = url_obj._replace(path='')
        new_url = url_obj._replace(scheme='https')
        return new_url.geturl()

    def save_results(self, results: list[str | bool]) -> None:
        data_frame = pd.read_excel(self.file_dir)
        data_frame.insert(3, 'RESULTS', results)
        data_frame.to_excel(self.new_file_dir)

if __name__ == '__main__':
    the_worker = UtilityClass()
    the_referee = HTMLComparer()
    the_dog = SeleniumFirefoxLocalAdapter(html_comparer=the_referee)

    projects = the_worker.get_list()
    results = the_dog.get_slots(projects)
    the_worker.save_results(list(results.values()))
