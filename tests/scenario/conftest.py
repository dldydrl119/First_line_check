"""
This module contains shared fixtures.
"""

import pytest
import selenium.webdriver
import platform
import getpass
import os
import importlib
import pickle
# from functools import cache
from _pytest.cacheprovider import Cache
from src.gtas_python_core.gtas_python_core_testrail import *
from applitools.selenium import *
from selenium.webdriver import Chrome, ChromeOptions
import secrets # 랜덤 토큰 (해시) 생성 모듈`
import os, re
import json
import tempfile
from sys import platform as pf
from applitools.common.errors import DiffsFoundError


# OS정보 / PC 사용자명 / 해시 토큰 가져오기
os_version=platform.platform()
username = getpass.getuser()
token_value=secrets.token_hex(nbytes=16)
token_goods_value=secrets.token_hex(nbytes=16)
cache_path = os.path.join(os.path.dirname(__file__))
cache_file_path = os.path.join(cache_path, token_value)
cache_file_path2 = os.path.join(cache_path, token_goods_value)
vault_login = Vault("gmarket")

# PATH List
if 'mac' in os_version:  # 맥 OS인 경우
    root_path = os.path.dirname(__file__).replace('/tests/scenario', '')

else: # 윈도우인 경우
    root_path=os.path.dirname(__file__).replace('\\tests\\scenario','')

# 경로에 따른 config.json 경로 설정
def get_config_path():
    if 'Windows' in os_version:
        return os.path.join(root_path, "config.json")
    elif 'mac' in os_version:
        return os.path.join(root_path, "config.json")
    return None

def delete_long_files_in_dir(directory='.'):
    """
    주어진 디렉토리에서 파일명이 32자 이상이고 확장자가 없는 파일을 삭제하는 함수
    """
    # 디렉토리의 파일과 폴더 목록을 가져옵니다.
    for filename in os.listdir(directory):
        # 파일명의 길이가 32자 이상이고 확장자가 없는 경우
        print(filename)
        if len(filename) >= 32 and '.' not in filename:
            file_path = os.path.join(directory, filename)
            try:
                # 파일을 삭제합니다.
                os.remove(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}. Reason: {e}")

def delete_module_long_json_files_in_dir(module_name=''):
    """
    주어진 모듈의 디렉토리에서 파일명이 32자 이상이고 확장자가 없는 파일을 삭제하는 함수
    """
    # 디렉토리의 파일과 폴더 목록을 가져옵니다.
    # module_path = os.path.dirname(module_name+"."+__file__)
    # 모듈을 불러옵니다.
    module = importlib.import_module(module_name)

    # 모듈이 위치한 디렉토리 경로를 얻습니다.
    module_path = os.path.dirname(module.__file__)
    for filename in os.listdir(module_path):
        # 파일명의 길이가 32자 이상이고 확장자가 없는 경우
        if len(filename) >= 32 and filename.endswith('.json'):
            file_path = os.path.join(module_path, filename)
            try:
                # 파일을 삭제합니다.
                os.remove(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}. Reason: {e}")

# pytest_addoption 함수를 사용해 커맨드 라인에 '--jsonfile' 옵션을 추가
def pytest_addoption(parser):
    parser.addoption(
        "--jsonfile",
        action="store", # action 지정하는 값에 따라 옵션이나 인자를 처리 / store : 옵션또는 인자값을 저장, append: 옵션 또는 인자값을 리스트에 추가
        default="", # 옵션의 기본값을 지정하는 인자 (옵션을 지정하지 않았을 때 사용될 값을 지정함
        help="테스트 데이터를 포함한 JSON 파일의 경로", # --help 옵션으로 도움말을 출력할 때 사용
    )

def pytest_configure(config): # 사용자 정의 마커를 등록함. 해당 마커는 테스트 타입에 따라 테스트를 구분하는 데 사용
    config.addinivalue_line("markers", "flaky: Mark a test as flaky")
    
def pytest_sessionfinish(session, exitstatus):
    cached_coupon_file = 'cached_coupon_id.txt'
    if os.path.exists(cached_coupon_file):
        os.remove(cached_coupon_file)
        print(f"# {cached_coupon_file} 파일이 삭제되었습니다.")
    else:
        print(f"# {cached_coupon_file} 파일이 존재하지 않습니다.")
# --------------------------------------------------------------------------------
# Session-Scope Fixtures
#   These fixtures run one time for the whole test suite.
#   Subsequent calls use the value cached from the first execution.
# --------------------------------------------------------------------------------

