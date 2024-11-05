from assertpy import assert_that
import pytest

def ss_1061(myg_page_param):
    myg_page_param.navigate_to_main_page()  # MyG 페이지로 이동
    myg_page_param.verify_my_gmarket()  # 나의 G 마켓 확인
def ss_1063(myg_page_param):
    
    myg_page_param.navigate_to_main_page()  # MyG 페이지로 이동
    myg_page_param.check_recent_order_box()  # 최근 주문내역 박스 확인
    myg_page_param.check_recent_item_box()  # 최근 본 상품 박스 확인
    ###### Gmarket 운영 페이지에서 제거된 부분 ######
    # myg_page_param.click_recent_item_slide(1)  # 첫 번째 슬라이드 클릭
    # myg_page_param.add_to_cart()  # 장바구니 담기
    # myg_page_param.check_cart_alert()  # 장바구니에 상품이 담겼는지 알림 확인
    # myg_page_param.close_cart_alert()  # 장바구니 알림 창 닫기
    # myg_page_param.select_vip_option()  # VIP 옵션 선택
    # myg_page_param.back_to_previous_page()  # 뒤로 가기
    #######
    myg_page_param.verify_my_gmarket()  # 나의 G 마켓 확인
    myg_page_param.scroll_to_top()