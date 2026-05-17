import tkinter as tk  # 파이썬의 기본 창 만들기 도구함(tkinter)을 불러와서 'tk'라는 별명으로 부릅니다.
from tkinter import colorchooser, messagebox, filedialog  # 색상 선택창과 알림창 기능을 따로 가져옵니다.
import math  # 삼각형이나 별의 좌표를 계산하기 위해 수학 도구함을 가져옵니다.
from PIL import Image, ImageDraw  # [수정] 저장을 위해 Pillow 라이브러리를 가져옵니다.

class PyPaint:
    def __init__(self, root):
        # --- 1. 초기 설정 부분 ---
        self.root = root  # 프로그램의 메인 창을 저장합니다.
        self.root.title("PyPaint - 그림판")  # 창 위쪽의 제목을 정합니다.
        self.root.geometry("1150x800")  # 창의 처음 크기를 가로 1150, 세로 800으로 정합니다.

        # --- 2. 그림판 상태 저장 변수들 ---
        self.color = "#000000"        # 지금 내가 무슨 색 물감을 묻혔는지 (기본 검정)
        self.eraser_color = "#ffffff"  # 지우개는 사실 '흰색 물감'과 같습니다.
        self.brush_size = 3           # 선의 굵기를 숫자로 저장합니다.
        self.mode = "pen"             # 현재 어떤 도구를 잡고 있는지 (기본 펜)
        self.start_x = None           # 마우스 클릭을 시작한 가로 위치
        self.start_y = None           # 마우스 클릭을 시작한 세로 위치
        self.current_obj = None       # 도형을 드래그할 때 실시간으로 그려지는 '임시 잔상'의 번호

        # [수정] 저장용 보이지 않는 도화지(배경은 흰색)를 만듭니다. (가로 2000, 세로 2000 넉넉하게 뚱뚱하게)
        self.image = Image.new("RGB", (2000, 2000), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.setup_ui()    # 화면(버튼, 도화지 등)을 만드는 함수를 실행합니다.
        self.bind_events() # 마우스 움직임과 코드를 연결하는 함수를 실행합니다.

    def setup_ui(self):
        """프로그램 상단의 도구 버튼들과 하단 도화지를 배치하는 함수입니다."""
        
        # 상단 도구함 프레임(그릇) 만들기
        self.toolbar = tk.Frame(self.root, bg="#f0f0f0", bd=1, relief="raised")
        self.toolbar.pack(side="top", fill="x", padx=5, pady=5)

        # [색상 선택 버튼]
        color_frame = tk.LabelFrame(self.toolbar, text=" 색상 ", bg="#f0f0f0")
        color_frame.pack(side="left", padx=5, pady=5)
        self.color_btn = tk.Button(color_frame, text="🎨\n색상선택", font=("Arial", 9), 
                                   bg=self.color, fg="white", width=8, height=3, 
                                   compound="top", command=self.choose_color)
        self.color_btn.pack(padx=5, pady=5)

        # [도구함 버튼들] 반복문을 사용해 여러 버튼을 한 번에 만듭니다.
        tools_frame = tk.LabelFrame(self.toolbar, text=" 도구함 ", bg="#f0f0f0")
        tools_frame.pack(side="left", padx=5, pady=5)

        # (아이콘, 모드이름, 아래에 적힐 글자)
        tool_list = [
            ("✎", "pen", "브러시"), ("📏", "line", "직선"), ("▭", "rect", "사각형"), 
            ("◯", "oval", "원형"), ("▲", "triangle", "삼각형"), ("★", "star", "별"), 
            ("🫗", "fill_bucket", "색채우기"), ("🧼", "eraser", "지우개") 
        ]

        self.tool_buttons = {} # 생성된 버튼들을 저장해둘 주머니입니다.
        for icon, mode, label in tool_list:
            btn = tk.Button(tools_frame, text=f"{icon}\n{label}", font=("Arial", 9), 
                            width=6, height=3, compound="top",
                            command=lambda m=mode: self.set_mode(m))
            btn.pack(side="left", padx=2, pady=5)
            self.tool_buttons[mode] = btn
        
        # [선 두께 조절 슬라이더]
        size_frame = tk.LabelFrame(self.toolbar, text=" 선 두께 ", bg="#f0f0f0")
        size_frame.pack(side="left", padx=5, pady=5)
        self.size_slider = tk.Scale(size_frame, from_=1, to=50, orient="horizontal", 
                                    length=120, command=self.update_size)
        self.size_slider.set(self.brush_size) # 처음 두께를 3으로 맞춤
        self.size_slider.pack(padx=5, pady=5)

        # [전체 삭제 버튼]
        tk.Button(self.toolbar, text="🗑️\n전체삭제", font=("Arial", 9, "bold"), 
                  fg="white", bg="#ff4d4d", width=8, height=3, compound="top",
                  command=self.clear_canvas).pack(side="right", padx=10)
        
        # [저장 버튼]
        tk.Button(self.toolbar, text="💾\n저장하기", font=("Arial", 9, "bold"),
                  fg="white", bg="#4CAF50", width=8, height=3, compound="top",
                  command=self.save_canvas).pack(side="right", padx=10) # [참고] save_canvas 호출

        # [도화지(캔버스)] 실제 그림이 그려지는 영역입니다.
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross", bd=2, relief="sunken")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def bind_events(self):
        """마우스 동작(클릭, 드래그, 떼기)을 감지하도록 연결합니다."""
        self.canvas.bind("<Button-1>", self.on_press)         # 마우스 왼쪽 클릭 시
        self.canvas.bind("<B1-Motion>", self.on_move)         # 클릭한 채로 움직일 때(드래그)
        self.canvas.bind("<ButtonRelease-1>", self.on_release) # 클릭을 뗄 때

    def set_mode(self, mode):
        """현재 도구를 변경하는 함수입니다."""
        self.mode = mode
        for m, btn in self.tool_buttons.items():
            if m == mode:
                btn.config(bg="#d0d0d0", relief="sunken")
            else:
                btn.config(bg="systemButtonFace", relief="raised")

    def choose_color(self):
        """팔레트 창을 띄워 색상을 고르게 합니다."""
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.color_btn.config(bg=self.color)

    def update_size(self, val):
        self.brush_size = int(val)

    def clear_canvas(self):
        """도화지를 싹 지웁니다."""
        self.canvas.delete("all")
        # [수정] 저장용 가상 도화지도 하얗게 초기화합니다.
        self.image = Image.new("RGB", (2000, 2000), "white")
        self.draw = ImageDraw.Draw(self.image)

    def on_press(self, event):
        """마우스를 처음 딱 클릭했을 때 실행됩니다."""
        self.start_x, self.start_y = event.x, event.y
        
        if self.mode == "fill_bucket":
            item = self.canvas.find_closest(event.x, event.y)
            if item:
                self.canvas.itemconfig(item, fill=self.color)
                # 주의: 캔버스 fill_bucket은 가상 이미지 파일에는 완벽히 연동되기 어렵지만 기본 호환 유지

    def on_move(self, event):
        """마우스를 누른 채로 움직일 때 계속 실행됩니다."""
        if self.mode == "fill_bucket": return

        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        if self.mode in ["pen", "eraser"]:
            draw_color = self.color if self.mode == "pen" else self.eraser_color
            self.canvas.create_line(x1, y1, x2, y2, width=self.brush_size, 
                                    fill=draw_color, capstyle="round", smooth=True)
            
            # [수정] 펜과 지우개질을 할 때 저장용 이미지 파일에도 선을 똑같이 그려줍니다.
            self.draw.line([x1, y1, x2, y2], fill=draw_color, width=self.brush_size)
            self.start_x, self.start_y = x2, y2
        else:
            if self.current_obj: self.canvas.delete(self.current_obj)
            
            if self.mode == "rect":
                self.current_obj = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.color, width=self.brush_size)
            elif self.mode == "oval":
                self.current_obj = self.canvas.create_oval(x1, y1, x2, y2, outline=self.color, width=self.brush_size)
            elif self.mode == "line":
                self.current_obj = self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.brush_size)
            elif self.mode == "triangle":
                pts = [(x1+x2)/2, y1, x1, y2, x2, y2]
                self.current_obj = self.canvas.create_polygon(pts, outline=self.color, fill="", width=self.brush_size)
            elif self.mode == "star":
                self.current_obj = self.draw_star(x1, y1, x2, y2)

    def draw_star(self, x1, y1, x2, y2):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        out_r = min(abs(x2 - x1), abs(y2 - y1)) / 2
        in_r = out_r / 2.5
        pts = []
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            r = out_r if i % 2 == 0 else in_r
            pts.extend([cx + r * math.cos(ang), cy + r * math.sin(ang)])
        return self.canvas.create_polygon(pts, outline=self.color, fill="", width=self.brush_size)

    # [수정] 마우스를 뗄 때, 최종 확정된 도형들을 저장용 이미지에도 그려줍니다.
    def on_release(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        if self.mode == "rect":
            self.draw.rectangle([x1, y1, x2, y2], outline=self.color, width=self.brush_size)
        elif self.mode == "oval":
            self.draw.ellipse([x1, y1, x2, y2], outline=self.color, width=self.brush_size)
        elif self.mode == "line":
            self.draw.line([x1, y1, x2, y2], fill=self.color, width=self.brush_size)
        elif self.mode == "triangle":
            pts = [(x1+x2)/2, y1, x1, y2, x2, y2]
            self.draw.polygon(pts, outline=self.color, width=self.brush_size)
        elif self.mode == "star":
            # 별의 좌표를 다시 계산해서 저장 이미지에 그리기
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            out_r = min(abs(x2 - x1), abs(y2 - y1)) / 2
            in_r = out_r / 2.5
            pts = []
            for i in range(10):
                ang = math.radians(i * 36 - 90)
                r = out_r if i % 2 == 0 else in_r
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
            self.draw.polygon(pts, outline=self.color, width=self.brush_size)

        self.current_obj = None

    # [수정] 클래스 안으로 들여쓰기를 맞춰서 포함시키고, 버튼이 요구하는 이름(save_canvas)으로 변경했습니다.
    def save_canvas(self):
        """현재까지 그린 이미지를 파일로 저장합니다."""
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if path:
            # 윈도우 창 크기만큼 이미지를 잘라서 깔끔하게 저장합니다.
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            cropped_image = self.image.crop((0, 0, canvas_width, canvas_height))
            
            cropped_image.save(path)
            messagebox.showinfo("저장 완료", "그림이 성공적으로 저장되었습니다!")

# --- 프로그램 시작 부분 ---
if __name__ == "__main__":
    root = tk.Tk()      # 실제 윈도우 창을 만듭니다.
    app = PyPaint(root) # 우리가 만든 그림판 클래스를 창에 올립니다.
    root.mainloop()     # 창이 꺼지지 않도록 무한 반복하며 대기합니다.