# Boolean Minimizer & Logic Generator EDA⚡

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg)
![Math](https://img.shields.io/badge/Math-SymPy-orange.svg)

An Electronic Design Automation (EDA) desktop application designed to automate Boolean logic minimization and physical circuit generation. It bridges the gap between mathematical logic synthesis and schematic design by instantly converting constraints into optimized logic expressions and ANSI/IEEE standard circuit diagrams.

(link_<img width="1916" height="1001" alt="project screenshot" src="https://github.com/user-attachments/assets/5c0ac452-4a01-4f94-92e1-911853cb31ad" />


## ✨ Core Features

*   **Multi-Modal Input System:**
    *   **Interactive K-Map Grid:** Click to toggle states (1, 0, or X for "Don't Cares").
    *   **Truth Table Editor:** A synchronized, scrollable interface for tabular data entry.
    *   **Algebraic Parser:** Type raw Boolean expressions (e.g., `A*B + C'`) directly into the engine.
*   **Automated Logic Minimization:** Powered by the Quine-McCluskey tabular method via SymPy, instantly generating minimized **SOP** (Sum of Products) and **POS** (Product of Sums) expressions.
*   **Universal Gate Synthesis:** Automatically translates standard logic into cost-effective **NAND-only** and **NOR-only** implementations using De Morgan's laws.
*   **Procedural Schematic Drawing:** A custom rendering engine that procedurally draws physical logic gate schematics (D-shape AND, Shield-shape OR) and routes wires based on the optimized mathematical equations.
*   **Hardware Efficiency Metrics:** Calculates live circuit complexity reductions, explicitly showing the percentage of hardware literals saved vs. an unoptimized design.

## 🛠️ Tech Stack

*   **Python:** Core logic and application structure.
*   **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** Modern, dark-mode graphical user interface.
*   **[SymPy](https://www.sympy.org/):** Symbolic mathematics library handling the heavy lifting of the Boolean algebraic minimization.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/LogicSynth-EDA.git](https://github.com/yourusername/LogicSynth-EDA.git)
   cd LogicSynth-EDA