# config 픽스쳐를 정의 / 이 픽스쳐는 전체 테스트 스위트 전에 한 번만 실행
@pytest.fixture(scope='session')
def config():
    # config.json 파일을 읽기
    with open('config.json') as config_file:
        config = json.load(config_file)  # 읽어온 파일을 config 변수에 저장

    # 읽어온 설정 값들의 유효성을 검사
    assert config['driver'] in ['Firefox', 'Chrome', 'Headless Chrome']  # 브라우저 유형이 올바른지 확인
    assert isinstance(config['implicit_wait'], int)  # 암시적 대기 값이 정수 타입인지 확인
    assert config['implicit_wait'] > 0  # 암시적 대기 값이 양수인지 확인

    # 유효성 검사를 통과한 설정 사전(config)을 반환
    # 이렇게 하면 다른 테스트 함수에서 이 픽스쳐를 사용하여 설정 값을 가져올 수 있음
    return config


@pytest.fixture
def driver(config):
    # 웹 드라이버 인스턴스를 초기화합니다.

    # config에 지정된 브라우저가 Firefox인 경우
    if config['driver'] == 'Firefox':
        # 운영 체제가 Windows인 경우
        if 'Windows' in os_version:
            opts = selenium.webdriver.FirefoxOptions()
            opts.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            b = selenium.webdriver.Firefox(
                executable_path=r'C:/webdriver/geckodriver.exe', options=opts)
            b.maximize_window()

        # 운영 체제가 macOS인 경우
        elif 'mac' in os_version:
            opts = selenium.webdriver.FirefoxOptions()
            b = selenium.webdriver.Firefox(
                executable_path="/Users/"+username+"/webdriver/geckodriver")
            b.maximize_window()

        else:
            print("지원하지 않는 OS 환경입니다.")

    # config에 지정된 브라우저가 Chrome인 경우
    elif config['driver'] == 'Chrome':
        # 운영 체제가 Windows인 경우
        if 'Windows' in os_version:
            opts = selenium.webdriver.ChromeOptions()
            opts.add_argument("--start-maximized")
            b = selenium.webdriver.Chrome(
                options=opts, executable_path="c:/webdriver/chromedriver.exe")

        # 운영 체제가 macOS인 경우
        elif 'mac' in os_version:
            opts = selenium.webdriver.ChromeOptions()
            opts.add_argument("--start-maximized")
            b = selenium.webdriver.Chrome(
                options=opts, executable_path="/Users/"+username+"/webdriver/chromedriver")

        else:
            print("지원하지 않는 OS 환경입니다.")

    # config에 지정된 브라우저가 Headless Chrome인 경우
    elif config['driver'] == 'Headless Chrome':
        # 운영 체제가 Windows인 경우
        if 'Windows' in os_version:
            opts = selenium.webdriver.ChromeOptions()
            opts.add_argument("--window-size=1920,1080")  # 해상도를 1920x1080으로 설정
            opts.add_argument('headless')  # headless 모드 활성화
            b = selenium.webdriver.Chrome(
                options=opts, executable_path="c:/webdriver/chromedriver.exe")

        # 운영 체제가 macOS인 경우
        elif 'mac' in os_version:
            opts = selenium.webdriver.ChromeOptions()
            opts.add_argument('headless')  # headless 모드 활성화
            b = selenium.webdriver.Chrome(
                options=opts, executable_path="/Users/" + username + "/webdriver/chromedriver")

        else:
            print("지원하지 않는 OS 환경입니다.")

    else:  # 지원되지 않는 브라우저인 경우
        raise Exception(f'Browser "{config["driver"]}" is not supported')

    # 웹 드라이버가 요소가 나타날 때까지 기다리도록 암시적 대기 시간을 설정
    b.implicitly_wait(config['implicit_wait']) # 암시적 대기시간 설정

    # 이 픽스쳐를 사용하는 테스트 함수에 웹 드라이버 인스턴스(b)를 전달
    yield b # 브라우저 인스턴스

    # 테스트 함수가 완료된 후 웹 드라이버 인스턴스를 종료하여 리소스를 정리
    b.quit() # 인스턴스 종료

# 사용자 정의 캐시 픽스처 생성
@pytest.fixture(scope="session")
def custom_cache(request) -> Cache:
    return request.config.cache

# token 픽스처 (테스트레일 결과 기록을 위한 token)
@pytest.fixture(scope="session")
def token(custom_cache):
    token = token_value
    with open(cache_file_path, 'wb') as f:
        pickle.dump(token, f)
    return token

# token_goods (상품 번호 기록을 위한 Token)
@pytest.fixture(scope="session")
def token_goods(custom_cache):
    token_goods = token_goods_value
    with open(cache_file_path2, 'wb') as f:
        pickle.dump(token_goods, f)
        f.close()  # 명시적으로 파일을 닫음
    yield token_goods  # 사용할 token_goods 반환

# 테스트 레일 케이스 묶음 리스트 생성
@pytest.fixture(autouse=True)
def create_test_case_list(config):
    # TestRail에서 case_ids 가져오기
    test_rail = TestRail(config)
    case_ids_from_testrail = test_rail.get_test_cases_by_section_name(config['project_id'], config['section_name'])

    # 만약 TestRail에서 case_ids를 못 가져오면, 파일명에서 직접 추출
    if not case_ids_from_testrail:
        print("TestRail에서 case_id를 가져오지 못했습니다. 파일명에서 추출을 시도합니다.")
        case_ids = extract_case_ids_from_files()
    else:
        case_ids = sorted(case_ids_from_testrail)
        case_ids = [str(x) for x in case_ids]  # 문자열로 변환

    # config.json 업데이트
    update_config_with_case_ids(case_ids)


