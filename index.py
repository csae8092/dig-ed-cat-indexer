import json
import pandas as pd
from slugify import slugify

from config import (
    EDITIONS,
    INSTITUTIONS,
    TS_CLIENT,
    TS_SCHEMA_NAME,
    MANDATORY_FIELDS,
    FACET_FIELDS,
    NO_FACET_FIELDS,
)

from utils import (
    make_schema,
    delete_and_create_schema,
)

print("hallo, lets start indexing")

print(f"fetching {EDITIONS}")
df = pd.read_csv(EDITIONS).head(-1)
df = df.astype("str")
df = df.replace(["nan", ""], "not provided")
objects = df.to_dict(orient="records")
labels = {slugify(x): x for x in df.keys()}
df.columns = labels.keys()
editions = df.to_dict(orient="records")


print(f"fetching {INSTITUTIONS}")
df = pd.read_csv(INSTITUTIONS).head(-1)
df = df.astype("str")
df = df.replace(["nan", ""], "not provided")
objects = df.to_dict(orient="records")
labels = {slugify(x): x for x in df.keys()}
df.columns = labels.keys()
orgs = {}
for i, x in enumerate(df.to_dict(orient="records"), start=1):
    orgs[x["institution-name"]] = x
    orgs[x["institution-name"]]["id"] = f"{i}"

editions_full = []
for i, x in enumerate(editions, start=1):
    x["id"] = f"{i}"
    old_orgs = [x.strip() for x in x["institution-s"].split(";")]
    institutions = []
    for org in old_orgs:
        try:
            institutions.append(orgs[org])
        except KeyError:
            continue
    x["institution-s"] = institutions
    for f in FACET_FIELDS:
        try:
            x[f] = [x.strip() for x in x[f].split(";")]
        except AttributeError:
            continue
    editions_full.append(x)

with open("editions.json", "w") as f:
    json.dump(editions_full, f, ensure_ascii=False, indent=4)


print("Typesense Index")
print(f"defining Typesense collection schema with name: {TS_SCHEMA_NAME}")
ts_schema = make_schema(editions[0], "dig-ed-cat", MANDATORY_FIELDS, NO_FACET_FIELDS)
with open("schema.json", "w") as f:
    json.dump(ts_schema, f, ensure_ascii=False, indent=4)

print(f"creating Typesnses Collection with schema {TS_SCHEMA_NAME}")
cur_schema = delete_and_create_schema(TS_CLIENT, TS_SCHEMA_NAME, ts_schema)
print(f"schema created at {cur_schema['created_at']}")
print(f"start to index {len(editions_full)} records")
index = TS_CLIENT.collections[TS_SCHEMA_NAME].documents.import_(
    editions_full, {"action": "create"}
)
print(f"status of index-process: {index[0]}")
