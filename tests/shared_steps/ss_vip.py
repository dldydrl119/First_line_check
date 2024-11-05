from assertpy import assert_that
import pytest


def ss_1066(vip_page):
    """
    ss_1066 테스트 케이스 실행
    VIP 페이지에서 필요한 요소들을 확인하고, SRP에서 저장된 상품명과 비교하는 함수

    :param json_data: 테스트에 사용될 JSON 데이터
    :param vip_page: GmktVipPageParam 인스턴스
    """
    # VIP 페이지 필수 요소 확인 (헤더, 내비게이션, 썸네일 등)
    vip_page.assert_header_wrap_displayed()  # 헤더 확인
    vip_page.assert_location_navi_displayed()  # 위치 내비게이션 확인
    vip_page.assert_item_topinfo_wrap_displayed()  # 상품 정보 상단 래핑 확인
    vip_page.assert_thumb_gallery_displayed()  # 썸네일 갤러리 확인
    vip_page.assert_item_topinfo_additional_displayed()  # 추가 상품 정보 확인
    vip_page.assert_cpc_togetheritems_displayed()  # 연관 상품 박스 확인
    vip_page.assert_vip_tabwrap_displayed()  # VIP 탭 래핑 확인
    vip_page.assert_vip_cpcarea_displayed()  # VIP CPC 영역 확인
    vip_page.assert_vip_detailoption_wrap_displayed()  # VIP 상세 옵션 래핑 확인

def ss_1067(vip_page):
    """
    ss_1067 테스트 케이스 실행
    VIP 페이지에서 일반 장바구니 담기 기능을 테스트하는 함수
    :param json_data: 테스트에 사용될 JSON 데이터
    :param vip_page: GmktVipPageParam 인스턴스
    """
    # 수량 버튼 클릭 및 확인
    vip_page.click_quantity_button()  # 수량 버튼 클릭
    vip_page.assert_quantity_button_selected()  # 수량 리스트 확인

    # 장바구니 담기 버튼 클릭 및 확인
    vip_page.click_add_to_cart_button()  # 장바구니 담기 버튼 클릭
    # vip_page.assert_cart_popup_displayed()  # 장바구니 팝업 확인

    # 팝업 창 닫기
    # vip_page.click_close_cart_popup()  # 팝업 창 닫기
    # vip_page.assert_cart_popup_closed()  # 팝업 창이 닫혔는지 확인