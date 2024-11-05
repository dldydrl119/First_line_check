# -*- coding: utf-8 -*-

# 외부 패키지 연동
from assertpy import assert_that
import time, datetime
import os, re
import pytest
import json
import contextlib  # testloging기록 추가
import io  # testloging기록 추가
import sys
import traceback
import pickle
import chromedriver_autoinstaller
import logging
import getpass
from sys import platform
from screeninfo import get_monitors
from applitools.selenium import Eyes, Target
from selenium.webdriver import Chrome

import subprocess

# GTAS 연동
from src.gtas_python_core.gtas_python_core_testrail import TestRail
from src.gtas_python_core.gtas_python_core_vault import Vault

# Shared Step 연동
from tests.shared_steps.ss_home import *
from tests.shared_steps.ss_login import *
from tests.shared_steps.ss_srp import *
from tests.shared_steps.ss_myg import *

# PATH List
current_directory = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로를 구함

if platform == "darwin":  # 맥 OS인 경우
    file_path = os.path.join(current_directory, 'file/')
    param_json_path = os.path.abspath(os.path.join(current_directory, '..', 'json', 'home'))  # json/home 폴더에 접근
    root_path = os.path.dirname(current_directory).replace('/tests/screen', '')
    param_root_path = os.path.dirname(current_directory).replace('/tests/screen', '')
    chrome_version = ''
    run_file_name = os.path.basename(__file__)

    # JSON 파일 경로를 안전하게 결합
    current_json = os.path.join(param_json_path, os.path.splitext(run_file_name)[0] + '.json')

    current_case = int(re.findall(r'\d+', run_file_name)[0])
    img_path = os.path.join(current_directory, 'img/')
    img_path_keypad = os.path.join(current_directory, 'img/security_keypad/Mac/1728_1117/')
    screenshot_path = os.path.join("/Users", getpass.getuser(), "webdriver/")

else:  # 윈도우인 경우
    file_path = os.path.join(current_directory, 'file/')
    img_path = os.path.join(current_directory, 'img/')
    img_path_keypad = os.path.join(current_directory, 'img/security_keypad/Windows/1920_1080/')
    param_json_path = os.path.abspath(os.path.join(current_directory, '..', 'json', 'home'))  # json/home 폴더에 접근
    root_path = os.path.dirname(current_directory).replace('\\tests\\screen', '')
    param_root_path = os.path.dirname(current_directory).replace('\\tests\\screen', '')
    chrome_version = ''
    run_file_name = os.path.basename(__file__)

    # JSON 파일 경로를 안전하게 결합
    current_json = os.path.join(param_json_path, os.path.splitext(run_file_name)[0] + '.json')

    current_case = int(re.findall(r'\d+', run_file_name)[0])
    screenshot_path = os.path.join("c:\\webdriver\\")
# 로깅 설정
logging.basicConfig(filename='example.log', level=logging.NOTSET,
                    format='%(asctime)s %(levelname)s %(message)s')


# 재시도 함수
def retry_on_failure(func, *args, driver="", test_rail="", token="", tr_no="", use_type=2, start="",
                     output_content=None, reruns=1, reruns_delay=2, **kwargs):
    # output_content가 None이면, 새 StringIO 객체를 초기화
    if output_content is None:
        output_content = io.StringIO()
    
    run_count = 1
    for i in range(reruns + 1):
        try:
            # func 호출 시 **kwargs를 전달
            func(*args, **kwargs)  # **kwargs로 추가된 인자들을 전달
            if tr_no:  # TestRail에 성공 결과 기록
                test_rail.add_result(
                    status=1,  # 1은 Passed 상태를 의미
                    case_id=int(tr_no),
                    version=chrome_version,
                    comment='Test passed',
                    elapsed=str(int(time.time()) - start) + 's',
                    file_name=token
                )
            # 로그 기록이 성공했을 때, StringIO를 초기화
            output_content.truncate(0)
            output_content.seek(0)
            return True
        except Exception as e:
            if i < reruns:
                time.sleep(reruns_delay)
                print(f"케이스가 실패하여 재시도 합니다. 실행 횟수: {run_count + i}/{reruns}")
                print(f"오류 내용: {e}")
            else:
                print(f"{func.__name__} failed with error: {str(e)}")
                if tr_no:  # 실패한 경우 TestRail에 실패 결과 기록
                    logging.exception("Exception occurred")
                    driver.save_screenshot(screenshot_path + "screenshot.png")
                    output_content.write(traceback.format_exc() + "\n\n")
                    input_data = "실행 내용:\n"
                    input_data += output_content.getvalue() + "\n\n"
                    input_data += traceback.format_exc()
                    test_rail.add_result(
                        status=5,  # 5는 Failed 상태를 의미
                        case_id=int(tr_no),
                        version=chrome_version,
                        comment=input_data,
                        elapsed=str(int(time.time()) - start) + 's',
                        file_name=token
                    )
                    print(input_data)
                return False


