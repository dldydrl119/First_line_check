# -*- coding: utf-8 -*-

# 외부 패키지 연동
import time, datetime
import os, re
import pytest
import json
import io  # testloging 기록 추가
import traceback
import chromedriver_autoinstaller
import logging
import getpass
from sys import platform
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from urllib.parse import urlparse, parse_qs

# GTAS 연동
from src.gtas_python_core.gtas_python_core_testrail import TestRail
from src.gtas_python_core.gtas_python_core_vault import Vault

# 모듈폴더의 모듈 불러오기
from tests.module.utils.load_json_data import load_json_data
from tests.module.retry_on_failure import retry_on_failure

# Shared Step 연동
from tests.shared_steps.ss_home import *
from tests.shared_steps.ss_login import *
from tests.shared_steps.ss_srp import *
from tests.shared_steps.ss_vip import *
from tests.shared_steps.ss_cart import *

# 경로 설정
current_directory = os.path.dirname(os.path.abspath(__file__))
if platform == "darwin":  # 맥 OS인 경우
    file_path = os.path.join(current_directory, 'file/')
    param_json_path = os.path.join(current_directory, 'json/')
    root_path = os.path.dirname(current_directory).replace('/tests/scenario', '')
    screenshot_path = os.path.join("/Users", getpass.getuser(), "webdriver/")
else:  # 윈도우인 경우
    file_path = os.path.join(current_directory, 'file\\')
    param_json_path = os.path.join(current_directory, 'json\\')
    root_path = os.path.dirname(current_directory).replace('\\tests\\scenario', '')
    screenshot_path = "c:\\webdriver\\"

# 로깅 설정
logging.basicConfig(filename='example.log', level=logging.NOTSET,
                    format='%(asctime)s %(levelname)s %(message)s')

# 시나리오 테스트 실행 함수
def run_scenario_test_case(driver, config, token, scenario_json_list):
    output_content = io.StringIO()
    chrome_version = chromedriver_autoinstaller.get_chrome_version()

    from src.gmkt_login_python_dweb_page.login.gmkt_log_in import GmktLogInPage
    from src.gmkt_home_python_dweb_page.gmkt_home import GmktHomePage
    from src.gmkt_srp_python_dweb_page.srp.gmkt_srp import GmktSrpPage
    from src.gmkt_vip_python_dweb_page.vip.gmkt_vip import GmktVipPage
    from src.gmkt_cart_python_dweb_page.cart.gmkt_cart import GmktCartPage

    try:
        driver.set_page_load_timeout(20)
        start = int(time.time())

        # 페이지 객체 생성
        login_page = GmktLogInPage(driver)
        home_page = GmktHomePage(driver)
        srp_page = GmktSrpPage(driver)
        vip_page = GmktVipPage(driver, srp_page)
        cart_page = GmktCartPage(driver)
        test_rail = TestRail(config)
        results = []

        # 테스트 반복 시작
        for index, scenario in enumerate(scenario_json_list):
            tr_no = scenario["test_info"]["tr_no"]

            try:
                # 홈 페이지 테스트
                if not retry_on_failure(ss_1053, home_page, driver=driver, test_rail=test_rail, start=start,
                                        token=token, output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1053 failed after retries in test case {tr_no}")

                # 로그인 테스트
                if not retry_on_failure(ss_1054, scenario["ss_1054"]["input"], scenario["ss_1054"]["assert"],
                                        login_page, driver=driver, test_rail=test_rail, start=start, token=token,
                                        output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1054 failed after retries in test case {tr_no}")

                # 로그인 후 홈
                if not retry_on_failure(ss_1065, scenario["ss_1065"]["assert"], home_page, driver=driver,
                                        test_rail=test_rail, start=start, token=token, output_content=output_content,
                                        tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1065 failed after retries in test case {tr_no}")

                # 검색 테스트
                search_keyword = scenario["ss_1063"]["input"]["value1"]
                search_keyword_assert = scenario["ss_1063"]["assert"]["value1"]
                srp_page.go_to_main_page()
                srp_page.enter_search_keyword(search_keyword)
                srp_page.click_search_button()
                
                # 검색 결과 검증
                if not retry_on_failure(ss_1063, scenario["ss_1063"], srp_page, driver=driver, test_rail=test_rail,
                                        start=start, token=token, output_content=output_content, tr_no=tr_no,
                                        index=index):
                    pytest.fail(f"ss_1063 failed after retries in test case {tr_no}")
                
                # VIP 페이지 이동 및 검증
                srp_page.click_third_item()
                third_item_url = driver.current_url
                parsed_url = urlparse(third_item_url)
                goodsnum = parse_qs(parsed_url.query).get('goodscode', [None])[0]
                item_url = f"https://item.gmarket.co.kr/Item?goodscode={goodsnum}"
                driver.get(item_url)

                if not retry_on_failure(ss_1066, vip_page, driver=driver, test_rail=test_rail, start=start, token=token,
                                        output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1066 failed after retries in test case {tr_no}")

                # 장바구니 담기
                if not retry_on_failure(ss_1067, vip_page, driver=driver, test_rail=test_rail, start=start, token=token,
                                        output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1067 failed after retries in test case {tr_no}")

                # 장바구니 페이지 로드
                cart_page.go_to_cart_page()
                if not retry_on_failure(ss_1069, cart_page, driver=driver, test_rail=test_rail, start=start,
                                        token=token, output_content=output_content, tr_no=tr_no, index=index):
                    pytest.fail(f"ss_1069 failed after retries in test case {tr_no}")

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

        # 최종 결과를 TestRail에 기록
        elapsed_time = int(time.time()) - start
        elapsed_str = f"{elapsed_time}s"

        if all(result == "pass" for result in results):
            overall_comment = "모든 테스트 성공"
        elif all(result == "fail" for result in results):
            overall_comment = "모든 테스트 실패"
        else:
            overall_comment = f"일부분 성공: {results.count('pass')} 패스, {results.count('fail')} 실패"

        test_rail.add_result(
            status=1 if all(result == "pass" for result in results) else 5,
            case_id=int(scenario_json_list[0]["test_info"]["tr_no"]),
            version=chrome_version,
            comment=overall_comment,
            elapsed=elapsed_str,
            file_name=token
        )

    except Exception as e:
        raise


# test_395708 실행 함수
def test_395708(driver, config, token):
    json_files = ['test_395708.json']
    scenario_json_list = load_json_data(param_json_path + json_files[0])

    # 시나리오 테스트 실행
    run_scenario_test_case(driver, config, token, scenario_json_list)
