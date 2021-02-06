You should see the following within the project submission:
1. A folder named templates, containing the following html files: error, index, layout, query, rest,
and stats.
2. The Python files application.py and helpers.py
3. data.db
4. The markdown files DESIGN and README (which you’re reading now)
5. A text file named requirements.txt
6. An named instance containing an empty folder named CSVuploads.

In order to make sure you have the required modules installed, run:
pip install -r requirements.txt

Serve the directory using flask, and open the address that it provides. The index page will present
two option buttons, Single Query and List Query. Select Single Query if you want to look up a single
wikidata entry and List Query if you have a csv file listing things you want to look up. Wikidata is
a bit fickle, so in either case you will have to make sure that your text is capitalized in the
appropriate way (i.e., first letters capitalized for Humans, title-case for Books or Movies, etc.).
In order to get the best result without asking the user to pick between possible intended results
(which would bring a list query to a standstill), the SPARQL query takes the first entry containing
a label ending in AND a label beginning with the entered search string (ideally, this is one and the
same label. Accepting any label in the wikidata entry with these qualities allows for retrieval of
things known by different names or titles.

In order to make the application flexible enough to accommodate the different types, the csv file
can only contain names or titles, one to a row. Once you have entered text or uploaded a file, click
look up. If you performed a single query, you will see the returned JSON data presented as a table,
with properties in the left column and the value on the right. If you performed a list query, you
will be redirected to a page to wait act while the back-end is iterating through the list. Wait a
while there (if your list was 3 items or fewer, you might be able to get away with just clicking
through immediately, but I wouldn’t risk it). This will bring you to a page that presents a table
showing the resulting queries, with the properties on the far left.