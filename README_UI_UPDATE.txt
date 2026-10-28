RANK2COLLEGE UI UPDATE

Added:
1. Searchable dropdowns on the results page for Round, College, Branch and Subcategory.
2. Long college lists are now searchable and scrollable instead of opening a huge native browser select.
3. Dark / Light mode toggle in the navbar.
4. Dark mode preference is saved in the browser using localStorage.
5. Dark mode covers homepage, predictor form, results, cards, filters, pagination, legal pages and footer.
6. Existing filters and pagination remain form-compatible; selecting an option updates the original hidden select so GET parameters continue to work.

Run:
  py -m pip install -r requirements.txt
  py app.py

Open:
  http://127.0.0.1:5000/

If Chrome shows an older version, hard refresh with Ctrl+Shift+R.
