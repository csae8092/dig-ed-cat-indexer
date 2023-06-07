""" some helper functions """
import typesense


def make_schema(record, ts_schema_name, mandatory_fields, no_facet_field):
    TS_SCHEMA = {"name": ts_schema_name, "enable_nested_fields": True, "fields": []}
    for key, value in record.items():
        if key in mandatory_fields:
            TS_SCHEMA["fields"].append({"name": key, "type": "string"})
        elif key in no_facet_field:
            TS_SCHEMA["fields"].append(
                {"name": key, "type": "string", "facet": False, "optional": True}
            )
        elif isinstance(value, list):
            if isinstance(value[0], dict):
                TS_SCHEMA["fields"].append(
                    {"name": key, "type": "object[]", "facet": True, "optional": True}
                )
            else:
                TS_SCHEMA["fields"].append(
                    {"name": key, "type": "string[]", "facet": True, "optional": True}
                )
        else:
            TS_SCHEMA["fields"].append(
                {"name": key, "type": "string", "facet": True, "optional": True}
            )
    return TS_SCHEMA


def delete_and_create_schema(ts_client, ts_schema_name, ts_schema):
    try:
        ts_client.collections[ts_schema_name].delete()
    except typesense.api_call.ObjectNotFound:
        pass
    created = ts_client.collections.create(ts_schema)
    return created
