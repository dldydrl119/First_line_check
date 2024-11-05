
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def ss_1069(cart_page):
    """
    장바구니 로드 및 상품 확인 테스트
    :param json_data: 테스트에 사용될 JSON 데이터
    :param cart_page: GmktCartPage 인스턴스
    """
  
    # 장바구니 탭 확인
    cart_page.check_cart_tab()  # 장바구니 탭 확인
    cart_page.check_tab_title_count()  # 장바구니 탭에 담긴 수 확인
    cart_page.check_cart_body()  # 장바구니 상세 확인
    # 장바구니 기능 확인 (전체 선택, 수량 선택, 쿠폰 확인, 가격 확인, 결제 정보)
    cart_page.click_select_all()  # 전체 선택 기능 확인
    # cart_page.check_item_qty_wrap()  # 수량 선택 확인
    # cart_page.check_item_coupon()  # 쿠폰 적용 확인
    # cart_page.check_item_price()  # 가격 확인
    # cart_page.check_cart_order()  # 결제정보 창 확인

