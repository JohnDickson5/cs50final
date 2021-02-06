    The story of “CS50 Final Project: Compare wikidata items from list” is ultimately a story of trying to use as much as possible
from “Finance”, out of a lack in confidence in my ability to learn more than one additional language (SPARQL) while trying to get a
firmer grasp on javascript and SQL. The use of Python I felt quite a bit better about. Basing my project on “Finance” turned out to
be not the best idea. In particular, the use of a relational database failed to take full advantage of the JSON-formatted documents
returned by wikidata, and was a wasteful use of computing resources. Mea culpa.
	Design decisions for application.py:
	index(): The only session information that I save is the category of thing that the user is searching in (i.e., the wikidata
property InstanceOf), in order to retain this information across the multiple pages that a list query ended up requiring. Therefore,
the proper time to clear the session is when a new search is being made.
	queryList(): Here is the heartbreak of my project. I attempted to use threading to have this section of code, which iterates
through the submitted csv file, queries wikidata for the uri, and then uses that uri to pull all of the data associated with that
entry into the SQL database, run in the background while another page was put up, then render a new template with the result when
it was finished. In this way, I hoped to get around a “page unresponsive” error. However, it seems that it is not possible to use
render_template or redirect within a thread. As there is nothing else I wanted it to return, I’ve had it simply return True. I was
never able to figure out another way to do this. I probably should have used Celery instead of threading? I used a time stamp to
identify jobs as it seemed like the easiest way to create a different number every time a job is run.
	retrieve(): Since I couldn’t save a session variable within the queryList() function, I settled on clearing all job data when a
list query is started, and selecting all rows with job data here, right after the list items have had the job time added.
	listQuery(): Most of this is right out of the Flask documentation for file uploads
(http://flask.pocoo.org/docs/1.0/patterns/fileuploads/). My reasoning for storing list category and using threading are described
in index() and queryList() above. I probably should have just stored the raw JSON in a Python dictionary.
	singleQuery(): I separated getData() and editDB() into helper functions because they seemed discrete and I knew I’d need them
again for listQuery().
	Design decisions for helpers.py
	allowed_file(): Once again, this is taken from (http://flask.pocoo.org/docs/1.0/patterns/fileuploads/).
	getData(): This is one of wikidata’s SPARQL query examples,
https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Data_of_Douglas_Adams_(modified_version). I initially
tried to lose the “PREFIX” line and sub in the complete address for the item in the body, but discovered that the slashes in the
address invalidated the SPARQL.
	editDB(): I designed this to be able to add columns “on the fly,” so that it could store any wikidata properties that an item
might contain. I also wanted to preserve datatype information contained in the JSON, so that non-text properties might be compared
in ways appropriate to their type down the line. I hoped that by only updating null values in the database, I might trim some time,
but I don’t think that this happened. Here is where I should have set up a different type of database, or even just stores the raw
JSON in a python dictionary.
	typify(): This enabled columns to be added with the “datetime” or “numeric” data types. This were the only XML datatypes I
encountered in the data I queried, and there were too many to hard code every one if they weren’t going to be in the data.
	queryURI(): This started off as the topmost of wikidata’s SPARQL query examples,
https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats (in acknowledgment of this, I left ‘cats’ as a
category to search in). The filters were based on the answer I got to a post I made on the wikidata “Request a query” page:
https://www.wikidata.org/wiki/Wikidata:Request_a_query#Retrieve_item_URI_by_title_without_knowing_language_of_title. I replaced the
suggested “contains” with “strEnds” to reduce the number of false positives, and added a second filter of “strStarts” to reduce
them even more.
