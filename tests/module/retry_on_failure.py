# retry_on_failure.py
import time
import traceback
import io
import pytest


def retry_on_failure(func, *args, driver="", test_rail="", token="", tr_no="", start=None, output_content=None,
                     reruns=1, reruns_delay=2, screenshot_list=None, index=0, **kwargs):
    if output_content is None:
        output_content = io.StringIO()
    if index is None:
        index = 0
    
    for i in range(reruns + 1):
        try:
            # 테스트 함수 실행
            func(*args, **kwargs)
            
            # 성공 시 TestRail에 결과 기록
            if tr_no is not None:
                elapsed_time = int(time.time()) - (start or 0)
                minutes, seconds = divmod(elapsed_time, 60)
                hours, minutes = divmod(minutes, 60)
                elapsed_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                
                # 배열 인덱스 정확히 기록
                test_rail.add_result(
                    status=1,
                    case_id=int(tr_no),
                    version=kwargs.get('chrome_version', ''),
                    comment=f'{index + 1}번째 배열 성공',
                    elapsed=elapsed_str,
                    file_name=token
                )
            return True
        except Exception as e:
            if i < reruns:
                time.sleep(reruns_delay)
                print(f"케이스가 실패하여 재시도 합니다. 실행 횟수: {i + 1}/{reruns}")
            else:
                print(f"{func.__name__} failed with error: {str(e)}")
                output_content.write(traceback.format_exc() + "\n\n")
                input_data = "실행 내용:\n" + output_content.getvalue() + "\n\n" + traceback.format_exc()
                
                elapsed_str = locals().get('elapsed_str', '0s')
                
                # 실패 결과 기록
                test_rail.add_result(
                    status=5,
                    case_id=int(tr_no),
                    version=kwargs.get('chrome_version', ''),
                    comment=f'{index + 1}번째 배열 실패\n에러 내용: {input_data}',
                    elapsed=elapsed_str,
                    file_name=token
                )
                return False
