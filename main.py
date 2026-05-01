import customtkinter as ctk
import sympy
from sympy.logic import SOPform, POSform
from sympy import symbols, sympify
import re


class CircuitWindow(ctk.CTkToplevel):
    def __init__(self, parent, expr, mode="SOP"):
        super().__init__(parent)
        self.title(f"{mode} Circuit Schematic")
        self.geometry("850x650")
        self.attributes('-topmost', True)

        # Match the clean, white "Textbook" style from the image
        self.canvas = ctk.CTkCanvas(self, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        self.expr = expr
        self.mode = mode
        self.wire_color = "#000000"
        self.text_color = "#000000"
        self.gate_outline = "#000000"

        if expr in (sympy.true, sympy.false):
            self.canvas.create_text(425, 300, text=f"Static Output: F = {expr}", fill=self.text_color,
                                    font=("Arial", 24))
            return

        self.draw_circuit()

    def draw_circuit(self):
        self.canvas.delete("all")

        # 1. Determine Logic Gate Types
        if self.mode == "SOP":
            l1_type, l2_type = "AND", "OR"
            split_expr, sub_expr = sympy.Or, sympy.And
        elif self.mode == "POS":
            l1_type, l2_type = "OR", "AND"
            split_expr, sub_expr = sympy.And, sympy.Or
        elif self.mode == "NAND":
            l1_type, l2_type = "NAND", "NAND"
            split_expr, sub_expr = sympy.Or, sympy.And
        elif self.mode == "NOR":
            l1_type, l2_type = "NOR", "NOR"
            split_expr, sub_expr = sympy.And, sympy.Or

        terms = self.expr.args if isinstance(self.expr, split_expr) else [self.expr]

        l1_gate_x = 200
        l1_y_start = 100
        y_spacing = max(450 // max(len(terms), 1), 90)
        l1_outputs = []
        gate_counter = 1

        # 2. Draw Level 1 Gates & Direct Horizontal Inputs
        for idx, term in enumerate(terms):
            y_pos = l1_y_start + (idx * y_spacing)
            factors = term.args if isinstance(term, sub_expr) else [term]

            # Calculate safe wire spacing
            num_inputs = len(factors)
            if num_inputs == 1:
                offsets = [0]
                step = 20  # Arbitrary fallback for font logic
            else:
                max_span = 44  # Safely uses most of the 50px gate height (-25 to +25)
                req_span = 20 * (num_inputs - 1)
                actual_span = min(max_span, req_span)
                step = actual_span / (num_inputs - 1)
                start_offset = -actual_span / 2
                offsets = [start_offset + i * step for i in range(num_inputs)]

            # --- THE FIX: DYNAMIC FONT SIZE ---
            # Max size 16, Min size 10. Shrinks automatically if wires are tight.
            label_font_size = max(10, min(16, int(step)))

            for f_idx, factor in enumerate(factors):
                f_str = str(factor).replace("Not(", "~").replace(")", "")
                f_str = f_str.replace("~", "") + "'" if "~" in f_str else f_str

                pin_y = y_pos + offsets[f_idx]

                self.canvas.create_line(80, pin_y, l1_gate_x + 15, pin_y, fill=self.wire_color, width=2)
                self.canvas.create_text(70, pin_y, text=f_str, fill=self.text_color,
                                        font=("Arial", label_font_size, "bold"), anchor="e")

            self.draw_gate(l1_gate_x, y_pos, l1_type, label=f"G{gate_counter}")

            out_start_x = l1_gate_x + (58 if "N" in l1_type else 50)
            l1_outputs.append((out_start_x, y_pos))
            gate_counter += 1

        # 3. Draw Level 2 Gate & Stepped Wiring
        if len(terms) > 1:
            l2_gate_x = l1_gate_x + 220
            l2_y_pos = l1_y_start + ((len(terms) - 1) * y_spacing) // 2

            num_l2_inputs = len(l1_outputs)
            if num_l2_inputs == 1:
                l2_offsets = [0]
            else:
                max_span = 44
                req_span = 20 * (num_l2_inputs - 1)
                actual_span = min(max_span, req_span)
                step = actual_span / (num_l2_inputs - 1)
                start_offset = -actual_span / 2
                l2_offsets = [start_offset + i * step for i in range(num_l2_inputs)]

            for i, (out_x, out_y) in enumerate(l1_outputs):
                target_y = l2_y_pos + l2_offsets[i]
                mid_x = out_x + 60

                self.canvas.create_line(out_x, out_y, mid_x, out_y, fill=self.wire_color, width=2)
                self.canvas.create_line(mid_x, out_y, mid_x, target_y, fill=self.wire_color, width=2)
                self.canvas.create_line(mid_x, target_y, l2_gate_x + 15, target_y, fill=self.wire_color, width=2)

            self.draw_gate(l2_gate_x, l2_y_pos, l2_type, label=f"G{gate_counter}")

            final_out_x = l2_gate_x + (58 if "N" in l2_type else 50)
            self.canvas.create_line(final_out_x, l2_y_pos, final_out_x + 60, l2_y_pos, fill=self.wire_color, width=2)
            self.canvas.create_text(final_out_x + 70, l2_y_pos, text="F", fill=self.text_color,
                                    font=("Arial", 20, "bold"), anchor="w")

        else:
            out_x, out_y = l1_outputs[0]
            self.canvas.create_line(out_x, out_y, out_x + 60, out_y, fill=self.wire_color, width=2)
            self.canvas.create_text(out_x + 70, out_y, text="F", fill=self.text_color, font=("Arial", 20, "bold"),
                                    anchor="w")

    def draw_gate(self, x, y, gate_type, label=""):
        """ Draws actual logic gate shapes using polygons """
        if "AND" in gate_type:
            # D-Shape
            pts = [
                x, y - 25, x + 25, y - 25, x + 35, y - 20, x + 43, y - 12, x + 50, y,
                   x + 43, y + 12, x + 35, y + 20, x + 25, y + 25, x, y + 25
            ]
        else:
            # Shield-Shape (OR / NOR)
            pts = [
                x, y - 25, x + 15, y - 22, x + 30, y - 15, x + 42, y - 6,
                   x + 50, y, x + 42, y + 6, x + 30, y + 15, x + 15, y + 22,
                x, y + 25, x + 10, y + 12, x + 12, y, x + 10, y - 12
            ]

        # Draw main gate body
        self.canvas.create_polygon(pts, fill="#ffffff", outline=self.gate_outline, width=2)

        # Add the G1, G2 label inside
        self.canvas.create_text(x + 20, y, text=label, fill="#2980b9", font=("Arial", 11, "bold"))

        # Add inversion circle for NAND / NOR
        if "N" in gate_type:
            self.canvas.create_oval(x + 50, y - 4, x + 58, y + 4, fill="#ffffff", outline=self.gate_outline, width=2)


class TruthTableWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Truth Table Input")
        self.geometry("350x550")
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text=f"{self.parent.num_vars}-Variable Truth Table",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20)
        for h in ["A", "B", "C", "D"][:self.parent.num_vars] + ["F (Out)"]:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(weight="bold"), width=30).pack(side="left", padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.buttons = {}
        for m_val in range(2 ** self.parent.num_vars):
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            bin_str = bin(m_val)[2:].zfill(self.parent.num_vars)
            for bit in bin_str:
                ctk.CTkLabel(row_frame, text=bit, width=30).pack(side="left", padx=10)

            current_state = self.parent.cell_states[m_val]
            btn = ctk.CTkButton(row_frame, text=current_state, width=40, command=lambda m=m_val: self.toggle_row(m))
            btn.pack(side="left", padx=20)
            self.buttons[m_val] = btn
            self.update_btn_color(btn, current_state)

        ctk.CTkButton(self, text="Solve & Close", command=self.apply_and_close, fg_color="#28a745",
                      hover_color="#218838").pack(pady=15)

    def toggle_row(self, m_val):
        current = self.parent.cell_states[m_val]
        nxt = "1" if current == "0" else ("X" if current == "1" else "0")
        self.parent.cell_states[m_val] = nxt
        self.buttons[m_val].configure(text=nxt)
        self.update_btn_color(self.buttons[m_val], nxt)
        self.parent.cells[m_val].configure(text=nxt)
        self.parent.update_cell_color(m_val, nxt)

    def update_btn_color(self, btn, state):
        colors = {"0": "#333333", "1": "#1f538d", "X": "#b8860b"}
        btn.configure(fg_color=colors[state])

    def apply_and_close(self):
        self.parent.solve_kmap()
        self.destroy()


class KMapSolverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boolean Minimizer & Logic Generator")
        self.geometry("1000x850")
        ctk.set_appearance_mode("dark")

        self.num_vars = 4
        self.cells = {}
        self.cell_states = {}
        self.term_buttons = []
        self.group_colors = ["#FF5733", "#33FF57", "#3357FF", "#F033FF", "#FFD433", "#33FFF0", "#FF8333"]

        self.current_sop_expr = None
        self.current_pos_expr = None

        self.setup_ui()
        self.build_grid()

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="EDA Logic Synthesizer", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20,
                                                                                                                padx=20)
        ctk.CTkLabel(self.sidebar, text="Number of Variables:").pack(pady=(10, 0), padx=20, anchor="w")

        self.var_select = ctk.CTkSegmentedButton(self.sidebar, values=["2", "3", "4"], command=self.change_vars)
        self.var_select.set("4")
        self.var_select.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="Edit Truth Table", command=lambda: TruthTableWindow(self),
                      fg_color="#e67e22").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Solve Grid", command=self.solve_kmap, fg_color="#28a745").pack(pady=10,
                                                                                                         padx=20,
                                                                                                         fill="x")
        ctk.CTkButton(self.sidebar, text="Clear Grid", command=self.clear_grid, fg_color="#dc3545").pack(pady=0,
                                                                                                         padx=20,
                                                                                                         fill="x")

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#555555").pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(self.sidebar, text="Parse Boolean Expr:\n(e.g., A*B + C')", justify="left").pack(pady=(0, 5),
                                                                                                      padx=20,
                                                                                                      anchor="w")
        self.expr_entry = ctk.CTkEntry(self.sidebar, placeholder_text="A&B | ~C")
        self.expr_entry.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Parse & Solve", command=self.parse_expression, fg_color="#1f538d").pack(
            pady=10, padx=20, fill="x")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(pady=10, expand=True)

        self.equation_label = ctk.CTkLabel(self.main_frame, text="---", font=ctk.CTkFont(size=26, weight="bold"),
                                           text_color="#f1c40f")
        self.equation_label.pack(pady=5)

        self.metrics_label = ctk.CTkLabel(self.main_frame, text="", text_color="#aaaaaa")
        self.metrics_label.pack()

        self.hw_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b", corner_radius=10)
        self.hw_frame.pack(pady=15, padx=20, fill="x")

        self.nand_label = ctk.CTkLabel(self.hw_frame, text="NAND Implementation: ---", font=ctk.CTkFont(size=14))
        self.nand_label.pack(pady=5)
        self.nor_label = ctk.CTkLabel(self.hw_frame, text="NOR Implementation: ---", font=ctk.CTkFont(size=14))
        self.nor_label.pack(pady=5)

        # Added NAND and NOR circuit viewing options to match the image!
        btn_frame = ctk.CTkFrame(self.hw_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, width=100, text="View SOP", command=lambda: self.open_circuit("SOP"),
                      fg_color="#8e44ad").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, width=100, text="View POS", command=lambda: self.open_circuit("POS"),
                      fg_color="#2980b9").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, width=100, text="View NAND", command=lambda: self.open_circuit("NAND"),
                      fg_color="#c0392b").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, width=100, text="View NOR", command=lambda: self.open_circuit("NOR"),
                      fg_color="#d35400").pack(side="left", padx=5)

        self.legend_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.legend_frame.pack(pady=5, fill="x")

    def open_circuit(self, mode):
        # SOP and NAND use the SOP expression layout
        if mode in ["SOP", "NAND"]:
            expr = self.current_sop_expr
        # POS and NOR use the POS expression layout
        else:
            expr = self.current_pos_expr

        if expr is not None:
            CircuitWindow(self, expr, mode)

    def get_gray_code(self, n):
        if n == 1: return ['0', '1']
        if n == 2: return ['00', '01', '11', '10']
        return []

    def change_vars(self, value):
        self.num_vars = int(value)
        self.build_grid()
        self.reset_outputs()

    def build_grid(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.cells.clear()
        self.cell_states.clear()

        r_vars = 1 if self.num_vars < 4 else 2
        c_vars = 1 if self.num_vars == 2 else 2
        row_labels, col_labels = self.get_gray_code(r_vars), self.get_gray_code(c_vars)

        top_label = "B" if self.num_vars == 2 else ("BC" if self.num_vars == 3 else "CD")
        side_label = "A" if self.num_vars < 4 else "AB"

        ctk.CTkLabel(self.grid_frame, text=f"{side_label} \\ {top_label}", font=ctk.CTkFont(weight="bold")).grid(row=0,
                                                                                                                 column=0,
                                                                                                                 padx=10,
                                                                                                                 pady=10)
        for j, col_val in enumerate(col_labels): ctk.CTkLabel(self.grid_frame, text=col_val,
                                                              font=ctk.CTkFont(weight="bold")).grid(row=0, column=j + 1)

        for i, row_val in enumerate(row_labels):
            ctk.CTkLabel(self.grid_frame, text=row_val, font=ctk.CTkFont(weight="bold")).grid(row=i + 1, column=0,
                                                                                              padx=5)
            for j, col_val in enumerate(col_labels):
                m_val = int(row_val + col_val, 2)
                btn = ctk.CTkButton(self.grid_frame, text="0", width=60, height=60, font=ctk.CTkFont(size=20),
                                    fg_color="#333333", command=lambda m=m_val: self.toggle_cell(m))
                btn.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                self.cells[m_val] = btn
                self.cell_states[m_val] = "0"

    def toggle_cell(self, m_val):
        current = self.cell_states[m_val]
        nxt = "1" if current == "0" else ("X" if current == "1" else "0")
        self.cell_states[m_val] = nxt
        self.cells[m_val].configure(text=nxt)
        self.update_cell_color(m_val, nxt)
        self.reset_outputs()

    def update_cell_color(self, m_val, state):
        colors = {"0": "#333333", "1": "#1f538d", "X": "#b8860b"}
        self.cells[m_val].configure(fg_color=colors[state])

    def clear_grid(self):
        for m_val in self.cells:
            self.cell_states[m_val] = "0"
            self.cells[m_val].configure(text="0", fg_color="#333333", border_width=0)
        self.reset_outputs()

    def reset_outputs(self):
        self.current_sop_expr = None
        self.current_pos_expr = None
        self.equation_label.configure(text="---", text_color="#f1c40f")
        self.metrics_label.configure(text="")
        self.nand_label.configure(text="NAND Implementation: ---")
        self.nor_label.configure(text="NOR Implementation: ---")
        for btn in self.cells.values(): btn.configure(border_width=0)
        for widget in self.legend_frame.winfo_children(): widget.destroy()
        self.term_buttons.clear()

    def parse_expression(self):
        raw_expr = self.expr_entry.get().strip()
        if not raw_expr: return

        clean_expr = raw_expr.replace('+', '|').replace('*', '&')
        clean_expr = re.sub(r'([a-zA-Z])\'', r'~\1', clean_expr)
        sym_list = symbols('A B C D')[:self.num_vars]

        try:
            parsed_expr = sympify(clean_expr, locals={str(s): s for s in sym_list})
            self.clear_grid()

            for m_val in range(2 ** self.num_vars):
                bin_str = bin(m_val)[2:].zfill(self.num_vars)
                subs_dict = {sym_list[k]: int(bin_str[k]) for k in range(self.num_vars)}
                if parsed_expr.subs(subs_dict) in (True, 1):
                    self.cell_states[m_val] = "1"
                    self.cells[m_val].configure(text="1")
                    self.update_cell_color(m_val, "1")

            self.solve_kmap()
        except:
            self.clear_grid()
            self.equation_label.configure(text="Invalid Expression Syntax!", text_color="#dc3545")

    def format_boolean_string(self, sym_expr):
        raw_str = str(sym_expr).replace(" ", "")
        raw_str = re.sub(r'~([a-zA-Z0-9_]+)', r"\1'", raw_str)
        return raw_str.replace('|', ' + ').replace('&', '')

    def solve_kmap(self):
        minterms = [m for m, state in self.cell_states.items() if state == "1"]
        dontcares = [m for m, state in self.cell_states.items() if state == "X"]

        if not minterms:
            self.equation_label.configure(text="F = 0")
            self.current_sop_expr = sympy.false
            return

        sym_list = symbols('A B C D')[:self.num_vars]

        self.current_sop_expr = SOPform(sym_list, minterms, dontcares)
        sop_str = self.format_boolean_string(self.current_sop_expr)
        self.equation_label.configure(text=f"F = {sop_str}", text_color="#f1c40f")

        unopt_lits = len(minterms) * self.num_vars
        opt_lits = sum(1 for c in sop_str if c.isalpha())
        reduction = round(100 * (unopt_lits - opt_lits) / unopt_lits, 1) if unopt_lits else 0
        self.metrics_label.configure(
            text=f"Efficiency Improved: Literals reduced from {unopt_lits} to {opt_lits} ({reduction}% reduction)")

        nand_str = self.generate_nand_string(self.current_sop_expr)
        self.nand_label.configure(text=f"NAND Only:  F = {nand_str}")

        self.current_pos_expr = POSform(sym_list, minterms, dontcares)
        nor_str = self.generate_nor_string(self.current_pos_expr)
        self.nor_label.configure(text=f"NOR Only:  F = {nor_str}")

        self.generate_interactive_legend(self.current_sop_expr, sym_list)

    def generate_nand_string(self, sop_expr):
        if sop_expr in (sympy.true, sympy.false): return str(sop_expr)
        terms = sop_expr.args if isinstance(sop_expr, sympy.Or) else [sop_expr]
        term_strs = [self.format_boolean_string(t) for t in terms]
        if len(term_strs) > 1: return "( " + " * ".join([f"({t})'" for t in term_strs]) + " )'"
        return term_strs[0]

    def generate_nor_string(self, pos_expr):
        if pos_expr in (sympy.true, sympy.false): return str(pos_expr)
        terms = pos_expr.args if isinstance(pos_expr, sympy.And) else [pos_expr]
        term_strs = [str(t).replace(" ", "").replace('|', '+').replace('&', '*') for t in terms]
        term_strs = [re.sub(r'~([a-zA-Z0-9_]+)', r"\1'", t) for t in term_strs]
        if len(term_strs) > 1: return "( " + " + ".join([f"({t})'" for t in term_strs]) + " )'"
        return term_strs[0]

    def generate_interactive_legend(self, expression, sym_list):
        for widget in self.legend_frame.winfo_children(): widget.destroy()
        self.term_buttons.clear()

        if expression in (sympy.true, sympy.false): return

        ctk.CTkLabel(self.legend_frame, text="Interactive SOP Groups (Hover/Click):",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)
        btn_frame = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
        btn_frame.pack()

        terms = expression.args if isinstance(expression, sympy.Or) else [expression]

        for idx, term in enumerate(terms):
            color = self.group_colors[idx % len(self.group_colors)]
            btn = ctk.CTkButton(btn_frame, text=self.format_boolean_string(term), fg_color=color, text_color="black",
                                hover_color=color)
            btn.pack(side="left", padx=5)

            btn.bind("<Enter>", lambda e, t=term, c=color: self.highlight_group(t, sym_list, c))
            btn.bind("<Leave>", lambda e: self.reset_highlights())
            self.term_buttons.append(btn)

    def highlight_group(self, term, sym_list, color):
        self.reset_highlights()
        for m_val, btn in self.cells.items():
            bin_str = bin(m_val)[2:].zfill(self.num_vars)
            subs_dict = {sym_list[k]: int(bin_str[k]) for k in range(self.num_vars)}
            if term.subs(subs_dict) == True:
                btn.configure(border_width=4, border_color=color)

    def reset_highlights(self):
        for btn in self.cells.values(): btn.configure(border_width=0)


if __name__ == "__main__":
    app = KMapSolverApp()
    app.mainloop()
