from assertpy import assert_that
import pytest

def ss_1063(test_data, srp_page):
    """
    ss_1063 테스트 케이스 실행 (검색 결과 검증)

    :param test_data: 검색 결과를 검증할 전체 데이터 (예: ss_1063 데이터)
    :param srp_page: GmktSrpPage 인스턴스
    """
    expected_search_result = test_data['assert']['value1']  # 기대하는 검색어

    # 검색 결과에 기대하는 검색어가 포함되어 있는지 확인
    srp_page.assert_search_result_contains_keyword(expected_search_result)
    srp_page.click_first_product_in_list()  # 첫 번째 상품 클릭
    srp_page.assert_vip_page_loaded()  # VIP 페이지 로드 확인
    srp_page.go_back_to_search_result_page(expected_search_result)  # 뒤로가기 후 검색 결과 페이지로 돌아오기
