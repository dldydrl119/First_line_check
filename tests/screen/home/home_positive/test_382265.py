# -*- coding: utf-8 -*-

# 외부 패키지 연동
import time
import os
import pytest
import json
import io
import traceback
import chromedriver_autoinstaller
import logging
import getpass
from sys import platform
from selenium.webdriver import Chrome

# GTAS 연동
from src.gtas_python_core.gtas_python_core_testrail import TestRail

# 모듈폴더의 모듈 불러오기
from tests.module.utils.load_json_data import load_json_data
from tests.module.retry_on_failure import retry_on_failure
# Shared Step 연동
from tests.shared_steps.ss_home import *
from tests.shared_steps.ss_login import *
from tests.shared_steps.ss_srp import *
from tests.shared_steps.ss_vip import *
from tests.shared_steps.ss_cart import *
# 경로 수정
current_directory = os.path.dirname(os.path.abspath(__file__))

if platform == "darwin":  # 맥 OS인 경우
    param_json_path = os.path.abspath(os.path.join(current_directory, '..', '..', 'json', 'home'))
    screenshot_path = os.path.join("/Users", getpass.getuser(), "webdriver/")
else:  # 윈도우인 경우
    param_json_path = os.path.abspath(os.path.join(current_directory, '..', '..', 'json', 'home'))
    screenshot_path = os.path.join("c:\\webdriver\\")

# 로깅 설정
logging.basicConfig(filename='example.log', level=logging.NOTSET,
                    format='%(asctime)s %(levelname)s %(message)s')


# 스크린 테스트 케이스 실행 함수
def run_screen_test_case(driver, config, token, screen_json_list):
    global chrome_version
    
    output_content = io.StringIO()
    
    # 필요한 PageObject 및 공통 모듈 불러오기
    from src.gmkt_home_python_dweb_page.gmkt_home import GmktHomePage
    
    try:
        driver.set_page_load_timeout(20)
        start = int(time.time())
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        
        # 페이지 객체 초기화
        home_page = GmktHomePage(driver)
        test_rail = TestRail(config)
        results = []
        
        # 시나리오를 반복 처리
        for index, screen in enumerate(screen_json_list):
            tr_no = screen["ss_1053"]["test_info"]["tr_no"]
            
            try:
                if not retry_on_failure(ss_1053, home_page,
                                        driver=driver, test_rail=test_rail, start=start, token=token,
                                        output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1053 failed after retries in test case {tr_no}")
                
                # 성공 시
                results.append("pass")
            
            except Exception as e:
                print(f"{index + 1}번째 배열에서 실패했습니다. 에러: {str(e)}")
                
                # 통일된 방식으로 스크린샷 파일 이름 생성
                screenshot_file = f"screenshot_{tr_no}_{index + 1}.png"
                driver.save_screenshot(screenshot_file)
                print(f"스크린샷이 저장되었습니다: {screenshot_file}")
                
                # 실패 시에도 시간을 기록하여 'elapsed_str' 생성
                elapsed_time = int(time.time()) - start
                minutes, seconds = divmod(elapsed_time, 60)
                hours, minutes = divmod(minutes, 60)
                elapsed_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                
                # 실패 결과 기록 (스크린샷 파일 경로를 전달)
                test_rail.add_result(
                    status=5,  # 실패
                    case_id=int(tr_no),
                    version=chrome_version,
                    comment=f'{index + 1}번째 배열에서 실패했습니다.\n에러: {str(e)}\n스크린샷 경로: {screenshot_file}',
                    elapsed=elapsed_str,
                    file_name=token,
                    screenshot_file=screenshot_file  # 스크린샷 파일 경로를 전달
                )
                
                # 실패 시
                results.append("fail")
        # 전체 테스트 결과 요약
        if all(result == "pass" for result in results):
            overall_comment = "모든 테스트 성공"
        elif all(result == "fail" for result in results):
            overall_comment = "모든 테스트 실패"
        else:
            overall_comment = f"일부분 성공 \n{results.count('pass')} 패스\n{results.count('fail')} 실패"
        
        # 최종 결과를 TestRail에 기록
        test_rail.add_result(
            status=1 if all(result == "pass" for result in results) else 5,
            case_id=int(tr_no),
            version=chrome_version,
            comment=f"최종 결과 : {overall_comment}",
            file_name=token
        )
    
    except Exception as e:
        raise


# test_382265 실행 함수
def test_382265(driver, config, token):
    # 시나리오 JSON 파일 불러오기
    screen_json_list = load_json_data(param_json_path + '/test_382265.json')
    
    # 스크린 테스트 실행
    run_screen_test_case(driver, config, token, screen_json_list)
