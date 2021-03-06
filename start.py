from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS, RDF, RDFS
from rdflib.tools import rdf2dot
import uuid
from graphviz import Digraph
from namespaces import apply_namespaces, get_namespace
from crmviz.visualise import visualise_graph
from pandas_ods_reader import read_ods
import yaml

graph = Graph() # graph for the dataset
docgraph = Graph() # graph for the documentation drawing

# add namespaces
graph = apply_namespaces(graph)
docgraph = apply_namespaces(docgraph)

# get the ones we need here
URO = get_namespace(graph, 'uro')
CRM = get_namespace(graph, 'crm')

# deal with thesaurus concepts
# types and materials
# read types and materials
types = read_ods("unruly-objects-statements.ods", "types")
for type in types.iloc:
    if type["local type uri"] is not None and type["local type uri"] != "#N/A":
        #md = '---\nlayout: type\nclasscolour: FAB565\n' # prepare the markdown for Jekyll
        yar = {"layout":"type","classcolour":"FAB565"} #prepare the YAML array to dump at the top of the markdown file
        localtypeuri = URIRef(URO[type["local type uri"]])
        # explaining this: URIRef(URO[type["local type uri"]])
        # type["local type uri"] gives the local uri without the base url as shown on the spreadsheet
        # URO[type["local type uri"]] gives the uri with the base url
        # URIRef(URO[type["local type uri"]]) makes it into a URI object for rdflib
        #md += 'uri: ' + str(localtypeuri) + '\n'
        yar["uri"] = str(localtypeuri)
        if type["CRM class"] == "E55":
            graph.add((localtypeuri, RDF.type, CRM["E55_Type"]))
            #md += 'crmtype: E55 Type\n'
            yar["crmtype"] = "E55 Type"
        elif type["CRM class"] == "E57":
            graph.add((localtypeuri, RDF.type, CRM["E57_Material"]))
            #md += 'crmtype: E57 Material\n'
            yar["crmtype"] = "E57 Material"
        graph.add((localtypeuri, SKOS.prefLabel, Literal(type["local label"], lang="en")))
        graph.add((localtypeuri, RDFS.label, Literal(type["local label"], lang="en")))
        #md += 'locallabel: ' + type["local label"] + '\n'
        yar["locallabel"] = type["local label"]
        if type["global type uri"] is not None and type["global type uri"] != "#N/A":
            globaltypeuri = URIRef(URO[type["global type uri"]])
            graph.add((localtypeuri, SKOS.exactMatch, globaltypeuri))
            #md += 'globaluri: ' + str(globaltypeuri) + '\n'
            yar["globaluri"] = str(globaltypeuri)
            #md += 'globallabel: ' + type["global label"] + '\n'
            yar["globallabel"] = type["global label"]
        md = '---\n'
        md += yaml.dump(yar)
        md += '---\n'
        # writing the file for jekyll website
        with open("docs/_types/" + type["local type uri"].replace("/", "-") + ".md", "w") as f:
            f.write(md)

