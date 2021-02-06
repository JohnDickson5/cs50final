from cs50 import SQL
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, redirect, render_template, request

ALLOWED_EXTENSIONS = set(['csv'])

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


# Make sure that the submitted file is a csv file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getData(uri):

    # Returns all the data for a given wikidata uri
    sparql.setQuery(f"""PREFIX entity: <http://www.wikidata.org/entity/>

                        SELECT ?propNumber ?propLabel ?val
                        WHERE
                        {{
                        	hint:Query hint:optimizer 'None' .
                        	{{	BIND(entity:{uri} AS ?valUrl) .
                        		BIND("N/A" AS ?propUrl ) .
                        		BIND("Name"@en AS ?propLabel ) .
                              entity:{uri} rdfs:label ?val .

                                FILTER (LANG(?val) = "en")
                        	}}
                            UNION
                            {{   BIND(entity:{uri} AS ?valUrl) .

                                BIND("AltLabel"@en AS ?propLabel ) .
                                optional{{entity:{uri} skos:altLabel ?val}}.
                                FILTER (LANG(?val) = "en")
                            }}
                            UNION
                            {{   BIND(entity:{uri} AS ?valUrl) .

                                BIND("Description"@en AS ?propLabel ) .
                                optional{{entity:{uri} schema:description ?val}}.
                                FILTER (LANG(?val) = "en")
                            }}
                          	UNION
                        	{{	entity:{uri} ?propUrl ?valUrl .
                        		?property ?ref ?propUrl .
                        		?property rdf:type wikibase:Property .
                        		?property rdfs:label ?propLabel.
                             	FILTER (lang(?propLabel) = 'en' )
                                filter  isliteral(?valUrl)
                                BIND(?valUrl AS ?val)
                        	}}
                        	UNION
                        	{{	entity:{uri} ?propUrl ?valUrl .
                        		?property ?ref ?propUrl .
                        		?property rdf:type wikibase:Property .
                        		?property rdfs:label ?propLabel.
                             	FILTER (lang(?propLabel) = 'en' )
                                filter  isIRI(?valUrl)
                                ?valUrl rdfs:label ?valLabel
                        		FILTER (LANG(?valLabel) = "en")
                                 BIND(CONCAT(?valLabel) AS ?val)
                        	}}
                                BIND( SUBSTR(str(?propUrl),38, 250) AS ?propNumber)
                        }}
                        ORDER BY xsd:integer(?propNumber)""")

    sparql.setReturnFormat(JSON)

    return sparql.query().convert()


def editDB(InstanceOf, uri, results):
    # Insert the uri into the appropriate table
    db.execute("INSERT INTO :table (id) VALUES (:uri)", table=InstanceOf, uri=uri)

    # Iterate through the properties, finding the datatype
    for result in results["results"]["bindings"]:
        myType = typify(result)
        label=result['propLabel']['value']
        # If the type is known, add a column for the property with the appropriate SQL type
        if 'myType' != "Unknown":
            try:
                db.execute("ALTER TABLE :table ADD COLUMN :column :myType;",
                            table=InstanceOf, column=label, myType=myType)
            # If the property column already exists, ignore the error
            except:
                pass
        else:
            # Print unknown datatypes
            print(f"Unknown datatype: {result['val']['datatype'][33:]}")

        # If the data contains a value for a property and the column in the database contains a null
        # value, add the value
        db.execute(f'UPDATE :table SET "{label}" = :value WHERE id = :id AND "{label}" IS NULL',
                    table=InstanceOf, value=result['val']['value'], id=uri)

    return True


def typify(binding):

    if 'datatype' in binding['val']:
        datatype = binding['val']['datatype'][33:]
        switcher = {
            'dateTime': "datetime",
            'decimal': "numeric(16,2)"
        }
        return switcher.get(datatype, "Unknown")
    else:
        return "varchar(255)"

def queryURI(InstanceOf, NameTitle):
        # Retrieves a uri based of the supplied category and term

        sparql.setQuery(f"""SELECT DISTINCT ?item WHERE {{
                          ?item (wdt:P31/wdt:P279*) wd:{InstanceOf}.
                          ?item rdfs:label ?itemLabel.
                          FILTER (strEnds(?itemLabel,"{NameTitle}"))
                          FILTER (strStarts(?itemLabel, "{NameTitle}"))
                        }}
                        LIMIT 1""")

        sparql.setReturnFormat(JSON)

        return sparql.query().convert()