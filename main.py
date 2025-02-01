from tkinter import *
from ctypes import windll
import json
import threading
import requests
import ctypes
import subprocess
import os

tk_title = "Chat-Bot"

OLLAMA_MODEL = "deepseek-r1:14b"
# OLLAMA_MODEL = "llama3.1:8b"

root = Tk()  # Create root window
root.title(tk_title)

# Configure window dimensions and position
sWidth = root.winfo_screenwidth()
sHeight = root.winfo_screenheight()
window_width = 800
window_height = 600
x_coordinate = int((sWidth / 2) - (window_width / 2))
y_coordinate = int((sHeight / 2) - (window_height / 2))

root.overrideredirect(True)
root.geometry(f'{window_width}x{window_height}+{x_coordinate}+{y_coordinate}')
root.minimized = False
root.maximized = False

# Color scheme
LGRAY = '#3e4042'
DGRAY = '#25292e'
RGRAY = '#10121f'
LBLUE = '#6fc3ff'
RED = '#ed093f'

root.config(bg=DGRAY)
title_bar = Frame(root, bg=RGRAY, relief='raised', bd=0, highlightthickness=0)

subprocess.Popen(
    ["ollama", "run", OLLAMA_MODEL],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
)

def set_appwindow(mainWindow):
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    hwnd = windll.user32.GetParent(mainWindow.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)
    mainWindow.wm_withdraw()
    mainWindow.after(10, lambda: mainWindow.wm_deiconify())


def minimize_me():
    root.attributes("-alpha", 0)
    root.minimized = True


def deminimize(event):
    if root.minimized:
        root.attributes("-alpha", 1)
        root.minimized = False
        root.focus()


def maximize_me():
    if not root.maximized:
        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)
            ]

        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.pointer(rect), 0)
        work_width = rect.right - rect.left
        work_height = rect.bottom - rect.top
        root.normal_size = root.geometry()
        expand_button.config(text=" 🗗 ")
        root.geometry(f"{work_width}x{work_height}+{rect.left}+{rect.top}")
        root.maximized = True
    else:
        expand_button.config(text=" 🗖 ")
        root.geometry(root.normal_size)
        root.maximized = False


# Title bar buttons
close_button = Button(title_bar, text='  ×  ', command=root.destroy, bg=RGRAY,
                      padx=2, pady=2, font=("calibri", 13), bd=0, fg='white',
                      highlightthickness=0)
expand_button = Button(title_bar, text=' 🗖 ', command=maximize_me, bg=RGRAY,
                       padx=2, pady=2, bd=0, fg='white', font=("calibri", 13),
                       highlightthickness=0)
minimize_button = Button(title_bar, text=' 🗕 ', command=minimize_me, bg=RGRAY,
                         padx=2, pady=2, bd=0, fg='white', font=("calibri", 13),
                         highlightthickness=0)
title_bar_title = Label(title_bar, text=tk_title, bg=RGRAY, bd=0, fg='white',
                        font=("helvetica", 10), highlightthickness=0)

window = Frame(root, bg=DGRAY, highlightthickness=0)

# Pack widgets
title_bar.pack(fill=X)
close_button.pack(side=RIGHT, ipadx=7, ipady=1)
expand_button.pack(side=RIGHT, ipadx=7, ipady=1)
minimize_button.pack(side=RIGHT, ipadx=7, ipady=1)
title_bar_title.pack(side=LEFT, padx=10)
window.pack(expand=1, fill=BOTH)


# Window movement and styling functions
def changex_on_hovering(event): close_button['bg'] = 'red'


def returnx_to_normalstate(event): close_button['bg'] = RGRAY


def change_size_on_hovering(event): expand_button['bg'] = LGRAY


def return_size_on_hovering(event): expand_button['bg'] = RGRAY


def changem_size_on_hovering(event): minimize_button['bg'] = LGRAY


def returnm_size_on_hovering(event): minimize_button['bg'] = RGRAY


def get_pos(event):
    if not root.maximized:
        xwin = root.winfo_x()
        ywin = root.winfo_y()
        startx, starty = event.x_root, event.y_root
        ywin -= starty
        xwin -= startx

        def move_window(event):
            root.config(cursor="fleur")
            root.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')

        def release_window(event): root.config(cursor="arrow")

        title_bar.bind('<B1-Motion>', move_window)
        title_bar.bind('<ButtonRelease-1>', release_window)
        title_bar_title.bind('<B1-Motion>', move_window)
        title_bar_title.bind('<ButtonRelease-1>', release_window)


title_bar.bind('<Button-1>', get_pos)
title_bar_title.bind('<Button-1>', get_pos)

# Button hover effects
close_button.bind('<Enter>', changex_on_hovering)
close_button.bind('<Leave>', returnx_to_normalstate)
expand_button.bind('<Enter>', change_size_on_hovering)
expand_button.bind('<Leave>', return_size_on_hovering)
minimize_button.bind('<Enter>', changem_size_on_hovering)
minimize_button.bind('<Leave>', returnm_size_on_hovering)

# Resize handles
resizex_widget = Frame(window, bg=DGRAY, cursor='sb_h_double_arrow')
resizex_widget.pack(side=TOP, ipadx=2, fill=Y)
resizey_widget = Frame(window, bg=DGRAY, cursor='sb_v_double_arrow')
resizey_widget.pack(side=BOTTOM, ipadx=2, fill=X)