# things
# read things
things = read_ods("unruly-objects-statements.ods", "things")
for thing in things.iloc:
    if thing["thing uri"] is not None and thing["thing uri"] != "#N/A":
        #md = '---\nlayout: thing\nclasscolour: E1BA9C\n'  # prepare the markdown for Jekyll
        yar = {"layout":"thing","classcolour":"E1BA9C"}
        thinguri = URIRef(URO[thing["thing uri"]])
        #md += 'uri: ' + str(thinguri) + '\n'
        yar["uri"] = str(thinguri)
        if thing["CRM class"] == "E22":
            graph.add((thinguri, RDF.type, CRM["E22_Man-Made_Object"]))
            #md += 'crmtype: E22 Human-Made Object\n'
            yar["crmtype"] = "E22 Human-Made Object"
        elif thing["CRM class"] == "E25":
            graph.add((thinguri, RDF.type, CRM["E25_Man-Made_Feature"]))
            #md += 'crmtype: E25 Human-Made Feature\n'
            yar["crmtype"] = "E25 Human-Made Feature"
        elif thing["CRM class"] == "E20":
            graph.add((thinguri, RDF.type, CRM["E20_Biological_Object"]))
            #md += 'crmtype: E20 Biological Object\n'
            yar["crmtype"] = "E20 Biological Object"
        graph.add((thinguri, SKOS.prefLabel, Literal(thing["thing label"], lang="en")))
        graph.add((thinguri, RDFS.label, Literal(thing["thing label"], lang="en")))
        #md += 'thinglabel: ' + thing["thing label"] + '\n'
        yar["thinglabel"] = thing["thing label"]
        # we have multiple types, materials and dimensions for objects therefore we need arrays before adding to the dictionary
        yartypes = []
        yarmaterials = []
        yardimensions = []
        for column in things:
            if column.startswith("part of"): #using the function starts with instead of == because panda automatically adds a ".#" to the labels for repeating fields
                if thing[column] is not None and thing[column] != "#N/A":
                    if thing["CRM class"] == "E22" or thing["CRM class"] == "E20":
                        graph.add((URIRef(URO[thing[column]]), CRM["P46_is_composed_of"], thinguri)) #URIRef(URO[thing["part of"]]) gives the URI of the parent
                        #md += 'composedof: ' + str(URO[thing[column]]) + '\n'
                        yar["composedof"] = str(URO[thing[column]])
                    elif thing["CRM class"] == "E25" or thing["CRM class"] == "E26":
                        graph.add((URIRef(URO[thing[column]]), CRM["P56_bears_feature"], thinguri)) #URIRef(URO[thing["part of"]]) gives the URI of the parent
                        #md += 'bearsfeature: ' + str(URO[thing[column]]) + '\n'
                        yar["bearsfeature"] = str(URO[thing[column]])
            elif column.startswith("type uri"):
                if thing[column] is not None and thing[column] != "#N/A":
                    graph.add((thinguri, CRM["P2_has_type"], URIRef(URO[thing[column]])))
                    #md += 'type: ' + str(URO[thing[column]]) + '\n'
                    yartypes.append(str(URO[thing[column]]))
            elif column.startswith("material uri"):
                if thing[column] is not None and thing[column] != "#N/A":
                    graph.add((thinguri, CRM["P45_consists_of"], URIRef(URO[thing[column]])))
                    #md += 'material: ' + str(URO[thing[column]]) + '\n'
                    yarmaterials.append(str(URO[thing[column]]))
            elif column.startswith("dimension uri"):
                if thing[column] is not None and thing[column] != "#N/A":
                    graph.add((thinguri, CRM["P43_has_dimension"], URIRef(URO[thing[column]])))
                    #md += 'dimension: ' + str(URO[thing[column]]) + '\n'
                    yardimensions.append(str(URO[thing[column]]))
        # add arrays to the dictionary
        if len(yartypes) > 0:
            yar["type"] = yartypes
        if len(yarmaterials) > 0:
            yar["material"] = yarmaterials
        if len(yardimensions) > 0:
            yar["dimension"] = yardimensions
        # prepare the markdown file
        md = '---\n'
        md += yaml.dump(yar)
        md += '---\n'
        # writing the file for jekyll website
        with open("docs/_things/" + thing["thing uri"].replace("/", "-") + ".md", "w") as f:
            f.write(md)
    #things = things.values.tolist()

# dimensions
# read dimensions
dimensions = read_ods("unruly-objects-statements.ods", "dimensions")
for dimension in dimensions.iloc:
    #md = '---\nlayout: dimension\nclasscolour: FFF\n'  # prepare the markdown for Jekyll
    yar = {"layout":"dimension","classcolour":"FFF"}
    dimensionuri = URIRef(URO[dimension["dimension uri"]])
    #md += 'uri: ' + str(dimensionuri) + '\n'
    yar["uri"] = str(dimensionuri)
    graph.add((dimensionuri, RDF.type, CRM["E54_Dimension"]))
    #md += 'crmtype: E54 Dimension\n'
    yar["crmtype"] = "E54 Dimension"
    graph.add((dimensionuri, SKOS.prefLabel, Literal(dimension["dimension label"], lang="en")))
    graph.add((dimensionuri, RDFS.label, Literal(dimension["dimension label"], lang="en")))
    #md += 'dimensionlabel: ' + dimension["dimension label"] + '\n'
    yar["dimensionlabel"] = dimension["dimension label"]
    for column in dimensions:
        if column=="type uri":
            if dimension[column] is not None and dimension[column] != "#N/A":
                graph.add((dimensionuri, CRM["P2_has_type"], URIRef(URO[dimension["type uri"]])))
                #md += 'type: ' + str(URO[dimension["type uri"]]) + '\n'
                yar["type"] = str(URO[dimension[column]])
        elif column=="value":
            if dimension[column] is not None and dimension[column] != "#N/A":
                graph.add((dimensionuri, CRM["P90_has_value"], Literal(dimension[column])))
                #md += 'value: ' + str(dimension[column]) + '\n'
                yar["value"] = str(dimension[column])
        elif column=="unit uri":
            if dimension[column] is not None and dimension[column] != "#N/A":
                graph.add((dimensionuri, CRM["P91_has_unit"], URIRef(URO[dimension["unit uri"]])))
                #md += 'unit: ' + str(URO[dimension["unit uri"]]) + '\n'
                yar["unit"] = str(URO[dimension[column]])
    md = '---\n'
    md += yaml.dump(yar)
    md += '---\n'
    # writing the file for jekyll website
    with open("docs/_dimensions/" + dimension["dimension uri"].replace("/", "-") + ".md", "w") as f:
        f.write(md)

