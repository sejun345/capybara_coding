import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


class CapybaraInterpreter:
    def __init__(self):
        self.variables = {}  # 변수 저장용 딕셔너리
        self.storage_path = os.path.join(os.path.expanduser("~"), "Documents", "카피바라 저장소")
        os.makedirs(self.storage_path, exist_ok=True)  # 저장 폴더 생성

    def execute(self, code):
        # 코드가 "카피바라~"로 시작하고 "카피바라!"로 끝나는지 확인
        if not code.startswith("<카피바라~>") or not code.endswith("<카피바라!>"):
            raise SyntaxError("코드는 <카피바라~>로 시작하고 <카피바라!>로 끝나야 합니다!")

        # 코드 내용 추출
        code_body = code[len("<카피바라~>"):-len("<카피바라!>")].strip()

        # 줄 단위로 명령어 처리
        for line in code_body.split("\n"):
            line = line.strip()
            if not line:  # 빈 줄 무시
                continue
            self.process_line(line)

    def process_line(self, line):
        # "물어바라~" 출력 명령
        if "물어바라~" in line:
            expression = re.search(r'\((.*?)\)', line)  # 괄호 안 숫자 계산
            if expression:
                result = self.safe_eval(expression.group(1))
                print(result)
            else:
                raise SyntaxError("물어바라~에는 괄호로 감싼 표현식이 필요합니다!")

        # "적어바라~" 입력 명령
        elif "적어바라~" in line:
            var_match = re.search(r'적어바라~\s*(\w+)\s*\(.*?\)', line)
            if var_match:
                var_name = var_match.group(1)
                input_prompt = re.search(r'".*?"', line).group(0).strip('"')
                user_input = input(f"{input_prompt}: ")
                self.variables[var_name] = int(user_input)  # 입력 값을 정수로 저장
            else:
                raise SyntaxError("적어바라~에는 변수 이름과 입력 안내가 필요합니다!")

        # "저장바라~" 명령
        elif "저장바라~" in line:
            var_match = re.search(r'저장바라~\s*(\w+)\((.*?)\)', line)
            if var_match:
                filename = var_match.group(1) + ".capybara"
                content = var_match.group(2)
                file_path = os.path.join(self.storage_path, filename)
                self.save_file(file_path, content)
            else:
                raise SyntaxError("저장바라~ 명령에는 파일 이름과 내용이 필요합니다!")

    def safe_eval(self, expression):
        # 안전하게 계산하기 위한 제한된 eval() 함수
        try:
            return eval(expression, {"__builtins__": None}, self.variables)
        except Exception as e:
            raise SyntaxError(f"계산 오류: {str(e)}")

    def save_file(self, file_path, content):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"{file_path}에 저장되었습니다.")

    def load_file(self, filename):
        # 파일에서 카피바라 코드를 읽어옴
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"{filename} 파일을 찾을 수 없습니다.")


class CapybaraEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("카피바라 코드 편집기")
        self.text_area = tk.Text(self.root, wrap="word", font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True)

        self.create_menu()
        self.filename = None  # 현재 열려 있는 파일

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # 파일 메뉴
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="열기", command=self.open_file)
        file_menu.add_command(label="저장", command=self.save_file)
        file_menu.add_command(label="다른 이름으로 저장", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        menu_bar.add_cascade(label="파일", menu=file_menu)

        # 실행 메뉴
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="실행", command=self.run_code)
        menu_bar.add_cascade(label="실행", menu=run_menu)

        self.root.config(menu=menu_bar)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Capybara Files", "*.capybara")])
        if file_path:
            self.filename = file_path
            with open(file_path, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())

    def save_file(self):
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END).strip())
            messagebox.showinfo("저장 성공", f"{self.filename} 파일이 저장되었습니다.")
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".capybara",
                                                 filetypes=[("Capybara Files", "*.capybara")])
        if file_path:
            self.filename = file_path
            self.save_file()

    def run_code(self):
        code = self.text_area.get(1.0, tk.END).strip()
        try:
            interpreter = CapybaraInterpreter()
            interpreter.execute(code)
        except Exception as e:
            messagebox.showerror("실행 오류", str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    editor = CapybaraEditor()
    editor.run()
