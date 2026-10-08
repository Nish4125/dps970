import tempfile
import unittest
from pathlib import Path

from agent import DATA, RULES, in_domains, run, simple_reflex_agent_program

EXPECTED = {
    "01_allowed_with_bad_words.eml": "email",
    "02_restricted_clean.eml": "spam",
    "03_unknown_six_bad_words.eml": "spam",
    "04_unknown_five_bad_words.eml": "email",
    "05_base64_spam.eml": "spam",
    "06_text_attachment_spam.eml": "spam",
    "07_allowed_subdomain.eml": "email",
    "08_lookalike_domain.eml": "spam",
    "09_clean_unknown.eml": "email",
}


class TestSampleInbox(unittest.TestCase):
    def test_every_sample_lands_in_the_right_folder(self):
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(run(DATA / "inbox", out), EXPECTED)
            for name, folder in EXPECTED.items():
                self.assertTrue((Path(out) / folder / name).exists(), name)

    def test_inbox_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as out:
            run(DATA / "inbox", out)
        self.assertEqual(sorted(p.name for p in (DATA / "inbox").glob("*.eml")), sorted(EXPECTED))


class TestRules(unittest.TestCase):
    agent = staticmethod(simple_reflex_agent_program(RULES, lambda state: state))

    def decide(self, allowed=False, restricted=False, bad_words=0):
        return self.agent(dict(allowed=allowed, restricted=restricted, bad_words=bad_words))

    def test_allow_list_beats_everything(self):
        self.assertEqual(self.decide(allowed=True, restricted=True, bad_words=100), "email")

    def test_restrict_list_beats_clean_body(self):
        self.assertEqual(self.decide(restricted=True), "spam")

    def test_bad_word_threshold_is_more_than_five(self):
        self.assertEqual(self.decide(bad_words=5), "email")
        self.assertEqual(self.decide(bad_words=6), "spam")


class TestDomains(unittest.TestCase):
    def test_subdomain_matches_but_lookalike_does_not(self):
        self.assertTrue(in_domains("github.com", {"github.com"}))
        self.assertTrue(in_domains("mail.github.com", {"github.com"}))
        self.assertFalse(in_domains("fakegithub.com", {"github.com"}))
        self.assertFalse(in_domains("", {"github.com"}))


if __name__ == "__main__":
    unittest.main()