def resizex(event):
    if root.winfo_width() > 150:
        try:
            root.geometry(f"{root.winfo_width() + (event.x_root - root.winfo_x() - root.winfo_width())}x{root.winfo_height()}")
        except:
            pass
    resizex_widget.config(bg=DGRAY)


def resizey(event):
    if root.winfo_height() > 150:
        try:
            root.geometry(f"{root.winfo_width()}x{root.winfo_height() + (event.y_root - root.winfo_y() - root.winfo_height())}")
        except:
            pass
    resizex_widget.config(bg=DGRAY)


resizex_widget.bind("<B1-Motion>", resizex)
resizey_widget.bind("<B1-Motion>", resizey)

root.bind("<FocusIn>", deminimize)
root.after(10, lambda: set_appwindow(root))

# =====================
# UI Configuration
# =====================

# Main chat container
text_container = Frame(window, bg=DGRAY)
text_container.pack(expand=True, fill=BOTH, padx=10, pady=5)

# Input area container
input_frame = Frame(window, bg=DGRAY, height=40)
input_frame.pack(side=BOTTOM, fill=X, padx=10, pady=5)
input_frame.pack_propagate(False)  # Lock input area height
input_frame.grid_columnconfigure(0, weight=1)
input_frame.grid_rowconfigure(0, weight=1)

# =====================
# Input Field Components
# =====================

# Rounded background canvas
canvas = Canvas(input_frame, bg=DGRAY, highlightthickness=0, height=40)
canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))


def create_rounded_rect(canvas, x1, y1, x2, y2, r=25, **kwargs):
    """Creates a smooth rounded rectangle polygon"""
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1, x1 + r, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# Text entry widget
entry = Entry(
    canvas,
    fg="white", bg=LBLUE,
    font=("Arial", 12),
    relief=FLAT, bd=0,
    insertbackground="white"
)
entry_window = canvas.create_window(15, 10, anchor="nw", window=entry)

# =====================
# Send Button Components
# =====================

send_btn = Button(
    input_frame,
    text="➤",
    fg="white", bg=LBLUE,
    activeforeground="white", activebackground=LGRAY,
    font=("Arial", 14, "bold"),
    relief=FLAT, bd=0,
    command=lambda: send_message()
)
send_btn.grid(row=0, column=1, sticky="ns")


# Hover effects
def on_enter(e): send_btn.config(bg=LGRAY)


def on_leave(e): send_btn.config(bg=LBLUE)


send_btn.bind("<Enter>", on_enter)
send_btn.bind("<Leave>", on_leave)

# =====================
# Chat History Display
# =====================

scrollbar = Scrollbar(text_container, bg=DGRAY, troughcolor=RGRAY)
scrollbar.pack(side=RIGHT, fill=Y)

T = Text(
    text_container,
    fg="white", bg=DGRAY,
    font=("Arial", 12),
    wrap=WORD, padx=0, pady=10,
    yscrollcommand=scrollbar.set,
    insertbackground="white",
    bd=0
)
T.pack(expand=True, fill=BOTH)
T.configure(state=DISABLED)
scrollbar.config(command=T.yview)

# Message formatting tags
T.tag_configure("user", foreground=LBLUE, lmargin1=0, lmargin2=0, rmargin=20)
T.tag_configure("bot", foreground=RED, lmargin1=0, lmargin2=0, rmargin=20)


# =====================
# UI Update Handlers
# =====================

def update_ui(event):
    """Responsive layout updates for canvas and entry"""
    # Update canvas background
    canvas.delete("bg")
    create_rounded_rect(canvas, 0, 0, event.width, event.height,
                        r=20, fill=LBLUE, tags="bg")

    # Resize entry widget
    entry_width = event.width - 30
    entry_height = event.height - 10
    canvas.coords(entry_window, 15, 5)
    canvas.itemconfigure(entry_window, width=entry_width, height=entry_height)


canvas.bind("<Configure>", update_ui)

# =====================
# Chat Functionality
# =====================

response_position = None
entry.focus_set()


def display_response(chunk, done=False):
    """Update chat display with streaming response"""
    global response_position
    T.configure(state=NORMAL)

    if response_position is None and chunk.strip():
        T.insert(END, "<Sparky> ", "bot")
        response_position = T.index(INSERT)

    if chunk.strip():
        T.insert(response_position, chunk, "bot")
        response_position = T.index(INSERT)
        T.see(END)

    if done:
        response_position = None
        T.insert(END, "\n")

    T.configure(state=DISABLED if not done else NORMAL)


def get_ollama_response(message, callback):
    """Handle LLM response streaming"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': OLLAMA_MODEL, 'prompt': message, 'stream': True},
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    callback(chunk.get('response', ''), chunk.get('done', False))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        callback(f"Error: {str(e)}", True)


def send_message(event=None):
    """Handle message submission"""
    global response_position
    message = entry.get().strip()

    if message:
        entry.delete(0, END)
        T.configure(state=NORMAL)
        T.insert(END, f"<You> {message}\n", "user")
        T.configure(state=DISABLED)
        T.see(END)
        response_position = None

        # Handle response in separate thread
        threading.Thread(
            target=get_ollama_response,
            args=(message, lambda r, d: window.after(0, display_response, r, d)),
            daemon=True
        ).start()


entry.bind("<Return>", send_message)

# =====================
# Start Application
# =====================

root.mainloop()