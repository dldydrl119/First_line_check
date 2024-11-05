from assertpy import assert_that
import pytest


def ss_1053(home_page):
    """
    ss_1053 테스트 케이스 실행

    :param json_data: 테스트에 사용될 JSON 데이터
    :param home_page: GmktHomePageParam 인스턴스
    """

    home_page.move_link()  # Gmarket 메인 페이지로 이동
    home_page.check_and_logout() # 만약 로그인이 되어있다면 로그아웃
    home_page.check_section_main_top()  # 메인 배너
    home_page.check_section_main_banner()  # 메인 띠배너
    home_page.check_section_main_best()  # 제일 잘 나가는 상품
    home_page.check_section_main_market()  # 스마일 서비스
    home_page.check_section_main_service()  # 서비스 섹션
    home_page.check_section_main_homeshopping()  # 홈쇼핑 섹션
    home_page.check_section_main_superdeal()  # 슈퍼딜 섹션
    home_page.check_section_main_overseas()  # 해외직구 섹션
    home_page.check_section_main_notice()  # 안내 섹션
    home_page.check_section_main_fontguide()  # 폰트 가이드 섹션
    home_page.check_url()        # URL 확인
    home_page.check_search_bar() # 검색 바 확인
    

def ss_1065(assert_data, home_page):
    """
    ss_1053 테스트 케이스 실행

    :param json_data: 테스트에 사용될 JSON 데이터
    :param home_page: GmktHomePageParam 인스턴스
    """
    expected_username_param = assert_data.get('user_name', None)  # 기본값 None 설정
    
    home_page.move_link()  # Gmarket 메인 페이지로 이동
    home_page.check_section_main_top()  # 메인 배너
    home_page.check_section_main_banner()  # 메인 띠배너
    home_page.check_section_main_best()  # 제일 잘 나가는 상품
    home_page.check_section_main_market()  # 스마일 서비스
    home_page.check_section_main_service()  # 서비스 섹션
    home_page.check_section_main_homeshopping()  # 홈쇼핑 섹션
    home_page.check_section_main_superdeal()  # 슈퍼딜 섹션
    home_page.check_section_main_overseas()  # 해외직구 섹션
    home_page.check_section_main_notice()  # 안내 섹션
    home_page.check_section_main_fontguide()  # 폰트 가이드 섹션
    home_page.check_url()        # URL 확인
    home_page.check_search_bar() # 검색 바 확인
    home_page.assert_home_username_displayed(expected_username_param)  # 로그인 후 계정명 확인
    