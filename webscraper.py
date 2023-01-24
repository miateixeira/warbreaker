from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

OUTPUT_DIR = "./output/"

def processElement(element):
    text = element.get_attribute("innerHTML")

    # convert italics tags to \textit{...}
    text = text.replace('<i>', '\\textit{')
    text = text.replace('</i>', '}')

    # convert non-breaking space
    text = text.replace('&nbsp;', '~')

    return text + "\n\n"

def elementsToLatex(heading, all_elements):

    filename = heading.text.split(' ')[1:]
    filename = '_'.join(filename)
    filename_dir = OUTPUT_DIR + filename.lower() + ".tex"

    with open(filename_dir, 'w') as f:
        # f.write("\\documentclass{article}\n\n\n")
        # f.write("\\begin{document}\n\n\n")
        # Section title
        section_title = "\\section{" + filename.title() + "}\n\n"
        f.write(section_title)

        # Process elements
        for element in all_elements:
            tex = processElement(element)
            f.write(tex)

        # f.write("\\end{document}\n\n\n")

def getPageContent(driver):
    """
    Get the heading and relevant text column elements for the current chapter
    """

    # Get section heading text
    heading = driver.find_element(By.CLASS_NAME, "vc_custom_heading")

    # Get relevant main text elements
    text_column_elements = driver.find_elements(By.CLASS_NAME, "wpb_text_column")
    wrapper_element = text_column_elements[1].find_element(By.CLASS_NAME, "wpb_wrapper")
    all_elements = wrapper_element.find_elements(By.XPATH, "*")

    elementsToLatex(heading, all_elements)

def doScraping():
    """
    Use driver object to scrape all available chapter pages
    """

    driver_path = "./chromedriver"
    brave_path = "/usr/bin/brave"
    
    option = webdriver.ChromeOptions()
    option.binary_location = brave_path
    
    s = Service(driver_path)
    
    driver = webdriver.Chrome(service=s, options=option)
    
    # url = "https://www.brandonsanderson.com/warbreaker-introduction/"
    url = "https://www.brandonsanderson.com/warbreaker-epilogue/"
    driver.get(url)

    getPageContent(driver)
    
    # NAVIGATE TO NEXT SECTION
    while driver.find_element(By.CLASS_NAME, "nav-next").get_attribute('href') is not None:
        # Navigate to the next chapter
        driver.find_element(By.CLASS_NAME, "nav-next").click()
    
        # Get page contents
        getPageContent(driver)
    
    print("That's all, folks!")
    
    driver.quit()

if __name__ == "__main__":
    doScraping()
