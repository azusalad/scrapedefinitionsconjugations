from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import os
from tqdm import tqdm
from config import *

class vocabword():
    def __init__(self,word):
        self.word = word

    def add_definitions(self, driver):
        """Gets the definitions of all the words from Merriam Webster"""
        driver.get('https://www.merriam-webster.com/dictionary/' + str(self.word))
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        pos = driver.find_element(By.CSS_SELECTOR,".important-blue-link").text
        content = driver.find_element(By.CLASS_NAME,'vg') # find the content that contains the definitions
        definitions = content.find_elements(By.CLASS_NAME,"dtText")
        filtered = []
        for y in definitions:
            filtered.append(y.text.split(': ')[1].lower().rstrip()) # get actual definition not synonym
        definitions_str = "; ".join(str(e) for e in filtered)
        self.pos = pos
        self.definition = definitions_str
        time.sleep(cooldown)

    def add_conjugations(self, driver):
        """Gets the conjugations of all the words from Collins Dictionary"""
        driver.get('https://www.collinsdictionary.com/dictionary/english/' + str(self.word))
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'orth')))
        time.sleep(cooldown)
        try:
            content = driver.find_element(By.XPATH,'/html/body/main/div[3]/div[1]/div/div[2]/div/div[1]/div[4]/div/div/div[5]')
        except:
            content = driver
        orth = content.find_elements(By.CLASS_NAME,'orth')
        pos = content.find_elements(By.CLASS_NAME,'pos')
        conjugations_list = []
        for y in orth:
            try:
                conjugations_list.append(y.text + " (" + str(pos[orth.index(y)].text.lower()) + ")")
            except:
                print('warning there is an OR in word ' + str(self.word))
        self.conjugation = "; ".join(str(e) for e in conjugations_list)

    def __str__(self):
        try:
            self.pos
        except AttributeError:
            return(f'{self.word}\tno pos\tno definition\tno conjugations')
        else:
            try:
                self.conjugation
            except AttributeError:
                return(f'{self.word}\t{self.pos}\t{self.definition}\tno conjugations')
            else:
                return(f'{self.word}\t{self.pos}\t{self.definition}\t{self.conjugation}')

def get_words():
    """Turns all the words in words.txt into a list with each element being a word"""
    with open('words.txt', 'r') as f:
        words = [vocabword(x.strip()) for x in f.readlines() if x != '']
    return words

def create_driver():
    """Create geckodriver given a path and ublock origin xpi file (optional)"""
    options = Options()
    options.headless = False
    print('creating driver')
    driver = webdriver.Firefox(options=options, executable_path=gecko_path)
    try:
        driver.install_addon(os.path.join(os.getcwd(), ublock_path), temporary=True)
    except:
        print('Cannot install ublock origin, skipping')
    return driver

def main():
    words = get_words()
    driver = create_driver()

    print('Getting definitions')
    for vocabword in tqdm(words):
        vocabword.add_definitions(driver)
    # just in case conjugations errors you still have a backup of your work
    with open('tmp.txt', 'w') as f:
        for x in words:
            f.write(str(x) + '\n')

    print('Getting conjugations')
    for vocabword in tqdm(words):
        vocabword.add_conjugations(driver)
    # just in case writing to file errors you still have a backup of your work
    with open('tmp.txt', 'w') as f:
        for x in words:
            f.write(str(x) + '\n')

    print('Writing to ' + str(output_filename))
    f = open(output_filename, 'w')
    f.write('Word\tpos\tdefinition\tconjugations\toriginal sentence\n')
    for vocabword in words:
        f.write(str(vocabword) + '\n')
    f.close()

    driver.close()

if __name__ == '__main__':
    main()
