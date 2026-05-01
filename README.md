# LogicSynth EDA: Interactive K-Map & Circuit Generator ⚡

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg)
![Math](https://img.shields.io/badge/Math-SymPy-orange.svg)

An Electronic Design Automation (EDA) desktop application designed to automate Boolean logic minimization and physical circuit generation. It bridges the gap between mathematical logic synthesis and schematic design by instantly converting constraints into optimized logic expressions and ANSI/IEEE standard circuit diagrams.

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
   git clone [https://github.com/MinaYoussefKamal/boolean-minimizer-circuit-generator.git](https://github.com/MinaYoussefKamal/boolean-minimizer-circuit-generator.git)
   cd boolean-minimizer-circuit-generator
   ```

2. **Install required dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install customtkinter sympy
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 How to Use

1. **Define Constraints:** Select the number of variables (2, 3, or 4). Enter your logic requirements using the K-Map grid, the Truth Table editor, or the Boolean parser.
2. **Utilize "Don't Cares":** Click a K-Map cell twice to input an `X`. The algorithm will use these impossible physical states to further optimize your circuit.
3. **Solve & Analyze:** Click **Solve Grid**. The application will display the optimized equations and calculate your literal efficiency reduction.
4. **View Circuit:** Click any of the "View Circuit" buttons (SOP, POS, NAND, NOR) to open the schematic rendering window and view the generated ANSI logic gate diagram.

## 🏗️ Technical Architecture

*   **Model-View-Controller (MVC) Pattern:** The application distinctly separates the `CustomTkinter` UI views from the `SymPy` math models, coordinated by a central `KMapSolverApp` class.
*   **Dynamic Font & Coordinate Scaling:** The circuit rendering engine features dynamic scaling, automatically adjusting wire spacing and font sizes to prevent overlapping when rendering complex 4-variable, 5-input gates.

## 🤝 Contributors

*   **[Your Name / Team Name]** - *Lead Developer & Architect*

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
```
