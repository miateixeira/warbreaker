from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

OUTPUT_DIR = "./output/"
MAIN_TEX_FILENAME = OUTPUT_DIR + "warbreaker_full.tex"
TEX_INCLUDES = []

def processAnnotations(driver, element):
    links = element.find_elements(By.TAG_NAME, "a")

    for link in links:
        link.click()

        try:
            heading = driver.find_element(By.CLASS_NAME, "vc_custom_heading")
        except:
            driver.back()
            continue

        # Don't follow links to things that aren't annotations
        if "ANNOTATION" not in heading.text:
            driver.back()
            continue

        # Get .tex filename
        header = heading.text.split(' ')
        header.pop(1)
        filename = OUTPUT_DIR + '_'.join(header).lower() + ".tex"

        # get text elements
        text_column_elements = driver.find_elements(By.CLASS_NAME, "wpb_text_column")
        wrapper_element = text_column_elements[1].find_element(By.CLASS_NAME, "wpb_wrapper")
        all_elements = wrapper_element.find_elements(By.XPATH, "*")

        TEX_INCLUDES.append(filename)
        with open(filename, 'w') as f:
            # Write section title to .tex file
            section_title = "\\section{" + ' '.join(header).title() + "}\n\n"
            f.write(section_title)

            for element in all_elements:
                text = element.get_attribute("innerHTML")
                if "href" in text:
                    text = ''
                # Italics
                text = text.replace('<i>', '\\textit{')
                text = text.replace('</i>', '}')
                # Non-breaking space
                text = text.replace('&nbsp;', '~')
                # Make bold text into subsection titles
                text = text.replace('<b>', '\\subsection*{')
                text = text.replace('</b>', '}')
                text = text + "\n\n"
                f.write(text)

        driver.back()

def processElement(driver, element):
    # process horizontal rules
    if "<hr>" in element.get_attribute("outerHTML"):
        return "\\bigskip \\hrule \\bigskip\n\n"

    text = element.get_attribute("innerHTML")

    # process annotations
    if "href=" in text:
        processAnnotations(driver, element)
        return ""

    # process table titles
    if "<h4>" in element.get_attribute("outerHTML"):
        return '\\subsubsection*{' + text + '}\n\n'

    text = text.replace('<tbody>', '\\begin{center}\n\\begin{tabular}{p{2cm}p{3cm}p{4cm}p{0cm}} \\hline')
    text = text.replace('</tbody>', '\\end{tabular}\n\\end{center}')
    text = text.replace('<tr>', '')
    text = text.replace('</tr>', '\\\\ \\hline')
    text = text.replace('<th>', '\\centering \\textbf{')
    text = text.replace('</th>', '}\n&')
    text = text.replace('<td>', '\\centering ')
    text = text.replace('</td>', '\n&')
    text = text.replace('<br>', '')

    # convert italics tags to \textit{...}
    text = text.replace('<i>', '\\textit{')
    text = text.replace('</i>', '}')

    # convert non-breaking space
    text = text.replace('&nbsp;', '~')

    # process description lists
    if "<dl>" in element.get_attribute("outerHTML"):
        text = text.replace('<dt>', '\t\\item[')
        text = text.replace('</dt>', ']')
        text = text.replace('<dd>', '\t')
        text = text.replace('</dd>', '\n')

        return "\\begin{description}\n" + text + "\\end{description}\n\n"

    return text + "\n\n"

def elementsToLatex(driver, heading, all_elements):
    header = heading.text.split(' ')[1:]
    filename_dir = OUTPUT_DIR + '_'.join(header).lower() + ".tex"

    TEX_INCLUDES.append(filename_dir)
    with open(filename_dir, 'w') as f:
        # f.write("\\documentclass{article}\n\n\n")
        # f.write("\\begin{document}\n\n\n")
        # Section title
        section_title = "\\section{" + ' '.join(header).title() + "}\n\n"
        f.write(section_title)

        # Process elements
        for element in all_elements:
            tex = processElement(driver, element)
            f.write(tex)

        # f.write("\\end{document}\n\n\n")

def getPageContent(driver):
    """
    Get the heading and relevant text column elements for the current chapter
    """

    # Get section heading text
    try:
        heading = driver.find_element(By.CLASS_NAME, "vc_custom_heading")
    except:
        print("no css selector vc_custom_heading")
    
    # try:
        # heading = driver.find_element(By.CLASS_NAME, "vc_custom_1571860185277")
    # except:
        # print("no css selector found")

    # Get relevant main text elements
    text_column_elements = driver.find_elements(By.CLASS_NAME, "wpb_text_column")
    wrapper_element = text_column_elements[1].find_element(By.CLASS_NAME, "wpb_wrapper")
    all_elements = wrapper_element.find_elements(By.XPATH, "*")

    elementsToLatex(driver, heading, all_elements)

def createMainTexFile():
    with open(MAIN_TEX_FILENAME, 'w') as f:
        preamble = "\\documentclass[12pt]{article}\n\n\\usepackage[utf8]{inputenc}\n\n\\begin{document}\n\n"
        f.write(preamble)

        includes = [x.replace(OUTPUT_DIR,'').replace('.tex','') for x in TEX_INCLUDES]
        for inc in includes:
            line = "\\include{" + inc + "}\n\n"
            f.write(line)

        end_doc = "\\end{document}"
        f.write(end_doc)

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
    
    url = "https://www.brandonsanderson.com/warbreaker-introduction/"
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

    createMainTexFile()

if __name__ == "__main__":
    doScraping()
