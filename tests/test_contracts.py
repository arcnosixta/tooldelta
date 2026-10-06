import copy
import json
from pathlib import Path
import tempfile
import unittest

from tooldelta.catalog import CatalogError, load_catalog, normalize_catalog
from tooldelta.diff import compare


def tool(schema=None, **extra):
    return {"name": "search", "inputSchema": schema or {"type": "object"}, **extra}


def catalog(schema):
    return [tool(schema)]


class ContractTests(unittest.TestCase):
    def test_catalog_shapes_and_order(self):
        tools = [tool(), {**tool(), "name": "other"}]
        for wrapper in (tools, {"tools": tools}, {"jsonrpc": "2.0", "result": {"tools": tools}}):
            self.assertFalse(compare(wrapper, list(reversed(tools))).changes)
            self.assertEqual(compare(wrapper, tools).old_hash, compare(tools, wrapper).new_hash)

    def test_required_added_input_and_removed_output_break(self):
        base = {"type": "object", "properties": {"q": {"type": "string"}}}
        required = {**base, "required": ["q"]}
        self.assertTrue(compare(catalog(base), catalog(required)).fails())
        self.assertFalse(compare(catalog(required), catalog(base)).fails())
        self.assertTrue(compare([tool(outputSchema=required)], [tool(outputSchema=base)]).fails())
        self.assertFalse(compare([tool(outputSchema=base)], [tool(outputSchema=required)]).fails())

    def test_type_number_integer_direction(self):
        def schema(value):
            return {"type": "object", "properties": {"n": {"type": value}}}
        number, integer = schema("number"), schema("integer")
        self.assertTrue(compare(catalog(number), catalog(integer)).fails())
        self.assertFalse(compare(catalog(integer), catalog(number)).fails())
        self.assertTrue(compare([tool(outputSchema=integer)], [tool(outputSchema=number)]).fails())

    def test_enum_input_narrowing_output_widening(self):
        def schema(values):
            return {"type": "object", "properties": {"mode": {"enum": values}}}
        wide, narrow = schema(["a", "b"]), schema(["a"])
        self.assertTrue(compare(catalog(wide), catalog(narrow)).fails())
        self.assertFalse(compare(catalog(narrow), catalog(wide)).fails())
        self.assertTrue(compare([tool(outputSchema=narrow)], [tool(outputSchema=wide)]).fails())

    def test_nested_array_bounds(self):
        base = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "string", "maxLength": 20}}}}
        new = copy.deepcopy(base)
        new["properties"]["items"]["items"]["maxLength"] = 10
        report = compare(catalog(base), catalog(new))
        self.assertTrue(report.fails())
        self.assertIn("/items/maxLength", report.changes[0].path)

    def test_closed_property_removal(self):
        old = {"type": "object", "properties": {"q": {"type": "string"}}, "additionalProperties": False}
        new = {"type": "object", "additionalProperties": False}
        self.assertTrue(compare(catalog(old), catalog(new)).fails())
        self.assertFalse(compare(catalog(new), catalog(old)).fails())

    def test_added_optional_property_constrains_previous_extras(self):
        old = {"type": "object"}
        new = {"type": "object", "properties": {"q": {"type": "string"}}}
        self.assertTrue(compare(catalog(old), catalog(new)).fails())

    def test_unsupported_even_unchanged(self):
        schema = {"type": "object", "$ref": "https://example.invalid/schema", "properties": {"x": {"oneOf": [{"type": "string"}, {"type": "number"}]}}}
        report = compare(catalog(schema), catalog(schema))
        self.assertEqual(report.counts["review"], 2)
        self.assertFalse(report.fails("breaking"))
        self.assertTrue(report.fails("review"))

    def test_hints_are_review_not_security_verdict(self):
        old = [tool(annotations={"readOnlyHint": True})]
        new = [tool(annotations={"readOnlyHint": False, "destructiveHint": True})]
        report = compare(old, new)
        self.assertEqual(report.counts["review"], 2)
        self.assertFalse(report.fails())
        self.assertTrue(report.fails("review"))

    def test_removal_addition_description_and_output_removal(self):
        self.assertTrue(compare([tool()], []).fails())
        self.assertEqual(compare([], [tool()]).counts["info"], 1)
        self.assertEqual(compare([tool(description="a")], [tool(description="b")]).counts["review"], 1)
        self.assertTrue(compare([tool(outputSchema={"type": "object"})], [tool()]).fails())

    def test_input_not_mutated_and_json_report(self):
        old = [tool()]
        snapshot = copy.deepcopy(old)
        json.dumps(compare(old, old).to_dict())
        self.assertEqual(old, snapshot)


class LoadingTests(unittest.TestCase):
    def test_invalid_catalogs(self):
        bad = [None, {}, {"tools": [] , "nextCursor": "next"}, {"error": {}},
               [tool(), tool()], [tool({"type": "array"})],
               [tool({"type": "object", "required": "q"})],
               [tool({"type": "object", "properties": []})],
               [tool({"type": "object", "properties": {"n": {"minimum": True}}})],
               [tool(annotations={"readOnlyHint": "true"})]]
        for data in bad:
            with self.subTest(data=data), self.assertRaises(CatalogError):
                normalize_catalog(data)

    def test_strict_json_and_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tools.json"
            for raw in ('{"tools": [], "tools": []}', '{"tools": [], "x": NaN}', 'not json'):
                path.write_text(raw, encoding="utf-8")
                with self.assertRaises(CatalogError):
                    load_catalog(path)
            path.write_text('{"tools": []}', encoding="utf-8-sig")
            self.assertEqual(load_catalog(path), {})

    def test_deep_input_rejected(self):
        value = {}
        for _ in range(70):
            value = {"child": value}
        with self.assertRaises(CatalogError):
            normalize_catalog([tool(**{"_meta": value})])


if __name__ == "__main__":
    unittest.main()
