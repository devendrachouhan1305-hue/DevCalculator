import ast
import operator
import tkinter as tk

# dev calculator - simple Windows desktop calculator
# Features: +, -, *, /, decimals, clear, equals, backspace, keyboard support.

BG = "#111827"
PANEL = "#1f2937"
DISPLAY_BG = "#0b1220"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
BUTTON = "#263244"
BUTTON_HOVER = "#35445b"
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
DANGER = "#b91c1c"
DANGER_HOVER = "#991b1b"

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    """Evaluate only numbers and basic arithmetic operators."""
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left = visit(node.left)
            right = visit(node.right)
            return OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](visit(node.operand))
        raise ValueError("Unsupported expression")

    return visit(tree)


class DevCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("dev calculator")
        self.root.geometry("390x570")
        self.root.minsize(330, 500)
        self.root.configure(bg=BG)

        self.expression = tk.StringVar(value="")
        self.just_calculated = False

        self.build_ui()
        self.bind_keyboard()
        self.root.after(100, self.display.focus_set)

    def build_ui(self):
        outer = tk.Frame(self.root, bg=BG, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header, text="dev calculator", bg=BG, fg=TEXT,
            font=("Segoe UI", 19, "bold")
        ).pack(side="left")

        tk.Label(
            header, text="SIMPLE EDITION", bg=BG, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(side="right", pady=(9, 0))

        display_card = tk.Frame(
            outer, bg=DISPLAY_BG, highlightthickness=1,
            highlightbackground="#334155"
        )
        display_card.pack(fill="x", pady=(0, 18))

        self.display = tk.Entry(
            display_card,
            textvariable=self.expression,
            font=("Segoe UI", 27),
            bg=DISPLAY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            justify="right",
            relief="flat",
            bd=0
        )
        self.display.pack(fill="x", padx=16, pady=24, ipady=8)

        tk.Label(
            outer, text="Use your keyboard or click the buttons",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 10))

        keypad = tk.Frame(outer, bg=BG)
        keypad.pack(fill="both", expand=True)

        for r in range(5):
            keypad.rowconfigure(r, weight=1, uniform="row")
        for c in range(4):
            keypad.columnconfigure(c, weight=1, uniform="col")

        buttons = [
            ("C", "⌫", "÷", "×"),
            ("7", "8", "9", "−"),
            ("4", "5", "6", "+"),
            ("1", "2", "3", "="),
            ("0", ".", None, None),
        ]

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                if label is None:
                    continue
                if label == "0":
                    self.make_button(keypad, label, lambda: self.add("0"),
                                     r, c, colspan=2)
                elif label == ".":
                    self.make_button(keypad, label, self.add_decimal, r, c)
                elif label == "C":
                    self.make_button(keypad, label, self.clear, r, c, danger=True)
                elif label == "⌫":
                    self.make_button(keypad, label, self.backspace, r, c)
                elif label == "=":
                    self.make_button(keypad, label, self.calculate, r, c,
                                     accent=True, rowspan=2)
                else:
                    value = {"÷": "/", "×": "*", "−": "-"}.get(label, label)
                    self.make_button(keypad, label, lambda v=value: self.add(v), r, c)

        footer = tk.Label(
            outer, text="Made with care • Windows edition",
            bg=BG, fg="#64748b", font=("Segoe UI", 8)
        )
        footer.pack(pady=(14, 0))

    def make_button(self, parent, label, command, row, col,
                    colspan=1, rowspan=1, accent=False, danger=False):
        base = ACCENT if accent else DANGER if danger else BUTTON
        hover = ACCENT_HOVER if accent else DANGER_HOVER if danger else BUTTON_HOVER

        btn = tk.Button(
            parent,
            text=label,
            command=command,
            bg=base,
            fg=TEXT,
            activebackground=hover,
            activeforeground=TEXT,
            font=("Segoe UI", 17, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            takefocus=True
        )
        btn.grid(
            row=row, column=col, columnspan=colspan, rowspan=rowspan,
            sticky="nsew", padx=4, pady=4
        )
        btn.bind("<Enter>", lambda event, b=btn, color=hover: b.configure(bg=color))
        btn.bind("<Leave>", lambda event, b=btn, color=base: b.configure(bg=color))

    def add(self, value):
        current = self.expression.get()
        if current == "Error" or self.just_calculated:
            if value in "+-*/":
                self.just_calculated = False
            else:
                current = ""
                self.expression.set("")
                self.just_calculated = False
        self.expression.set(current + value)
        self.display.icursor(tk.END)

    def add_decimal(self):
        current = self.expression.get()
        if current == "Error" or self.just_calculated:
            current = ""
            self.expression.set("")
            self.just_calculated = False

        # Only add a decimal if the current number doesn't already contain one.
        current_number = current.replace("+", " ").replace("-", " ")
        current_number = current_number.replace("*", " ").replace("/", " ").split(" ")[-1]
        if "." not in current_number:
            if not current or current[-1] in "+-*/":
                self.expression.set(current + "0.")
            else:
                self.expression.set(current + ".")
        self.display.icursor(tk.END)

    def clear(self):
        self.expression.set("")
        self.just_calculated = False
        self.display.focus_set()

    def backspace(self):
        current = self.expression.get()
        if current == "Error" or self.just_calculated:
            self.clear()
            return
        cursor = self.display.index(tk.INSERT)
        if cursor > 0:
            self.expression.set(current[:cursor - 1] + current[cursor:])
            self.display.icursor(cursor - 1)
        self.display.focus_set()

    def calculate(self):
        current = self.expression.get().strip()
        if not current or current == "Error":
            return
        try:
            result = safe_calculate(current)
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
            self.expression.set(str(result))
            self.just_calculated = True
        except ZeroDivisionError:
            self.expression.set("Cannot divide by zero")
            self.just_calculated = True
        except Exception:
            self.expression.set("Error")
            self.just_calculated = True
        self.display.icursor(tk.END)

    def bind_keyboard(self):
        self.root.bind("<Return>", lambda event: self.calculate())
        self.root.bind("<KP_Enter>", lambda event: self.calculate())
        self.root.bind("<Escape>", lambda event: self.clear())
        self.root.bind("<BackSpace>", lambda event: self.backspace())

        def key_input(event):
            if event.char in "0123456789+-*/":
                self.add(event.char)
                return "break"
            if event.char == ".":
                self.add_decimal()
                return "break"
            return None

        # Handle keys on the Entry before Tkinter's default Entry binding.
        # Returning "break" prevents the same key from being inserted twice.
        self.display.bind("<Key>", key_input)

        # Keep keyboard support when a calculator button has focus.
        def button_focused_key_input(event):
            if event.widget is self.display:
                return None
            return key_input(event)

        self.root.bind("<Key>", button_focused_key_input)


if __name__ == "__main__":
    window = tk.Tk()
    app = DevCalculator(window)
    window.mainloop()
