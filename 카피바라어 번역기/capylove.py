import random
import tkinter as tk
from tkinter import scrolledtext

# 글을 2진수로 변환
def text_to_binary(text):
    binary_result = ''
    for char in text:
        binary_result += format(ord(char), '08b')
    return binary_result

# 2진수를 카피바라어로 변환
def binary_to_capybara(binary):
    capybara_result = ''
    for bit in binary:
        if bit == '1':
            capybara_result += random.choice(['카', '피'])  # '1'을 카 또는 피로 변환
        else:
            capybara_result += random.choice(['바', '라'])  # '0'을 바 또는 라로 변환
    return capybara_result

# 버튼 클릭 시 실행될 함수
def on_convert():
    input_text = entry.get()  # 입력 받은 텍스트
    if input_text:
        # 2진수 변환
        binary = text_to_binary(input_text)
        # 카피바라어로 변환
        capybara_text = binary_to_capybara(binary)
        
        # 결과 출력
        result_text.config(state=tk.NORMAL)  # 출력 필드를 편집 가능하게 설정
        result_text.delete(1.0, tk.END)  # 기존 내용 삭제
        result_text.insert(tk.END, capybara_text)  # 카피바라어로 변환된 텍스트 삽입
        result_text.config(state=tk.DISABLED)  # 출력 필드를 편집 불가능하게 설정

# tkinter 윈도우 설정
window = tk.Tk()
window.title("카피바라어 번역기")
window.geometry("400x400")

# 텍스트 입력 라벨
label = tk.Label(window, text="입력 텍스트:")
label.pack(pady=10)

# 텍스트 입력 필드
entry = tk.Entry(window, width=40)
entry.pack(pady=10)

# 변환 버튼
convert_button = tk.Button(window, text="변환", command=on_convert)
convert_button.pack(pady=10)

# 출력 필드 (스크롤 가능)
result_label = tk.Label(window, text="카피바라어 번역 결과:")
result_label.pack(pady=10)

result_text = scrolledtext.ScrolledText(window, width=40, height=10, wrap=tk.WORD, state=tk.DISABLED)
result_text.pack(pady=10)

# tkinter 윈도우 실행
window.mainloop()