# 파일명에서 case_id 추출 (fallback 방식)
def extract_case_ids_from_files():
    case_ids = []

    if 'Windows' in os_version:
        directory_path = root_path + "\\tests\\scenario"
    elif 'mac' in os_version:
        directory_path = root_path + "/tests/scenario"

    # 파일명에서 'test_c'로 시작하는 파일을 찾아 case_id 추출
    for filename in os.listdir(directory_path):
        if filename.endswith(".py") and filename.startswith("test_c"):
            case_id = re.findall(r'c(\d+)', filename)
            if case_id:
                case_ids.extend(map(int, case_id))  # 여러 숫자가 있을 경우 모두 추가

    return sorted([str(x) for x in case_ids])


# config.json에 case_id 업데이트
def update_config_with_case_ids(case_ids):
    config_path = get_config_path()
    if not config_path:
        print("config.json 경로를 찾을 수 없습니다.")
        return

    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # case_ids를 config에 업데이트
    config_data["case_id"] = case_ids

    # 임시 파일을 생성하여 config.json 업데이트
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(config_data, temp_file, indent=4, ensure_ascii=False)

    # 임시 파일을 원본 파일로 교체
    os.replace(temp_file.name, config_path)
  

# 테스트 레일 스위트 생성 픽스쳐
@pytest.fixture(autouse=True)  # 모든 테스트에 자동으로 적용
def create_test_rail_suite(request, config, custom_cache):  # request를 추가로 인자로 받음
    # 테스트 파일의 고유한 식별자를 사용하여 캐시 키를 생성
    test_file_path = request.fspath
    cache_key = f"test_rail_created"
    # cache_key = f"test_rail_created_{test_file_path}"

    # 캐시에 해당 키의 값이 없거나 False 인 경우
    if not custom_cache.get(cache_key, False):
        # config.json 파일을 읽어서 config 변수에 저장
        with open('config.json') as config_file:
            config = json.load(config_file)

        # 테스트 레일 스위트를 생성
        with open(cache_file_path, 'wb') as f:
            pickle.dump(token_value, f)

        test_rail = TestRail(config)

        # 테스트 파일 이름을 얻기 위해 해쉬값 사용
        with open(cache_file_path, 'rb') as f:
            test_file_name = pickle.load(f)


        # 테스트 run sheet 생성
        test_rail.run_test_suite(runsheet_name=config['runsheet_name'],project_id=config['project_id'], suite_id=config['suite_id'], include_all=False,
                                 case_ids=config['case_id'], file_name=(test_file_name), milestone_id=int(config['milestone_id']))

        # 테스트 레일 스위트가 생성되었음을 나타내는 캐시 값을 설정
        # 이렇게 하면 다음 번 테스트 실행 때 중복된 스위트가 생성 안됨
        custom_cache.set(cache_key, True)

@pytest.fixture(scope="session", autouse=True)
def update_config_file(request):
    # config.json 파일 경로 설정

    # 운영 체제가 Windows인 경우
    if 'Windows' in os_version:
        config_path = os.path.join(root_path + "\\config.json")

    # 운영 체제가 macOS인 경우
    elif 'mac' in os_version:
        config_path = os.path.join(root_path + "/config.json")

    # config.json 파일 열기
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # config.json 파일의 case_id 키의 데이터 삭제
    config_data["case_id"] = [""]

    # 테스트가 끝날 때 config.json 파일 업데이트
    def fin():
        with open(config_path, 'w') as file:
            json.dump(config_data, file, indent=4)

    request.addfinalizer(fin)


@pytest.fixture(scope='session', autouse=True)
def cleanup_temp_files(request,config):
    if config["multiple_test_use"]==False:
        print("병렬 테스트 하지 않음")
        # 테스트들이 모두 실행된 후에 호출될 함수를 정의합니다.
        def cleanup_files():
            delete_long_files_in_dir('./tests/scenario')
        def cleanup_json_files():
            delete_module_long_json_files_in_dir('src.gtas_python_core.gtas_python_core_testrail')

        # finalizer로 위에서 정의한 remove_files 함수를 등록합니다.
        request.addfinalizer(cleanup_files)
        request.addfinalizer(delete_long_files_in_dir)
        request.addfinalizer(cleanup_json_files)
    else:
        print("병렬 테스트 사용")

# conftest.py 파일에 이 코드를 추가합니다.
def pytest_exception_interact(node, call, report):
    if "handle_diffs_found_error" in node.keywords:
        if isinstance(call.excinfo.value, DiffsFoundError):
            report.outcome = "passed"
