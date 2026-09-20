import hashlib
import json
import tempfile
import unittest
import wave
from pathlib import Path
from build_alignment_review import build


class AlignmentReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.wav = Path(self.temp.name) / 'audio.wav'
        self.evidence = Path(self.temp.name) / 'evidence.json'
        with wave.open(str(self.wav), 'wb') as stream:
            stream.setparams((1, 2, 100, 0, 'NONE', 'not compressed'))
            stream.writeframes(b'\x00\x01' * 100)
        self.data = {'audioSha256': hashlib.sha256(self.wav.read_bytes()).hexdigest(),
                     'sampleRate': 100, 'observedFirst33BeatSeconds': [0.1, 0.5]}

    def render(self):
        self.evidence.write_text(json.dumps(self.data))
        return build(self.wav, self.evidence)

    def test_embeds_verified_audio_and_draft_only_export(self):
        html = self.render()
        self.assertIn(self.data['audioSha256'], html)
        self.assertNotIn('__AUDIO__', html)
        self.assertNotIn('__DATA__', html)
        self.assertIn("reviewStatus:'draft'", html)
        self.assertNotIn('https://', html)

    def test_rejects_mismatched_audio(self):
        self.data['audioSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.render()

    def test_rejects_invalid_pulses(self):
        for pulses in [[0.5, 0.1], [0.1, 0.1], [True], [float('nan')], [1.1]]:
            self.data['observedFirst33BeatSeconds'] = pulses
            with self.subTest(pulses=pulses), self.assertRaises(ValueError):
                self.render()

    def test_rejects_rate_mismatch(self):
        self.data['sampleRate'] = 22050
        with self.assertRaisesRegex(ValueError, 'sample-rate'):
            self.render()


if __name__ == '__main__':
    unittest.main()