# documentation drawing
dot = visualise_graph(graph, 'Unruly objects graph',"")
dot.render('unruly-objects.gv',format='svg')

# serialise the graph
graph.serialize(destination='unruly-objects.ttl', format='turtle', encoding="utf-8")


# # production events
#
# cursor.execute("SELECT mss.msuuid, mss.cataloguename, pms.msid, pms.yesnonk FROM MSs mss INNER JOIN `1_2_PageMarkers` pms on mss.id=pms.msid")
# rows = cursor.fetchall()
#
# for row in rows:
#     msuuid = URIRef(row["msuuid"], str(URO))
#     if row["yesnonk"] == "no":
#         graph.add((msuuid, CRM["NTP46_is_not_composed_of_physical_thing_of_type"], URIRef("http://w3id.org/lob/concept/5423")))
#
#     if row["msid"] == doci1:
#         docgraph1.add((URIRef("http://w3id.org/lob/concept/5423"), RDF.type, CRM["E55_Type"]))
#         docgraph1.add((URIRef("http://w3id.org/lob/concept/5423"), SKOS.prefLabel, Literal("leaf markers", lang="en")))
#         docgraph1.add((msuuid, CRM["NTP46_is_not_composed_of_physical_thing_of_type"], URIRef("http://w3id.org/lob/concept/5423")))
#         docgraph1.add((msuuid, RDF.type, CRM["E22_Man-Made_Object"]))
#         docgraph1.add((msuuid, RDFS.label, Literal(row["cataloguename"], lang="en")))
#     if row["msid"] == doci2:
#         docgraph2.add((msuuid, RDF.type, CRM["E22_Man-Made_Object"]))
#         docgraph2.add((msuuid, RDFS.label, Literal(row["cataloguename"], lang="en")))
#     if row["msid"] == doci3:
#         docgraph3.add((msuuid, RDF.type, CRM["E22_Man-Made_Object"]))
#         docgraph3.add((msuuid, RDFS.label, Literal(row["cataloguename"], lang="en")))
#
# # Pagemarkers
# cursor.execute("SELECT mss.msuuid, mss.cataloguename, pm.msid, pm.id, pm.uuid, pm.type, pm.attachment, pm.partadditionuuid, pm.material FROM PageMarkers pm INNER JOIN MSs mss ON pm.msid=mss.id")
# rows = cursor.fetchall()
#
# for row in rows:
#     shelfmark = row["cataloguename"]
#     msuuid = URIRef(row["msuuid"], str(URO))
#     # pagemarker series attachment, type, material
#     if row["uuid"] is None:
#         newuuid = str(uuid.uuid4())
#         pagemarkeruuid = URIRef(newuuid, str(URO))
#         # update the database
#         sql = "UPDATE PageMarkers SET uuid=%s WHERE id=%s"
#         val = (newuuid, row["id"])
#         cursorupdate.execute(sql, val)
#         mydb.commit()
#     else:
#         pagemarkeruuid = URIRef(row["uuid"], str(URO))
#
#     if row["type"] is not None:
#         if bool(row["type"] == "Folded") | bool(row["type"] == "Folded and knotted") | bool(row["type"] == "Straight") | bool(row["type"] == "Platted") | bool(row["type"] == "Tied") | bool(row["type"] == "Twisted thread") | bool(row["type"] == "Thread"):
#             graph.add((pagemarkeruuid, RDF.type, CRM["E22_Man-Made_Object"])) # page markers of these types are separate things.
#             graph.add((msuuid, CRM["P46_is_composed_of"], pagemarkeruuid))  # book is composed of page markers
#         elif bool(row["type"] == "Wax") | bool(row["type"] == "Painted"):
#             graph.add((pagemarkeruuid, RDF.type, CRM["E25_Man-Made_Feature"]))  # page markers of these types are features, i.e. cannot be removed.
#             graph.add((msuuid, CRM["P56_bears_feature"], pagemarkeruuid))  # book bears feature page markers
#         else:
#             graph.add((pagemarkeruuid, RDF.type, CRM["E24_Physical_Man-Made_Thing"])) # page markers of these types are separate things.
#             graph.add((msuuid, CRM["P46_is_composed_of"], pagemarkeruuid))  # book is composed of page markers
#
#         if row["type"] != "-":
#             if bool(row["type"] == "Folded") | bool(row["type"] == "Folded and knotted"):
#                 pagemarkertypeuuid = URIRef("http://w3id.org/lob/concept/2945")
#             elif row["type"] == "Straight":
#                 pagemarkertypeuuid = URIRef("http://w3id.org/lob/concept/5423")
#             elif bool(row["type"] == "Platted") | bool(row["type"] == "Tied") | bool(row["type"] == "Twisted thread") | bool(row["type"] == "Thread"):
#                 pagemarkertypeuuid = URIRef("http://w3id.org/lob/concept/2944")
#             elif bool(row["type"] == "Wax") | bool(row["type"] == "Painted"):
#                 # TODO: consider a new type of page marker which is a feature
#                 pass
#             graph.add((pagemarkeruuid, CRM["P2_has_type"], pagemarkertypeuuid))
#             graph.add((msuuid, CRM["TP46_is_composed_of_physical_thing_of_type"], pagemarkertypeuuid))
#     else:
#         graph.add((pagemarkeruuid, RDF.type, CRM["E24_Physical_Man-Made_Thing"]))  # not sure what these page markers are
#         graph.add((msuuid, CRM["P46_is_composed_of"], pagemarkeruuid))  # book is composed of page markers
#     graph.add((pagemarkeruuid, RDFS.label, Literal("Page-markers of " + shelfmark, lang="en")))
#
#     if row["attachment"] is not None:
#         if row["partadditionuuid"] is None:
#             newuuid = str(uuid.uuid4())
#             partadditionuuid = URIRef(newuuid, str(URO))
#             # update the database
#             sql = "UPDATE PageMarkers SET partadditionuuid=%s WHERE id=%s"
#             val = (newuuid, row["id"])
#             cursorupdate.execute(sql, val)
#             mydb.commit()
#         else:
#             partadditionuuid = URIRef(row["partadditionuuid"], str(URO))
#         graph.add((partadditionuuid, RDF.type, CRM["E79_Part_Addition"])) # type the part addition event
#         graph.add((partadditionuuid, RDFS.label, Literal("Addition of pagemarkers to " + shelfmark, lang="en"))) # label
#         graph.add((partadditionuuid, CRM["P110_augmented"], msuuid)) # augmented book
#         graph.add((partadditionuuid, CRM["P111_added"], pagemarkeruuid)) # added pagemarker
#
#         if row["attachment"] != "-":
#             if row["attachment"] == "Adhesive":
#                 partadditiontechniqueuuid = URIRef("http://w3id.org/lob/concept/5429")
#             elif row["attachment"] == "Sewn":
#                 partadditiontechniqueuuid = URIRef("http://w3id.org/lob/concept/2362")
#             elif row["attachment"] == "Looped":
#                 partadditiontechniqueuuid = URIRef("http://URO.looped")
#             elif row["attachment"] == "Paint":
#                 partadditiontechniqueuuid = URIRef("http://w3id.org/lob/concept/1476")
#             graph.add((partadditionuuid, CRM["P32_used_general_technique"], partadditiontechniqueuuid))
#
#     if row["material"] is not None and row["material"] != "-":
#         if bool(row["material"] == "Candle wax"):
#             materialuuid = URIRef("http://vocab.getty.edu/aat/300014585")
#         elif row["material"] == "Tanned leather":
#             materialuuid = URIRef("http://w3id.org/lob/concept/1658")
#         elif row["material"] == "Silk":
#             materialuuid = URIRef("http://w3id.org/lob/concept/2468")
#         elif row["material"] == "Textile":
#             materialuuid = URIRef("http://w3id.org/lob/concept/2470")
#         elif row["material"] == "Paper":
#             materialuuid = URIRef("http://w3id.org/lob/concept/1481")
#         elif row["material"] == "Tawed leather":
#             materialuuid = URIRef("http://w3id.org/lob/concept/1197")
#         elif row["material"] == "Parchment":
#             materialuuid = URIRef("http://w3id.org/lob/concept/1485")
#         elif row["material"] == "Natural thread":
#             materialuuid = URIRef("http://w3id.org/lob/concept/2474")
#         elif row["material"] == "Wax":
#             materialuuid = URIRef("http://vocab.getty.edu/aat/300014585")
#         elif row["material"] == "Tinted paper":
#             materialuuid = URIRef("http://w3id.org/lob/concept/3855")
#         elif row["material"] == "Paint":
#             materialuuid = URIRef("http://w3id.org/lob/concept/3165")
#         graph.add((pagemarkeruuid, CRM["P45_consists_of"], materialuuid))
#
#     if row["msid"] == doci2:
#         docgraph2.add((pagemarkeruuid, RDF.type, CRM["E22_Man-Made_Object"]))
#         docgraph2.add((pagemarkeruuid, RDFS.label, Literal("Page-markers of " + shelfmark, lang="en")))
#         docgraph2.add((msuuid, CRM["TP46_is_composed_of_physical_thing_of_type"], pagemarkertypeuuid))
#         docgraph2.add((msuuid, CRM["P46_is_composed_of"], pagemarkeruuid))  # book is composed of page markers
#         docgraph2.add((pagemarkeruuid, CRM["P2_has_type"], pagemarkertypeuuid))
#         docgraph2.add((partadditionuuid, RDF.type, CRM["E79_Part_Addition"]))  # type the part addition event
#         docgraph2.add((partadditionuuid, RDFS.label, Literal("Addition of pagemarkers to " + shelfmark, lang="en")))  # label
#         docgraph2.add((partadditionuuid, CRM["P110_augmented"], msuuid))  # augmented book
#         docgraph2.add((partadditionuuid, CRM["P111_added"], pagemarkeruuid))  # added pagemarker
#         docgraph2.add((partadditionuuid, CRM["P32_used_general_technique"], partadditiontechniqueuuid))
#         docgraph2.add((pagemarkeruuid, CRM["P45_consists_of"], materialuuid))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/2470"), RDF.type, CRM["E57_Material"]))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/2470"), RDFS.label, Literal("textile", lang="en")))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/2945"), RDF.type, CRM["E55_Type"]))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/2945"), SKOS.prefLabel, Literal("leaf tab markers", lang="en")))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/5429"), RDF.type, CRM["E55_Type"]))
#         docgraph2.add((URIRef("http://w3id.org/lob/concept/5429"), RDFS.label, Literal("adhering", lang="en")))
#         docgraph2.add((URIRef("http://vocab.getty.edu/aat/300129361"), RDF.type, CRM["E55_Type"]))
#         docgraph2.add((URIRef("http://vocab.getty.edu/aat/300129361"), RDFS.label, Literal("blue (color)", lang="en")))
#     if row["msid"] == doci3:
#         docgraph3.add((pagemarkeruuid, RDF.type, CRM["E22_Man-Made_Object"]))
#         docgraph3.add((pagemarkeruuid, RDFS.label, Literal("Page-markers of " + shelfmark, lang="en")))
#         docgraph3.add((msuuid, CRM["TP46_is_composed_of_physical_thing_of_type"], pagemarkertypeuuid))
#         docgraph3.add((msuuid, CRM["P46_is_composed_of"], pagemarkeruuid))  # book is composed of page markers
#         docgraph3.add((pagemarkeruuid, CRM["P2_has_type"], pagemarkertypeuuid))
#         docgraph3.add((partadditionuuid, RDF.type, CRM["E79_Part_Addition"]))  # type the part addition event
#         docgraph3.add((partadditionuuid, RDFS.label, Literal("Addition of pagemarkers to " + shelfmark, lang="en")))  # label
#         docgraph3.add((partadditionuuid, CRM["P110_augmented"], msuuid))  # augmented book
#         docgraph3.add((partadditionuuid, CRM["P111_added"], pagemarkeruuid))  # added pagemarker
#         docgraph3.add((partadditionuuid, CRM["P32_used_general_technique"], partadditiontechniqueuuid))
#         docgraph3.add((pagemarkeruuid, CRM["P45_consists_of"], materialuuid))
#         docgraph3.add((URIRef("http://w3id.org/lob/concept/2474"), RDF.type, CRM["E57_Material"]))
#         docgraph3.add((URIRef("http://w3id.org/lob/concept/2474"), RDFS.label, Literal("thread", lang="en")))
#         docgraph3.add((URIRef("http://w3id.org/lob/concept/2944"), RDF.type, CRM["E55_Type"]))
#         docgraph3.add((URIRef("http://w3id.org/lob/concept/2944"), SKOS.prefLabel, Literal("leaf string markers", lang="en")))
#         docgraph3.add((URIRef("http://URO.looped"), RDF.type, CRM["E55_Type"]))
#         docgraph3.add((URIRef("http://URO.looped"), RDFS.label, Literal("looped", lang="en")))
#         docgraph3.add((URIRef("http://vocab.getty.edu/aat/300056130"), RDF.type, CRM["E55_Type"]))
#         docgraph3.add((URIRef("http://vocab.getty.edu/aat/300056130"), RDFS.label, Literal("color (perceived attribute)", lang="en")))
#
# # PageMarkers colour
# cursor.execute("SELECT mss.id AS msid, pm.uuid, pmc.pagemarker, pmc.pagemarkercolour FROM PageMarkersColour pmc LEFT JOIN PageMarkers pm on pm.id=pmc.pagemarker INNER JOIN MSs mss ON pm.msid=mss.id")
# rows = cursor.fetchall()
# for row in rows:
#     pagemarkeruuid = URIRef(row["uuid"], str(URO))
#     if row["pagemarkercolour"] is not None and row["pagemarkercolour"] != "-" and row["pagemarkercolour"] != "NK":
#         if row["pagemarkercolour"] == "Natural":
#             graph.add((pagemarkeruuid, CRM["NTP56_does_not_bear_feature_of_type"], URIRef("http://vocab.getty.edu/aat/300056130"))) # pagemarker does not have colour
#         else:
#             if row["pagemarkercolour"] == "Blue":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300129361")
#             elif row["pagemarkercolour"] == "Brown":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300127490")
#             elif row["pagemarkercolour"] == "Gold" or row["pagemarkercolour"] == "Gilded" or row["pagemarkercolour"] == "Gilt":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300311191")
#             elif row["pagemarkercolour"] == "Dark brown":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300127526")
#             elif row["pagemarkercolour"] == "Deep red":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300126272")
#             elif row["pagemarkercolour"] == "Red":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300126225")
#             elif row["pagemarkercolour"] == "Light brown":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300127503")
#             elif row["pagemarkercolour"] == "Yellow":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300127794")
#             elif row["pagemarkercolour"] == "Green":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300128438")
#             elif row["pagemarkercolour"] == "Deep blue":
#                 colouruuid = URIRef("http://vocab.getty.edu/aat/300129394")
#             graph.add((pagemarkeruuid, CRM["P56_bears_feature"], colouruuid))
#
#     if row["msid"] == doci2:
#         docgraph2.add((pagemarkeruuid, CRM["P56_bears_feature"], colouruuid))
#     if row["msid"] == doci3:
#         docgraph3.add((pagemarkeruuid, CRM["NTP56_does_not_bear_feature_of_type"], URIRef("http://vocab.getty.edu/aat/300056130")))  # pagemarker does not have colour
#
# # Pagemarker locations
# cursor.execute("SELECT mss.id AS msid, pm.uuid AS pagemarkersetuuid, pml.id, pml.uuid AS pagemarkersubsetuuid, pml.pagemarker, pml.pagemarkerlocation, pml.locationno FROM PageMarkersLocation pml LEFT JOIN PageMarkers pm ON pm.id=pml.pagemarker INNER JOIN MSs mss ON mss.id=pm.msid")
# rows = cursor.fetchall()
#
# for row in rows:
#     pagemarkersetuuid = URIRef(row["pagemarkersetuuid"], str(URO)) # we should have a uuid for every set of pagemerkers by now
#     pagemarkersetlabel = graph.preferredLabel(pagemarkersetuuid, lang="en") # get the pagemarkers set label
#     # find the total number of pagemarkers in this set
#     cursor.execute("SELECT SUM(locationno) FROM `PageMarkersLocation` WHERE pagemarker=" + str(row["pagemarker"]))
#     pagemarkersettotal = cursor.fetchall()
#     # add the number of parts for it
#     graph.add((pagemarkersetuuid, CRM["P57_has_number_of_parts"], Literal(pagemarkersettotal[0]["SUM(locationno)"])))
#     # pagemarker subsets
#     if row["pagemarkersubsetuuid"] is None:
#         newuuid = str(uuid.uuid4())
#         pagemarkersubsetuuid = URIRef(newuuid, str(URO))
#         # update the database
#         sql = "UPDATE PageMarkersLocation SET uuid=%s WHERE id=%s"
#         val = (newuuid, row["id"])
#         cursorupdate.execute(sql, val)
#         mydb.commit()
#     else:
#         pagemarkersubsetuuid = URIRef(row["pagemarkersubsetuuid"], str(URO))
#     pmstype = graph.value(pagemarkersetuuid, RDF.type) # find the rdf type of the pagemarker set, we assume that the subset is of the same type
#     graph.add((pagemarkersubsetuuid, RDF.type, pmstype))
#     graph.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' on " + row["pagemarkerlocation"], lang="en")))
#     graph.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#     graph.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["locationno"]))) # specify the pagemarker subset in the specific location
#     if row["pagemarkerlocation"] is not None:
#         if row["pagemarkerlocation"] == "Foredge":
#             # TODO: query the graph to get the URI of the textblock foredge place
#             pass
#         elif row["pagemarkerlocation"] == "Head":
#             # TODO: query the graph to get the URI of the textblock foredge place
#             pass
#         elif row["pagemarkerlocation"] == "Tail":
#             # TODO: query the graph to get the URI of the textblock foredge place
#             pass
#         # graph.add((pagemarkersubsetuuid, CRM["P53_has_former_or_current_location"], *place*))
#
#     if row["msid"] == doci2:
#         docgraph2.add((pagemarkersubsetuuid, RDF.type, pmstype))
#         docgraph2.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' on " + row["pagemarkerlocation"], lang="en")))
#         docgraph2.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#         docgraph2.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["locationno"])))
#     if row["msid"] == doci3:
#         docgraph3.add((pagemarkersubsetuuid, RDF.type, pmstype))
#         docgraph3.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' on " + row["pagemarkerlocation"], lang="en")))
#         docgraph3.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#         docgraph3.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["locationno"])))
#
# # Pagemarker conditions
# cursor.execute("SELECT mss.id AS msid, pm.uuid AS pagemarkersetuuid, pmc.id, pmc.uuid AS pagemarkersubsetuuid, pmc.pagemarker, pmc.condition, pmc.conditionuuid, pmc.conditionno FROM PageMarkersCondition pmc INNER JOIN PageMarkers pm ON pm.id=pmc.pagemarker INNER JOIN MSs mss ON mss.id=pm.msid")
# rows = cursor.fetchall()
#
# for row in rows:
#     pagemarkersetuuid = URIRef(row["pagemarkersetuuid"], str(URO)) # we should have a uuid for every set of pagemerkers by now
#     pagemarkersetlabel = graph.preferredLabel(pagemarkersetuuid, lang="en") # get the pagemarkers set label
#     # pagemarker subsets
#     if row["pagemarkersubsetuuid"] is None:
#         newuuid = str(uuid.uuid4())
#         pagemarkersubsetuuid = URIRef(newuuid, str(URO))
#         # update the database
#         sql = "UPDATE PageMarkersCondition SET uuid=%s WHERE id=%s"
#         val = (newuuid, row["id"])
#         cursorupdate.execute(sql, val)
#         mydb.commit()
#     else:
#         pagemarkersubsetuuid = URIRef(row["pagemarkersubsetuuid"], str(URO))
#     pmstype = graph.value(pagemarkersetuuid, RDF.type) # find the rdf type of the pagemarker set, we assume that the subset is of the same type
#     graph.add((pagemarkersubsetuuid, RDF.type, pmstype))
#     graph.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' with condition " + row["condition"], lang="en")))
#     graph.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#     graph.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["conditionno"])))  # specify the pagemarker subset in the specific location
#     # subset condition
#     if row["conditionuuid"] is None:
#         newuuid = str(uuid.uuid4())
#         conditionuuid = URIRef(newuuid, str(URO))
#         # update the database
#         sql = "UPDATE PageMarkersCondition SET conditionuuid=%s WHERE id=%s"
#         val = (newuuid, row["id"])
#         cursorupdate.execute(sql, val)
#         mydb.commit()
#     else:
#         conditionuuid = URIRef(row["conditionuuid"], str(URO))
#     graph.add((conditionuuid, RDF.type, CRM["E3_Condition_State"]))
#     graph.add((conditionuuid, RDFS.label, Literal("Condition of subset of " + str(pagemarkersetlabel[0][1]), lang="en")))
#     graph.add((pagemarkersubsetuuid, CRM["P44_has_condition"], conditionuuid)) # subset of pagemarkers have a condition
#     if row["condition"] is not None:
#         if row["condition"] == "Sound":
#             conditiontypeuuid = URIRef("http://URO.sound")
#         elif row["condition"] == "Detached":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300131111")
#         elif row["condition"] == "Broken off":
#             conditiontypeuuid = URIRef("http://URO.brokenoff")
#         elif row["condition"] == "Worn":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300219449")
#         elif row["condition"] == "Stained":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300379497")
#         elif row["condition"] == "Missing":
#             conditiontypeuuid = URIRef("http://URO.missing")
#         elif row["condition"] == "Trimmed foredge":
#             conditiontypeuuid = URIRef("http://URO.trimmedforedge")
#         elif row["condition"] == "Dangling":
#             conditiontypeuuid = URIRef("http://URO.dangling")
#         elif row["condition"] == "Adhesive remains only":
#             conditiontypeuuid = URIRef("http://URO.missing")
#             graph.add((conditionuuid, CRM["P3_has_note"], Literal(row["condition"], lang="en")))
#         elif row["condition"] == "Rodent":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300380188")
#         elif row["condition"] == "Insect damage":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300230031")
#         elif row["condition"] == "Abraded in the fold":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300053077")
#             graph.add((conditionuuid, CRM["P3_has_note"], Literal(row["condition"], lang="en")))
#         elif row["condition"] == "Worn at foredge":
#             conditiontypeuuid = URIRef("http://vocab.getty.edu/aat/300219449")
#             graph.add((conditionuuid, CRM["P3_has_note"], Literal(row["condition"], lang="en")))
#         elif row["condition"] == "Dirty":
#             conditiontypeuuid = URIRef("http://URO.dirty")
#         graph.add((conditionuuid, CRM["P2_has_type"], conditiontypeuuid))
#
#     if row["msid"] == doci2:
#         docgraph2.add((pagemarkersubsetuuid, RDF.type, pmstype))
#         docgraph2.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' with condition " + row["condition"], lang="en")))
#         docgraph2.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#         docgraph2.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["conditionno"])))  # specify the pagemarker subset in the specific location
#         docgraph2.add((conditionuuid, RDF.type, CRM["E3_Condition_State"]))
#         docgraph2.add((conditionuuid, RDFS.label, Literal("Condition of subset of " + str(pagemarkersetlabel[0][1]), lang="en")))
#         docgraph2.add((pagemarkersubsetuuid, CRM["P44_has_condition"], conditionuuid))  # subset of pagemarkers have a condition
#         docgraph2.add((conditionuuid, CRM["P2_has_type"], conditiontypeuuid))
#         docgraph2.add((URIRef("http://URO.sound"), RDF.type, CRM["E55_Type"]))
#         docgraph2.add((URIRef("http://URO.sound"), RDFS.label, Literal("sound", lang="en")))
#     if row["msid"] == doci3:
#         docgraph3.add((pagemarkersubsetuuid, RDF.type, pmstype))
#         docgraph3.add((pagemarkersubsetuuid, RDFS.label, Literal("Subset of '" + str(pagemarkersetlabel[0][1]) + "' with condition " + row["condition"], lang="en")))
#         docgraph3.add((pagemarkersetuuid, CRM["P46_is_composed_of"], pagemarkersubsetuuid))
#         docgraph3.add((pagemarkersubsetuuid, CRM["P57_has_number_of_parts"], Literal(row["conditionno"])))  # specify the pagemarker subset in the specific location
#         docgraph3.add((conditionuuid, RDF.type, CRM["E3_Condition_State"]))
#         docgraph3.add((conditionuuid, RDFS.label, Literal("Condition of subset of " + str(pagemarkersetlabel[0][1]), lang="en")))
#         docgraph3.add((pagemarkersubsetuuid, CRM["P44_has_condition"], conditionuuid))  # subset of pagemarkers have a condition
#         docgraph3.add((conditionuuid, CRM["P2_has_type"], conditiontypeuuid))
#         docgraph3.add((URIRef("http://URO.dangling"), RDF.type, CRM["E55_Type"]))
#         docgraph3.add((URIRef("http://URO.dangling"), RDFS.label, Literal("dangling", lang="en")))