# 재시도 함수
def retry_on_failure_precondition(func, *args, reruns=2, reruns_delay=2):
    run_count = 1
    for i in range(reruns + 1):
        try:
            func(*args)
            return True
        except Exception as e:
            if i < reruns:
                time.sleep(reruns_delay)
                print("케이스가 실패하여 재시도 합니다. 실행 횟수: " + str(run_count + i) + "/" + str(reruns))
                print("오류 내용 :", e)
            else:
                print(f"{func.__name__} failed with error: {str(e)}")
                raise ()


# @pytest.mark.flaky(reruns=3, reruns_delay=2) # 실패 시 최대 3번까지 실행하며, 실패시 마다 2초의 대기 딜레이 있음
def test_382265(driver, config, token):
    global chrome_version
    
    # StringIO 객체를 사용
    output_content = io.StringIO()  # testloging 기록 변수에 저장
    
    # 여러 JSON 파일을 불러오기
    json_files = ['/test_382265.json']
    json_data_list = []  # 모든 JSON 데이터를 저장할 리스트
    
    # 각 JSON 파일을 순차적으로 읽어서 json_data_list에 추가
    for json_file in json_files:
        current_json = param_json_path + json_file
        try:
            with open(current_json, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                # JSON이 리스트로 시작하는지 확인하고, 맞춤 처리
                if isinstance(json_data, list):
                    json_data_list.append(json_data[0])  # 리스트라면 첫 번째 요소 추가
                else:
                    json_data_list.append(json_data)  # 객체라면 그대로 추가
        except FileNotFoundError as e:
            print(f"JSON 파일을 찾을 수 없습니다: {e}")
            raise
        except KeyError as e:
            print(f"JSON 데이터에 접근할 수 없습니다: {e}")
            raise
    
    # 필요한 PageObject 및 공통 모듈 불러오기
    from src.gmarket_regression_common.gmarket_regression_common_page_param import CommonPageParam
    from src.gmkt_login_python_dweb_page.login.gmkt_log_in_page_param import GmktLogInPageParam
    from src.gmkt_home_python_dweb_page.gmkt_home_page import GmktHomePageParam
    from src.gmkt_lp_python_dweb_page.lp.gmkt_lp_page_param import GmktLpPageParam
    from src.gmkt_srp_python_dweb_page.srp.gmkt_srp_page_param import GmktSrpPageParam
    from src.gmkt_myg_python_dweb_page.gmkt_myg_page_param import GmktMygPageParam
    from src.gmkt_vip_python_dweb_page.vip.gmkt_vip_in_page_param import GmktVipPageParam
    from src.gtas_python_core.gtas_python_core_testrail import TestRail
    from src.gtas_python_core.gtas_python_core_vault import Vault
    
    try:  # Try Catch 문을 사용하여, 테스트 성공 유무 판단 (TestRail 결과 체크용)
        
        # 시작 시간 측정 및 크롬 버전 확인
        start = int(time.time())
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        
        # 테스트 케이스 변수 정의
        # gmkt_log_in_page_param = GmktLogInPageParam(driver)
        common_page_param = CommonPageParam(driver)
        login_page_param = GmktLogInPageParam(driver)
        home_page_param = GmktHomePageParam(driver)
        lp_page_param = GmktLpPageParam(driver)
        srp_page_param = GmktSrpPageParam(driver)
        myg_page_param = GmktMygPageParam(driver)
        vip_page_param = GmktVipPageParam(driver)
        # setting_page_param = SettingPageParam(driver,config)
        test_rail = TestRail(config)
        
        ##################################### 테스트 케이스 작성 시작 영역 #####################################
        #################################################################################################
        #################################################################################################
        
        # with contextlib.redirect_stdout(output_content):  # testloging 기록
        
        # Preconditions
        # home step - 홈 페이지 UI 확인 (json_data_list[2]는 test_home.json 파일의 데이터)
        if not retry_on_failure(ss_1053, json_data_list[0], home_page_param, driver=driver, test_rail=test_rail,
                                start=start, token=token, output_content=output_content,
                                tr_no=json_data_list[0]['ss_home']['ss_1053']['tr_no'],
                                use_type=json_data_list[0]['ss_home']['ss_1053']['use_type']):
            pytest.fail("ss_1053 failed after retries")
        
        ##################################### 테스트 케이스 작성 끝 영역 #####################################
        ################################################################################################
        ################################################################################################
    
    except Exception as e:  # 테스트 실패 시 Exception 발생
        raise


