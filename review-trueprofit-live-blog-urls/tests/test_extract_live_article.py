"""Regression tests for streamed and legacy TrueProfit FAQ extraction."""

import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from extract_live_article import extract_faqs, hydrate_streamed_components, in_scope_tags


def faq_data(html):
    soup = BeautifulSoup(html, "html.parser")
    hydrate_streamed_components(soup)
    scope, _, _ = in_scope_tags(soup)
    return extract_faqs(scope)


class FAQExtractionTests(unittest.TestCase):
    def test_legacy_label_without_question_classes(self):
        for label in ("Frequently Asked Question", "Frequently Asked Questions"):
            with self.subTest(label=label):
                data = faq_data(
                    '<h1>Article</h1><h2>' + label + '</h2>'
                    '<h3>First <em>question?</em></h3>'
                    '<p>Before <strong>bold</strong> after.</p><p>More detail.</p>'
                    '<h3>Second question?</h3><p>Second answer.</p>'
                    '<div class="wrap-bio">Author text</div>'
                )
                self.assertEqual(data, [
                    {"question": "First question?",
                     "answer": "Before bold after. More detail."},
                    {"question": "Second question?", "answer": "Second answer."},
                ])

    def test_streamed_faq_stays_inside_article(self):
        data = faq_data(
            '<h1>Article</h1><template id="B:0"></template>'
            '<div class="wrap-bio">Author text<h3>Not a FAQ?</h3></div>'
            '<div id="S:0"><h2>Product FAQs</h2>'
            '<div><h3 class="question">Question?</h3><div><p>Answer.</p></div></div>'
            '</div>'
        )
        self.assertEqual(data, [{"question": "Question?", "answer": "Answer."}])

    def test_next_section_ends_faq_and_body_questions_are_ignored(self):
        data = faq_data(
            '<h1>Article</h1><h2>Body</h2><h3>Body question?</h3><p>Body.</p>'
            '<h2>FAQ</h2><h3>FAQ question?</h3><p>Answer.</p>'
            '<h2>Other section</h2><h3>Other question?</h3><p>Not an answer.</p>'
            '<div class="wrap-bio">Author text</div>'
        )
        self.assertEqual(data, [{"question": "FAQ question?", "answer": "Answer."}])


if __name__ == "__main__":
    unittest.main()
