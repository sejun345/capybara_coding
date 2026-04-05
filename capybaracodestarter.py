import sys
import re
import random
import os
import webbrowser
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QEventLoop, QTimer

# 1. 에디터와 동일한 시각적 팝업창
class CapyPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦦 카피바라 실행기")
        self.setFixedSize(450, 600)
        self.layout = QVBoxLayout(self)
        
        self.msg_label = QLabel("로딩 중...")
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setFont(QFont("Malgun Gothic", 20, QFont.Weight.Bold))
        
        self.input_field = QLineEdit()
        self.input_field.setFixedHeight(55)
        self.input_field.setFont(QFont("Malgun Gothic", 15))
        self.input_field.setStyleSheet("border: 3px solid #5d4037; border-radius: 10px; padding: 5px;")
        self.input_field.hide()
        
        self.confirm_btn = QPushButton("확인바라~")
        self.confirm_btn.setFixedHeight(85)
        self.confirm_btn.setFont(QFont("Malgun Gothic", 22, QFont.Weight.ExtraBold))
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.hide()
        
        self.layout.addStretch()
        self.layout.addWidget(self.msg_label)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.input_field)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.confirm_btn)
        self.layout.addStretch()
        
        self.user_input = None
        self.confirm_btn.clicked.connect(self.on_confirm)

    def on_confirm(self):
        self.user_input = self.input_field.text()
        self.input_field.hide()
        self.confirm_btn.hide()

    def set_design(self, bg, fg):
        btn_bg = fg if fg != "transparent" else "#3e2723"
        btn_fg = bg if bg != "transparent" else "white"
        self.setStyleSheet(f"""
            QDialog {{ background: {bg}; border: 6px solid #5d4037; border-radius: 35px; }}
            QLabel {{ color: {fg}; background: transparent; }}
            QPushButton {{ background-color: {btn_bg}; color: {btn_fg}; border-radius: 20px; border: 4px solid #2d1b18; }}
            QPushButton:hover {{ background-color: #ffd54f; color: #3e2723; }}
        """)

# 2. 에디터 엔진(v9.3)과 100% 호환되는 실행기 클래스
class CapyLauncher(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.vars = {"현재시간": datetime.now().strftime("%H:%M:%S"), "__last__": "0"}
        self.lists = {}
        self.popup = None
        
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # <카피바라~> 태그 추출
                    match = re.search(r'(<카피바라~>.*<카피바라!>)', content, re.DOTALL)
                    if match:
                        code_lines = match.group(1)[7:-7].strip().split('\n')
                        self.execute_engine(code_lines)
            except Exception as e:
                print(f"실행 오류: {e}")
        
        # 모든 코드가 끝나면 종료
        sys.exit()

    def execute_engine(self, lines):
        idx = 0
        while idx < len(lines):
            line = lines[idx].strip()
            if not line or line.startswith("#"): idx += 1; continue
            
            # 변수 치환 로직
            line = re.sub(r'\{([^}]+)\}', lambda m: str(self.vars.get(m.group(1), self.lists.get(m.group(1), "없음"))), line)
            
            try:
                # [GUI 제어]
                if "디자인바라~" in line:
                    self.popup = CapyPopup()
                    m = re.search(r'"([^"]*)"', line); style = m.group(1) if m else ""
                    bg = re.search(r'배경:\s*([^;]+)', style).group(1) if "배경:" in style else "#fff"
                    fg = re.search(r'글자:\s*([^;]+)', style).group(1) if "글자:" in style else "#333"
                    self.popup.set_design(bg, fg); self.popup.show()
                elif "제목바라~" in line:
                    if self.popup: self.popup.setWindowTitle(re.search(r'"([^"]*)"', line).group(1))
                elif "투명바라~" in line:
                    if self.popup: self.popup.setWindowOpacity(float(re.search(r'"([^"]*)"', line).group(1))/100)

                # [입출력]
                elif "말해바라~" in line or "보여바라~" in line:
                    msg = re.search(r'"([^"]*)"', line).group(1)
                    if self.popup and self.popup.isVisible():
                        self.popup.msg_label.setText(msg); loop = QEventLoop(); QTimer.singleShot(1300, loop.quit); loop.exec()
                    else: QMessageBox.information(None, "카피바라", msg)
                elif "적어바라~" in line:
                    msg = re.search(r'"([^"]*)"', line).group(1)
                    if self.popup and self.popup.isVisible():
                        self.popup.msg_label.setText(msg); self.popup.input_field.show(); self.popup.confirm_btn.show()
                        self.popup.user_input = None; loop = QEventLoop()
                        con = self.popup.confirm_btn.clicked.connect(loop.quit); loop.exec()
                        self.popup.confirm_btn.clicked.disconnect(con); self.vars['__last__'] = self.popup.user_input
                    else:
                        val, ok = QInputDialog.getText(None, '입력', msg)
                        if ok: self.vars['__last__'] = val

                # [제어문/변수/수학]
                elif "반복바라~" in line:
                    c = int(re.search(r'"(\d+)"', line).group(1)); body = []; idx += 1
                    while idx < len(lines) and "끝바라!" not in lines[idx]: body.append(lines[idx]); idx += 1
                    for _ in range(c): self.execute_engine(body)
                elif "기다려바라~" in line:
                    t = float(re.search(r'"([\d\.]+)"', line).group(1)); loop = QEventLoop(); QTimer.singleShot(int(t*1000), loop.quit); loop.exec()
                elif "변수바라~" in line: self.vars[re.search(r'"([^"]*)"', line).group(1)] = self.vars.get('__last__', "0")
                elif "계산바라~" in line:
                    expr = re.search(r'"([^"]*)"', line).group(1); f, v = expr.split('='); self.vars[v.strip()] = eval(f)
                elif "랜덤바라~" in line:
                    m = re.search(r'"(\d+),\s*(\d+),\s*([^"]+)"', line); self.vars[m.group(3)] = random.randint(int(m.group(1)), int(m.group(2)))

                # [리스트]
                elif "목록바라~" in line: self.lists[re.search(r'"([^"]*)"', line).group(1)] = []
                elif "넣어바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.lists[m.group(1).strip()].append(m.group(2).strip())
                elif "섞어바라~" in line: random.shuffle(self.lists[re.search(r'"([^"]*)"', line).group(1)])
                elif "골라바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.vars[m.group(2).strip()] = random.choice(self.lists[m.group(1).strip()])
                elif "길이바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.vars[m.group(2).strip()] = len(self.lists[m.group(1).strip()])

                # [시스템/파일]
                elif "저장바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line)
                    with open(m.group(1).strip(), "w", encoding="utf-8") as f: f.write(m.group(2).strip())
                elif "시간바라~" in line: self.vars['현재시간'] = datetime.now().strftime("%H:%M:%S"); self.vars['__last__'] = self.vars['현재시간']
                elif "날짜바라~" in line: self.vars['현재날짜'] = datetime.now().strftime("%Y-%m-%d"); self.vars['__last__'] = self.vars['현재날짜']
                elif "열어바라~" in line: webbrowser.open(re.search(r'"([^"]*)"', line).group(1))
                elif "명령바라~" in line: os.system(re.search(r'"([^"]*)"', line).group(1))
                elif "꺼져바라~" in line: sys.exit()

            except Exception as e:
                print(f"구문 에러: {e}")
            idx += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        launcher = CapyLauncher(sys.argv[1])
    else:
        # 파일 인자가 없을 경우 안내창
        QMessageBox.warning(None, "카피바라", "실행할 .capy 또는 .capybara 파일을 끌어다 놓으세요.")
    sys.exit()