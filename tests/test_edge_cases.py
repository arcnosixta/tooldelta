import unittest

from mcp_tooldelta.catalog import CatalogError, normalize_catalog
from mcp_tooldelta.diff import compare


def tool(child):
    return {"name": "t", "inputSchema": {"type": "object", "properties": {"x": child}, "additionalProperties": False}}


class EdgeCaseTests(unittest.TestCase):
    def test_input_and_output_bounds_matrix(self):
        for keyword, before, after in (
            ("minimum", 0, 1), ("maximum", 10, 9),
            ("exclusiveMinimum", 0, 1), ("exclusiveMaximum", 10, 9),
            ("minLength", 0, 1), ("maxLength", 10, 9),
            ("minItems", 0, 1), ("maxItems", 10, 9),
            ("minProperties", 0, 1), ("maxProperties", 10, 9),
        ):
            with self.subTest(keyword=keyword):
                a, b = tool({keyword: before}), tool({keyword: after})
                self.assertTrue(compare([a], [b]).fails())
                self.assertFalse(compare([b], [a]).fails())
                a = {"name": "t", "inputSchema": {"type": "object"}, "outputSchema": a["inputSchema"]}
                b = {"name": "t", "inputSchema": {"type": "object"}, "outputSchema": b["inputSchema"]}
                self.assertFalse(compare([a], [b]).fails())
                self.assertTrue(compare([b], [a]).fails())

    def test_numeric_enum_equality_is_not_boolean_equality(self):
        self.assertFalse(compare([tool({"enum": [1]})], [tool({"enum": [1.0]})]).changes)
        self.assertTrue(compare([tool({"enum": [True]})], [tool({"enum": [1]})]).fails())
        with self.assertRaises(CatalogError):
            normalize_catalog([tool({"enum": [1, 1.0]})])

    def test_unsupported_nested_in_new_optional_property(self):
        old = {"name": "t", "inputSchema": {"type": "object", "additionalProperties": False}}
        new = tool({"type": "object", "properties": {"nested": {"$ref": "#/other"}}})
        report = compare([old], [new])
        self.assertTrue(report.fails("review"))
        self.assertEqual(report.counts["review"], 1)

    def test_boolean_replacement_preserves_unknown_nested_review(self):
        a = tool(True)
        b = tool({"type": "object", "properties": {"z": {"pattern": "^a"}}})
        self.assertEqual(compare([a], [b]).counts["review"], 1)

    def test_json_pointer_escaping(self):
        a = {"name": "t", "inputSchema": {"type": "object", "properties": {"a~/b": {"type": "string"}}, "additionalProperties": False}}
        b = {"name": "t", "inputSchema": {"type": "object", "additionalProperties": False}}
        self.assertEqual(compare([a], [b]).changes[0].path, "/inputSchema/properties/a~0~1b")

    def test_unknown_extensions_changed_are_reviewed(self):
        a = {**tool({"type": "string"}), "_meta": {"vendor": "v1"}}
        b = {**tool({"type": "string"}), "_meta": {"vendor": "v2"}}
        self.assertEqual(compare([a], [b]).counts["review"], 1)

    def test_additional_schema_constraints_and_unique_arrays(self):
        a = {"name": "t", "inputSchema": {"type": "object"}}
        b = {"name": "t", "inputSchema": {"type": "object", "additionalProperties": {"type": "string"}}}
        self.assertTrue(compare([a], [b]).fails())
        self.assertTrue(compare([tool({"type": "array"})], [tool({"type": "array", "uniqueItems": True})]).fails())

    def test_boolean_extra_relaxation_with_new_properties_is_not_review(self):
        a = {"name": "t", "inputSchema": {"type": "object", "additionalProperties": False}}
        b = {"name": "t", "inputSchema": {"type": "object", "properties": {"optional": {"type": "string"}}}}
        report = compare([a], [b])
        self.assertEqual(report.counts["review"], 0)
        self.assertFalse(report.fails())
        self.assertTrue(compare([b], [a]).fails())

    def test_zero_minimum_cardinality_is_default_not_breaking(self):
        for keyword in ("minLength", "minItems", "minProperties"):
            with self.subTest(keyword=keyword):
                self.assertFalse(compare([tool({})], [tool({keyword: 0})]).changes)


if __name__ == "__main__":
    unittest.main()
