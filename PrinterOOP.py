from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures


def setwebdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("C:\webdrivers\chromedriver.exe", options=chrome_options)

    driver.set_page_load_timeout(10)
    return driver


def get_printer_model(url):
        urlLines = "http://" + url.strip()
        print(urlLines)
        try:
            driver= setwebdriver()

            driver.get(urlLines.strip())

            model = driver.title
            print(model)
            if model == "B432" or model == "B412":
                printer = Oki("oki", url)
                print(printer)
                driver.close()
                return printer
            elif model == "MB492":
                printer = Oki492("oki", url)
                print(printer)
                driver.close()
                return printer

            elif model.startswith("Lexmark"):
                printer = Lexmark("lexmark", url)
                print(printer)
                driver.close()
                return printer

            else:
                print(model)
                print(url)
                printer = Oki("offline",url)
                driver.close()
                return printer
                print("unknown model or offline")

        except:
            printer = Oki("offline", url)
            driver.close()
            return printer
            print("not nice offline")


class Printers:

    number_printers = []

    def __init__(self, model, ip, location=None, toner=None, drum=None, alert=None):
        self.model = model
        self.ip = ip
        self.location = location
        self.toner = toner
        self.drum = drum
        self.alert = alert
        self.url = "http://"+ip

        self.add_printer()
    @classmethod
    def number_of_printers(cls):
        return len(cls.number_printers)

    def add_printer(self):
        self.number_printers.append(self)

    def get_location(self):
        self.location = "Somere else"
        return self.location

    def get_alerts(self):
        alert = "Alert Status Not Supported"
        return alert

    def update(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f1 = executor.submit(self.get_status)
            f2 = executor.submit(self.get_supplies_level)

            self.model, self.location, self.alert = f1.result()
            self.toner, self.drum = f2.result()

    def print_status(self):
        print("Model: " + self.model)
        print("Ip: " + self.ip)
        print("Location: " + self.location)
        print("Toner Level: " + self.toner)
        print("Drum Level: " + self.drum)
        print("Alerts: " + self.alert + "\n")


class Lexmark(Printers):
    MODEL_CSS = "body > table > tbody > tr > td:nth-child(3) > span"
    TONER_CSS = "body > table:nth-child(3) > tbody > tr:nth-child(3) > td > b"
    DRUM_CSS = "body > table:nth-child(9) > tbody > tr:nth-child(6) > td:nth-child(2)"
    LOCATION_CSS = "body > table > tbody > tr > td:nth-child(3) > b:nth-child(7)"
    ALERT_CSS = "body > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(1) > td > font"
    ALERT_CSS_2 = "body > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(2) > td > font"
    DRUM_CSS_2 = "body > table:nth-child(9) > tbody > tr:nth-child(5) > td:nth-child(2)"

    @staticmethod
    def get_status_url(url):
        return url+"/cgi-bin/dynamic/topbar.html"

    @staticmethod
    def get_supplies_url(url):
        return url+"/cgi-bin/dynamic/printer/PrinterStatus.html"

    def get_supplies_level(self):

        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            try:
                tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text
                if tonerLevel == "Black Toner" or tonerLevel =="Black Cartridge":
                    tonerLevel ="0%"
            except:
                tonerLevel = "0%"
            try:
                drumLevel =driver.find_element_by_css_selector(self.DRUM_CSS).text

            except:
                drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS_2).text


            driver.close()
            return tonerLevel, drumLevel

        except:
            tonerLevel = "OFFLINE"
            drumLevel = "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            print("couldn't retrieve toner information, probably offline " + self.url)
            return tonerLevel, drumLevel

    def get_status(self):
        try:
            driver = setwebdriver()
            driver.get(self.get_status_url(self.url))
            modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            alertStatus = driver.find_element_by_css_selector(self.ALERT_CSS).text
            try:
                alertStatus2 = driver.find_element_by_css_selector(self.ALERT_CSS_2).text
                alertStatus2 = (", "+ alertStatus2)
            except:
                alertStatus2 = " "
            driver.close()

            return modelStatus, location, (alertStatus+ alertStatus2)
        except:
            modelStatus="OFFLINE"
            location="OFFLINE"
            alertStatus = "OFFLINE"

            print("couldn't retrieve alert status, probably offline")
            return modelStatus, location, alertStatus

    def get_toner_level(self):

        try:
            driver= setwebdriver()

            driver.get(self.get_supplies_url(self.url))
            try:
                tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text
                if tonerLevel == "Black Toner" or tonerLevel =="Black Cartridge":
                    tonerLevel ="0%"
            except:
                tonerLevel = "0%"
            driver.close()
            print(tonerLevel)
            return tonerLevel

        except:
            tonerLevel = "OFFLINE"
            print("couldn't retrieve toner information, probably offline" + self.url)
            return tonerLevel

    def get_drum_level(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            if driver.find_element_by_css_selector(self.DRUM_CSS):
                drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS).text
            elif driver.find_element_by_css_selector(self.DRUM_CSS_2):
                drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS_2).text

            driver.close()

            return drumLevel
        except:
            drumLevel= "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            return drumLevel

    def get_alerts(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            alertStatus = driver.find_element_by_css_selector(self.ALERT_CSS).text
            try:
                alertStatus2 = driver.find_element_by_css_selector(self.ALERT_CSS_2).text
                alertStatus2 = (", "+ alertStatus2)
            except:
                alertStatus2 = " "
            driver.close()
            return (alertStatus+ alertStatus2)
        except:
            alertStatus = "OFFLINE"

            print("couldn't retrieve alert status, probably offline")
            return alertStatus

    def get_location(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            driver.close()
            return location
        except:
            location = "Unknown"
            print("couldn't retrieve location, probably offline")
            return location

    def get_model(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            driver.close()
            return modelStatus
        except:
            modelStatus = "OFFLINE"
            print("couldn't retrieve model, probably offline")
            return modelStatus


class Oki(Printers):
    MODEL_CSS = "body > form > table:nth-child(4) > tbody > tr > td:nth-child(1) > " \
                "table:nth-child(2) > tbody > tr:nth-child(1) > td.normal"
    TONER_CSS = "body > form > p:nth-child(3) > table:nth-child(2) > tbody > tr:nth-child(5) > td"
    DRUM_CSS = "body > form > p:nth-child(3) > table:nth-child(3) > tbody > tr:nth-child(2) > td"
    LOCATION_CSS = "body > form > table:nth-child(4) > tbody > tr > td:nth-child(1) > " \
                   "table:nth-child(2) > tbody > tr:nth-child(8) > td.normal"
    ALERT_CSS = "body > form > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(1) > " \
                "div > table > tbody > tr:nth-child(2) > td.sub_item_color > div > table > tbody > " \
                "tr:nth-child(2) > td:nth-child(2) > b > font"

    @staticmethod
    def get_status_url(url):
        return url+"/status.htm"

    @staticmethod
    def get_supplies_url(url):
        return url+"/printer/suppliessum.htm"

    def get_supplies_level(self):

        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text
            drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS).text
            driver.close()
            return tonerLevel, drumLevel

        except:
            tonerLevel = "OFFLINE"
            drumLevel = "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            print("couldn't retrieve toner information, probably offline " + self.url)
            return tonerLevel, drumLevel

    def get_status(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            alertStatus = driver.find_element_by_css_selector(self.ALERT_CSS).text

            driver.close()
            return modelStatus, location, alertStatus
        except:
            modelStatus = "OFFLINE"
            location = "OFFLINE"
            alertStatus = "OFFLINE"
            print("couldn't retrieve alert status, probably offline")
            return modelStatus, location, alertStatus

    def get_toner_level(self):

        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text

            driver.close()
            return tonerLevel

        except:
            tonerLevel = "OFFLINE"

            print("couldn't retrieve toner information, probably offline" + self.url)
            return tonerLevel

    def get_drum_level(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS).text
            driver.close()
            return drumLevel
        except:
            drumLevel= "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            return drumLevel



    def get_alerts(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            alertStatus = driver.find_element_by_css_selector(self.ALERT_CSS).text
            driver.close()
            return alertStatus
        except:
            alertStatus = "OFFLINE"
            print("couldn't retrieve alert status, probably offline")
            return alertStatus

    def get_location(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            driver.close()
            return location
        except:
            location = "Unknown"
            print("couldn't retrieve location, probably offline")
            return location

    def get_model(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            driver.close()
            return modelStatus
        except:
            modelStatus = "OFFLINE"
            print("couldn't retrieve model, probably offline")
            return modelStatus


class Oki492(Printers):
    MODEL_CSS = "body > form > table:nth-child(2) > tbody > tr > td:nth-child(1) > " \
                "table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2)"
    TONER_CSS = "body > form > p > table:nth-child(2) > tbody > tr.sub_item_color > td:nth-child(3)"
    DRUM_CSS = "body > form > p > table:nth-child(3) > tbody > tr.sub_item_color > td:nth-child(2)"
    LOCATION_CSS = "body > form > table:nth-child(2) > tbody > tr > td:nth-child(1) > " \
                   "table:nth-child(3) > tbody > tr:nth-child(8) > td:nth-child(2)"


    @staticmethod
    def get_status_url(url):
        return url+"/status.htm"

    @staticmethod
    def get_supplies_url(url):
        return url+"/printer/suppliessum.htm"

    def get_supplies_level(self):

        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text
            drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS).text
            driver.close()
            return tonerLevel, drumLevel

        except:
            tonerLevel = "OFFLINE"
            drumLevel = "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            print("couldn't retrieve toner information, probably offline" + self.url)
            return tonerLevel, drumLevel

    def get_status(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            try:
                modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            except:
                modelStatus="cant retrieve"
                print("cant retrieve model status")
            try:
                location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            except:
                location="cant retrive"
                print("cant retrieve location")
            alertStatus= "Not supported"

            driver.close()
            return modelStatus, location, alertStatus
        except:
            modelStatus = "OFFLINE"
            location = "OFFLINE"
            alertStatus = "Not Supported"
            print("couldn't retrieve alert status, probably offline")
            driver.close()
            return modelStatus, location, alertStatus
    def get_toner_level(self):

        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            tonerLevel = driver.find_element_by_css_selector(self.TONER_CSS).text
            driver.close()
            return tonerLevel

        except:
            tonerLevel = "OFFLINE"
            print("couldn't retrieve toner information, probably offline" + self.url)
            return tonerLevel

    def get_drum_level(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_supplies_url(self.url))
            drumLevel = driver.find_element_by_css_selector(self.DRUM_CSS).text
            driver.close()
            return drumLevel
        except:
            drumLevel= "OFFLINE"
            print("couldn't retrieve drum information, probably offline")
            return drumLevel

    def get_location(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            location = driver.find_element_by_css_selector(self.LOCATION_CSS).text
            driver.close()
            return location
        except:
            location = "Unknown"
            print("couldn't retrieve location, probably offline")
            return location

    def get_model(self):
        try:
            driver= setwebdriver()
            driver.get(self.get_status_url(self.url))
            modelStatus = driver.find_element_by_css_selector(self.MODEL_CSS).text
            driver.close()
            return modelStatus
        except:
            modelStatus = "OFFLINE"
            print("couldn't retrieve model, probably offline")
            return modelStatus



