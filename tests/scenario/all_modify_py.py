# -*- coding: utf-8 -*-

import os
import glob

# 대상 디렉토리 경로
current_path= os.path.dirname(__file__)
print(current_path)

# 대상 구문 및 수정 내용
old_text = r"""

""".strip()

new_text = r"""

""".strip()

# 디렉토리 내의 모든 파이썬 파일을 찾음
file_list = glob.glob(os.path.join(current_path, "*.py"))

modified_files = 0

# 각 파일을 순회하며 대상 구문을 수정하고 파일을 저장
for file_path in file_list:
    with open(file_path, "r", encoding='utf-8') as file:  # 여기에 encoding을 추가
        file_data = file.read()

    # 구문 수정
    updated_file_data = file_data.replace(old_text, new_text)

    # 만약 변경이 있었다면 파일에 쓴다.
    if file_data != updated_file_data:
        modified_files += 1
        with open(file_path, "w", encoding='utf-8') as file:  # 여기에도 encoding을 추가
            file.write(updated_file_data)
        print(f"Modified {file_path}")

if modified_files:
    print(f"Modified {modified_files} files.")
else:
    print("No modifications were made.")
