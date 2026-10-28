RANK2COLLEGE - START HERE

1. Open this folder in VS Code: AKTU College Predictor
2. Open a NEW terminal in this exact folder (the folder containing app.py).
3. Install dependencies:
   py -m pip install -r requirements.txt
4. Start:
   py app.py
5. Open:
   http://127.0.0.1:5000/

IMPORTANT
- Do NOT run the app.py inside the "Codex Project" subfolder for this version.
- The canonical app is the app.py beside templates/, static/, data/ and utils/.
- The UI CSS has both a normal static file and an inline fallback.
- If an older Flask process is running, stop it with Ctrl+C before starting this copy.
- Hard refresh Chrome with Ctrl+Shift+R after replacing the project.

Features included:
- Round, college, branch and subcategory filters
- 20 results per page with pagination
- Responsive result cards with long-name overflow protection
- Redesigned homepage, results page, legal pages and footer
