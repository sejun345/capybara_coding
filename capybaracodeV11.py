import sys
import re
import random
import os
import webbrowser
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QEventLoop, QTimer

# 1. 시각적 가독성이 극대화된 팝업창
class CapyPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🦦 카피바라 실행기")
        self.setFixedSize(450, 600)
        self.layout = QVBoxLayout(self)
        
        self.msg_label = QLabel("시스템 대기 중...")
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

# 2. 모든 문법을 지원하는 메인 에디터 및 엔진
class CapybaraEditor(QMainWindow):
    def __init__(self, start_path=None):
        super().__init__()
        self.vars = {"현재시간": "", "__last__": "0"}
        self.lists = {}
        self.popup = None
        self.initUI()
        # 파일 경로가 인자로 넘어왔을 경우 자동으로 불러오기
        if start_path and os.path.isfile(start_path):
            self.load_specific_file(start_path)

    def initUI(self):
        self.setWindowTitle("🦦 Capybara Ultimate v11 (Full Support)")
        self.setGeometry(100, 100, 1100, 850)
        self.setStyleSheet("QMainWindow { background-color: #3e2723; }")
        
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { background-color: #5d4037; color: white; } QMenuBar::item:selected { background-color: #ffd54f; color: black; }")
        file_menu = menubar.addMenu("파일(&F)")
        load_act = QAction("불러오기 (.capy)", self); load_act.triggered.connect(self.load_file)
        save_act = QAction("저장하기 (.capy)", self); save_act.triggered.connect(self.save_file)
        file_menu.addActions([load_act, save_act])

        central = QWidget(); self.setCentralWidget(central); layout = QVBoxLayout(central)
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 14))
        self.editor.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; border-radius: 12px; padding: 15px;")
        
        self.run_btn = QPushButton("🔥 코드 실행 / AI 호출 (RUN)"); self.run_btn.setFixedHeight(65)
        self.run_btn.setStyleSheet("background-color: #ffd54f; color: #3e2723; font-size: 18pt; font-weight: bold; border-radius: 15px;")
        self.run_btn.clicked.connect(self.run_process)
        
        self.console = QTextEdit(); self.console.setReadOnly(True); self.console.setFixedHeight(180)
        self.console.setStyleSheet("background: black; color: #64ffda; font-family: 'Consolas'; border-radius: 10px;")
        
        layout.addWidget(QLabel("<font color='white'><b>카피바라 에디터</b></font>"))
        layout.addWidget(self.editor); layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("<font color='white'><b>시스템 로그</b></font>"))
        layout.addWidget(self.console)

    def log(self, text):
        self.console.append(f"🦦 > {text}"); QApplication.processEvents()

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "코드 저장", "", "Capybara Files (*.capy)")
        if path:
            with open(path, 'w', encoding='utf-8') as f: f.write(self.editor.toPlainText())
            self.log(f"파일 저장 완료: {path}")

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "코드 불러오기", "", "Capybara Files (*.capy)")
        if path: self.load_specific_file(path)

    def load_specific_file(self, path):
        with open(path, 'r', encoding='utf-8') as f: self.editor.setPlainText(f.read())
        self.log(f"파일 로드 완료: {path}")

    def call_local_gemini(self, prompt):
        self.log("AI가 카피바라 코드를 생성 중이다바라...")
        manual = ("너는 카피바라 언어 전문가다. <카피바라~>와 <카피바라!>로만 답해라. "
                  "문법: 디자인바라~, 제목바라~, 투명바라~, 말해바라~, 보여바라~, 적어바라~, 반복바라~, 기다려바라~, "
                  "변수바라~, 계산바라~, 랜덤바라~, 목록바라~, 넣어바라~, 골라바라~, 섞어바라~, 길이바라~, "
                  "저장바라~, 열어바라~, 시간바라~, 날짜바라~, 명령바라~, 청소바라~, 꺼져바라~"
                  f"\n요청: {prompt}")
        try:
            res = subprocess.check_output(["gemini", manual], shell=True, text=True, encoding='utf-8')
            return res.strip()
        except: return '<카피바라~>\n말해바라~ "로컬 AI 호출 실패!"\n<카피바라!>'

    def run_process(self):
        text = self.editor.toPlainText().strip()
        if not text.startswith("<카피바라~>"): text = self.call_local_gemini(text)
        self.vars = {"현재시간": datetime.now().strftime("%H:%M:%S"), "__last__": "0"}; self.lists = {}
        if self.popup: self.popup.close()
        self.console.clear()
        match = re.search(r'(<카피바라~>.*<카피바라!>)', text, re.DOTALL)
        if match: self.execute_engine(match.group(1)[7:-7].strip().split('\n'))

    def execute_engine(self, lines):
        idx = 0
        while idx < len(lines):
            line = lines[idx].strip()
            if not line or line.startswith("#"): idx += 1; continue
            line = re.sub(r'\{([^}]+)\}', lambda m: str(self.vars.get(m.group(1), self.lists.get(m.group(1), "없음"))), line)
            
            try:
                if "디자인바라~" in line:
                    self.popup = CapyPopup(self); m = re.search(r'"([^"]*)"', line); style = m.group(1) if m else ""
                    bg = re.search(r'배경:\s*([^;]+)', style).group(1) if "배경:" in style else "#fff"
                    fg = re.search(r'글자:\s*([^;]+)', style).group(1) if "글자:" in style else "#333"
                    self.popup.set_design(bg, fg); self.popup.show()
                elif "제목바라~" in line:
                    if self.popup: self.popup.setWindowTitle(re.search(r'"([^"]*)"', line).group(1))
                elif "투명바라~" in line:
                    if self.popup: self.popup.setWindowOpacity(float(re.search(r'"([^"]*)"', line).group(1))/100)
                elif "말해바라~" in line or "보여바라~" in line:
                    m = re.search(r'"([^"]*)"', line); msg = m.group(1) if m else ""
                    self.log(f"출력: {msg}")
                    if self.popup and self.popup.isVisible():
                        self.popup.msg_label.setText(msg); loop = QEventLoop(); QTimer.singleShot(1300, loop.quit); loop.exec()
                    else: QMessageBox.information(self, "카피바라", msg)
                elif "적어바라~" in line:
                    m = re.search(r'"([^"]*)"', line); msg = m.group(1) if m else ""
                    if self.popup and self.popup.isVisible():
                        self.popup.msg_label.setText(msg); self.popup.input_field.show(); self.popup.confirm_btn.show()
                        self.popup.user_input = None; loop = QEventLoop()
                        con = self.popup.confirm_btn.clicked.connect(loop.quit); loop.exec()
                        self.popup.confirm_btn.clicked.disconnect(con); self.vars['__last__'] = self.popup.user_input
                    else:
                        val, ok = QInputDialog.getText(self, '입력', msg)
                        if ok: self.vars['__last__'] = val
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
                elif "목록바라~" in line: self.lists[re.search(r'"([^"]*)"', line).group(1)] = []
                elif "넣어바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.lists[m.group(1)].append(m.group(2))
                elif "섞어바라~" in line: random.shuffle(self.lists[re.search(r'"([^"]*)"', line).group(1)])
                elif "골라바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.vars[m.group(2)] = random.choice(self.lists[m.group(1)])
                elif "길이바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line); self.vars[m.group(2)] = len(self.lists[m.group(1)])
                elif "저장바라~" in line:
                    m = re.search(r'"([^,]+),\s*([^"]+)"', line)
                    with open(m.group(1).strip(), "w", encoding="utf-8") as f: f.write(m.group(2).strip())
                elif "시간바라~" in line: self.vars['현재시간'] = datetime.now().strftime("%H:%M:%S"); self.vars['__last__'] = self.vars['현재시간']
                elif "날짜바라~" in line: self.vars['현재날짜'] = datetime.now().strftime("%Y-%m-%d"); self.vars['__last__'] = self.vars['현재날짜']
                elif "열어바라~" in line: webbrowser.open(re.search(r'"([^"]*)"', line).group(1))
                elif "명령바라~" in line: os.system(re.search(r'"([^"]*)"', line).group(1))
                elif "청소바라~" in line: self.console.clear()
                elif "꺼져바라~" in line: sys.exit()
            except Exception as e: self.log(f"에러: {str(e)}")
            idx += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 인자로 받은 파일이 있으면 에디터에 로드
    path = sys.argv[1] if len(sys.argv) > 1 else None
    ex = CapybaraEditor(path); ex.show(); sys.exit(app.exec())