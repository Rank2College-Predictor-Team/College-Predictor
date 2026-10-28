RANK2COLLEGE - DARK MODE UPDATE

What changed:
- Added a persistent Light/Dark mode toggle in the navbar.
- Theme preference is saved in localStorage and restored on reload.
- Dark mode covers home, predictor, results, filters, searchable dropdowns, cards, pagination, legal pages and footer.
- Buttons keep readable contrast in both themes.
- Searchable dropdowns use matching dark surfaces and readable search/options.
- Theme is applied before page paint to reduce light-mode flash.

How to run:
1. Open this folder in VS Code.
2. Install dependencies: py -m pip install -r requirements.txt
3. Run: py app.py
4. Open http://127.0.0.1:5000/

Use the Dark/Light button in the navbar. The selection persists between pages and browser reloads.
