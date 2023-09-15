import json
from collections import defaultdict

with open("editions.json", "r") as f:
    data = json.load(f)


nw_data = {
    "attributes": {
        "name": "The Dig-Ed-Cat Network-Graph",
        "description": "A network of Digital Editions, their PIs, related institutions and locations",
    },
    "options": {"type": "undirected", "multi": True, "allowSelfLoops": True},
    "nodes": [],
    "edges": [],
}

persons = defaultdict(list)
places = defaultdict(list)
countries = defaultdict(list)
orgs = defaultdict(dict)

for x in data:
    edition_id = f'edition__{x["id"]}'
    edition_node = {
        "key": edition_id,
        "attributes": {},
    }
    edition_node["attributes"]["label"] = x["edition-name"]
    edition_node["attributes"]["type"] = "Edition"
    nw_data["nodes"].append(edition_node)
    for org in x["institution-s"]:
        org_id = f"org__{org['id']}"
        org_node = {
            "key": org_id,
            "attributes": {"type": "Edition-Institution-Relation"},
        }
        org_node["attributes"]["label"] = org["institution-name"]
        org_node["attributes"]["type"] = "Institution"
        orgs[org_id] = org_node
        edge = {"key": f"{edition_id}-{org_id}", "source": edition_id, "target": org_id}
        nw_data["edges"].append(edge)

        # place
        place_id = org["located-at"]
        place = {"key": place_id, "attributes": {"label": place_id, "type": "City"}}
        places[place_id] = place
        edge = {
            "key": f"{place_id}-{org_id}",
            "source": place_id,
            "target": org_id,
            "attributes": {"type": "Place-Institution-Relation"},
        }
        nw_data["edges"].append(edge)

        # country
        country_id = org["part-of"]
        country = {
            "key": country_id,
            "attributes": {"label": country_id, "type": "Country"},
        }
        countries[country_id] = country
        edge = {
            "key": f"{place_id}-{country_id}",
            "source": place_id,
            "target": country_id,
            "attributes": {"type": "Place-Country-Relation"},
        }
        nw_data["edges"].append(edge)

        # persons
        for p in x["manager-or-editor"]:
            person = {"key": p, "attributes": {"label": p, "type": "Person"}}
            persons[p] = person
            edge = {
                "key": f"{p}-{edition_id}",
                "source": p,
                "target": edition_id,
                "attributes": {"type": "Person-Edition-Relation"},
            }
            nw_data["edges"].append(edge)


for x in orgs.items():
    nw_data["nodes"].append(x[1])
for x in places.items():
    nw_data["nodes"].append(x[1])
for x in countries.items():
    nw_data["nodes"].append(x[1])
for x in persons.items():
    nw_data["nodes"].append(x[1])

with open("network.json", "w") as f:
    json.dump(nw_data, f, ensure_ascii=False, indent=2)
