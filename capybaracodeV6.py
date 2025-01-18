import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


class CapybaraInterpreter:
    def __init__(self, display_callback, input_callback):
        self.variables = {}  # 변수 저장용 딕셔너리
        self.storage_path = os.path.join(os.path.expanduser("~"), "Documents", "카피바라 저장소")
        os.makedirs(self.storage_path, exist_ok=True)  # 저장 폴더 생성
        self.display_callback = display_callback  # GUI에 출력을 보내는 콜백 함수
        self.input_callback = input_callback  # GUI에서 입력을 받는 콜백 함수

    def execute(self, code):
        if not code.startswith("<카피바라~>") or not code.endswith("<카피바라!>"):
            raise SyntaxError("코드는 <카피바라~>로 시작하고 <카피바라!>로 끝나야 합니다!")

        code_body = code[len("<카피바라~>"):-len("<카피바라!>")].strip()

        for line in code_body.split("\n"):
            line = line.strip()
            if not line:
                continue
            self.process_line(line)

    def process_line(self, line):
        if "물어바라~" in line:
            expression = re.search(r'"\s*(.*?)\s*"', line)
            if expression:
                self.display_callback(expression.group(1))  # 질문 출력
            else:
                raise SyntaxError("물어바라~에는 문자열이 필요합니다!")

        elif "말해바라~" in line:
            expression = re.search(r'"\s*(.*?)\s*"', line)
            if expression:
                self.display_callback(expression.group(1))  # 말하기 출력
            else:
                raise SyntaxError("말해바라~에는 문자열이 필요합니다!")

        elif "변수바라~" in line:
            var_match = re.search(r'변수바라~\s*(\w+)', line)
            if var_match:
                var_name = var_match.group(1)
                self.variables[var_name] = None  # 변수를 저장하지만 초기값은 None
                self.display_callback(f"변수 {var_name}이 생성되었습니다.")
            else:
                raise SyntaxError("변수바라~에는 변수 이름이 필요합니다!")

        elif "적어바라~" in line:
            var_match = re.search(r'적어바라~\s*(\w+)\s*\(.*?\)', line)
            if var_match:
                var_name = var_match.group(1)
                input_prompt = re.search(r'".*?"', line).group(0).strip('"')
                # GUI에서 입력 받기
                user_input = self.input_callback(input_prompt)
                try:
                    user_input = int(user_input)  # 숫자만 받도록 처리
                    self.variables[var_name] = user_input
                    self.display_callback(f"{var_name} = {self.variables[var_name]}")  # 입력 후 출력
                except ValueError:
                    self.display_callback("잘못된 입력입니다. 숫자만 입력해 주세요.")  # 입력 오류 처리
            else:
                raise SyntaxError("적어바라~에는 변수 이름과 입력 안내가 필요합니다!")

    def save_file(self, file_path, content):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        self.display_callback(f"{file_path}에 저장되었습니다.")

    def load_file(self, filename):
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

        self.output_area = tk.Text(self.root, wrap="word", font=("Consolas", 12), height=10)
        self.output_area.pack(fill="both", expand=True)
        self.output_area.config(state=tk.DISABLED)

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
            interpreter = CapybaraInterpreter(self.display_output, self.get_input)
            interpreter.execute(code)
        except Exception as e:
            messagebox.showerror("실행 오류", str(e))

    def get_input(self, prompt):
        # GUI에서 입력 받기
        input_window = tk.Toplevel(self.root)
        input_window.title("입력")
        input_label = tk.Label(input_window, text=prompt, font=("Arial", 12))
        input_label.pack(padx=10, pady=10)

        input_entry = tk.Entry(input_window, font=("Arial", 12))
        input_entry.pack(padx=10, pady=10)

        # 입력 버튼
        input_button = tk.Button(input_window, text="입력", font=("Arial", 12),
                                  command=lambda: self.on_input_button(input_window, input_entry))
        input_button.pack(padx=10, pady=10)

        input_window.wait_window(input_window)  # 입력창이 닫힐 때까지 대기

        return self.user_input

    def on_input_button(self, input_window, input_entry):
        self.user_input = input_entry.get()  # 입력 값 가져오기
        input_window.destroy()  # 창 닫기

    def display_output(self, output):
        # 출력 영역에 결과를 추가
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, output + "\n")
        self.output_area.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    editor = CapybaraEditor()
    editor.run()
