import copy
import unittest

from repair_contextual_octaves import repair_events, transform


def e(i, t, midi):
    return {"id": i, "start": t, "end": t + 0.2, "midi": midi, "amplitude": 0.5}


class ContextualOctaveRepairTests(unittest.TestCase):
    def test_repairs_singleton_octave_when_both_neighbors_support_lower_voice(self):
        rows = [e("a", 0, 52), e("b", 0.3, 64), e("c", 0.6, 52)]
        fixed, changes = repair_events(rows)
        self.assertEqual([r["midi"] for r in fixed], [52, 52, 52])
        self.assertEqual(changes[0]["fromMidi"], 64)
        self.assertEqual(changes[0]["toMidi"], 52)

    def test_does_not_change_chord_group(self):
        rows = [e("a", 0, 52), e("b", 0.3, 64), e("x", 0.31, 67), e("c", 0.6, 52)]
        fixed, changes = repair_events(rows)
        self.assertEqual([r["midi"] for r in fixed], [52, 64, 67, 52])
        self.assertEqual(changes, [])

    def test_does_not_change_when_lower_octave_lacks_two_sided_support(self):
        rows = [e("a", 0, 52), e("b", 0.3, 64), e("c", 0.6, 67)]
        fixed, changes = repair_events(rows)
        self.assertEqual([r["midi"] for r in fixed], [52, 64, 67])
        self.assertEqual(changes, [])

    def test_does_not_bridge_long_context_gap(self):
        rows = [e("a", 0, 52), e("b", 1.0, 64), e("c", 1.3, 52)]
        fixed, changes = repair_events(rows)
        self.assertEqual([r["midi"] for r in fixed], [52, 64, 52])
        self.assertEqual(changes, [])

    def test_never_changes_count_or_time(self):
        rows = [e("a", 0, 52), e("b", 0.3, 64), e("c", 0.6, 52)]
        fixed, _ = repair_events(rows)
        self.assertEqual(len(fixed), len(rows))
        self.assertEqual([(r["start"], r["end"]) for r in fixed], [(r["start"], r["end"]) for r in rows])

    def test_input_is_not_mutated_and_delivery_stays_false(self):
        doc = {"kind": "x", "customerDeliveryEligible": False, "events": [e("a", 0, 52), e("b", 0.3, 64), e("c", 0.6, 52)]}
        before = copy.deepcopy(doc)
        out = transform(doc, input_sha256="a" * 64)
        self.assertEqual(doc, before)
        self.assertFalse(out["customerDeliveryEligible"])
        self.assertFalse(out["octaveRepair"]["referenceLabelsRead"])

    def test_invalid_event_fails_closed(self):
        with self.assertRaises(ValueError):
            repair_events([{"id": "a", "start": 0, "end": 1, "midi": True}])


if __name__ == "__main__":
    unittest.main()
