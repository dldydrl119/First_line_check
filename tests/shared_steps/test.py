from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import re

# 웹드라이버 초기화
def init_driver():
    driver = webdriver.Chrome(executable_path='/Users/leeyongg/webdriver/chromedriver')  # 경로를 수정
    return driver

# 웹사이트로 이동
def load_website(driver, url):
    driver.get(url)
    time.sleep(3)  # 페이지가 로드될 시간을 줍니다

# URL 기반 폴더 이름 생성 함수
def url_to_folder_name(url):
    sanitized_name = re.sub(r'\W+', '_', url)  # 특수 문자 제거하고 "_"로 대체
    return sanitized_name

# XPath 생성 함수
def get_element_xpath(element):
    components = []
    while element is not None:
        siblings = element.find_elements(By.XPATH, './preceding-sibling::*')
        index = len(siblings) + 1
        tag_name = element.tag_name
        components.append(f"{tag_name}[{index}]")
        parent = element.find_element(By.XPATH, './..')
        element = parent if parent.tag_name != "html" else None
    components.reverse()
    return "/" + "/".join(components)

# 화면에 표시된 요소만 추출하는 함수
def extract_displayed_elements(driver):
    elements_info = []
    target_tags = ['input', 'button', 'textarea', 'select', 'a']
    for tag in target_tags:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for index, element in enumerate(elements, start=1):
            if element.is_displayed() and element.size['width'] > 0 and element.size['height'] > 0:
                element_id = element.get_attribute('id')
                css_selector = f"#{element_id}" if element_id else tag
                classes = element.get_attribute("class")
                if classes and not element_id:
                    css_selector = f"{tag}." + ".".join(classes.split())
                text = element.text.strip() if element.text else f"index_{index}"
                sanitized_text = re.sub(r'\W+', '_', text)  # 특수 문자를 "_"로 대체
                xpath = get_element_xpath(element)  # 고유 XPath 생성
                elements_info.append({
                    'tag': tag,
                    'id': element_id,
                    'css_selector': css_selector,
                    'xpath': xpath,
                    'element': element,
                    'text': sanitized_text,
                    'base_name': generate_base_name({
                        'tag': tag,
                        'id': element_id,
                        'css_selector': css_selector,
                        'text': sanitized_text
                    }, "click" if tag in ['button', 'a'] else "input" if tag in ['input', 'textarea', 'select'] else "select", index)
                })
    return elements_info

# 이름 생성 함수
def generate_base_name(element_info, prefix, index):
    text = element_info['text'] if element_info['text'] else f"element_{index}"
    base_name = element_info['id'] if element_info['id'] else element_info['css_selector'].replace(".", "_")
    base_name = f"{prefix}_{index:03}_{text}_{base_name}".replace("-", "_").replace("#", "").replace(" ", "_")
    return base_name

# 스크린샷 저장 (너비와 높이를 다시 확인하여 0일 경우 스킵)
def save_element_screenshot(element, base_name, output_folder):
    if element.size['width'] > 0 and element.size['height'] > 0:
        output_path = os.path.join(os.getcwd(), output_folder)  # 상대 경로 처리
        os.makedirs(output_path, exist_ok=True)
        file_path = os.path.join(output_path, f"{base_name}.png")
        element.screenshot(file_path)
        print(f"스크린샷 저장: {file_path}")
    else:
        print(f"스킵: {base_name} - 크기가 0입니다.")

# POM 메서드 및 스크린샷 생성
def generate_function_code(element_info, output_folder, index):
    base_name = element_info['base_name']
    if element_info['tag'] in ['input', 'textarea', 'select']:
        action = "문자를 입력합니다"
    elif element_info['tag'] in ['button', 'a']:
        action = "버튼을 클릭합니다"
    elif element_info['tag'] == 'input' and element_info['element'].get_attribute('type') == 'radio':
        action = "버튼을 체크합니다"
    else:
        return None  # 해당하지 않는 경우 함수 생성 생략
    save_element_screenshot(element_info['element'], base_name, output_folder)
    if element_info['id']:
        locator = f'By.ID, "{element_info["id"]}"'
    else:
        locator = f'By.XPATH, "{element_info["xpath"]}"'
    if element_info['tag'] in ['input', 'textarea', 'select']:
        return f"""
    def {base_name}(self, text):
        \"\"\" {action} \"\"\"
        self.driver.find_element({locator}).send_keys(text)
        """
    else:
        return f"""
    def {base_name}(self):
        \"\"\" {action} \"\"\"
        self.driver.find_element({locator}).click()
        """

# Page Object Model 클래스 생성
def generate_pom_class(elements_info, class_name="PageObject", output_folder="output"):
    elements_info.sort(key=lambda x: x['base_name'])
    class_code = f"""from selenium.webdriver.common.by import By\nclass {class_name}:\n    def __init__(self, driver):\n        self.driver = driver\n"""
    for index, element_info in enumerate(elements_info, start=1):
        function_code = generate_function_code(element_info, output_folder, index)
        if function_code:
            class_code += function_code
    return class_code

# Python 파일에 저장
def save_to_file(class_code, output_folder, file_name="page_objects.py"):
    output_path = os.path.join(os.getcwd(), output_folder)
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, file_name)
    with open(file_path, "w") as f:
        f.write(class_code)
    print(f"{file_path} 파일에 저장되었습니다.")

# 전체 프로세스 실행
def automate_pom_creation(urls):
    driver = init_driver()
    try:
        for url in urls:
            folder_name = url_to_folder_name(url)
            load_website(driver, url)
            elements_info = extract_displayed_elements(driver)
            class_code = generate_pom_class(elements_info, class_name="PageObject", output_folder=folder_name)
            save_to_file(class_code, folder_name)
    finally:
        driver.quit()

# 실행할 URL 목록
urls = [
    "https://www.gmarket.co.kr",
    "https://signinssl.gmarket.co.kr/login/login?url=https%3A%2F%2Fwww.gmarket.co.kr%2F"
]
automate_pom_creation(urls)
