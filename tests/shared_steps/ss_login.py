from assertpy import assert_that
import pytest


# ss_1054 (로그인 성공 케이스)
# 예시: ss_1054 함수
def ss_1054(input_data, assert_data, login_page, *args, **kwargs):
    # 로그인 로직

    """
    각 회원별 로그인 : 로그인 절차를 JSON 데이터를 바탕으로 단계별로 실행
    """
    id_param = input_data['value1']  # ID
    password_param = input_data['value2']  # 비밀번호
    expected_username_param = assert_data.get('user_name', None)  # 기본값 None 설정
    
    login_page.navigate_to_login_page()  # 로그인 페이지로 이동
    login_page.enter_username(id_param)  # 아이디 입력 및 확인
    login_page.assert_username_entered(id_param)
    login_page.enter_password(password_param)  # 비밀번호 입력 및 확인
    login_page.assert_password_entered(password_param)
    login_page.click_login_button()  # 로그인 버튼 클릭
    # login_page.assert_redirect_to_main_page()
    login_page.assert_username_displayed(expected_username_param)  # 로그인 후 계정명 확인
    # 로그인 후 로그아웃 실행
    # login_page.log_out()
    # login_page.assert_logged_out()  # 로그아웃 성공 확인


def ss_1055(input_data, assert_data, login_page):
    """
    로그인 실패 : 로그인 실패 절차를 전달받은 데이터를 바탕으로 단계별로 실행
    """
    # Parameter
    id_param = input_data['value1']  # ID
    password_param = input_data['value2']  # 비밀번호
    expected_alert = assert_data['alert']  # 예상 경고 메시지
    
    login_page.navigate_to_login_page()  # 로그인 페이지로 이동
    login_page.enter_username(id_param)  # 아이디 입력 및 확인
    login_page.assert_username_entered(id_param)
    
    login_page.enter_password(password_param)  # 비밀번호 입력 및 확인
    login_page.assert_password_entered(password_param)
    
    login_page.click_login_button()  # 로그인 버튼 클릭
    login_page.check_login_failure_message(expected_alert)  # 로그인 실패 메시지 확인