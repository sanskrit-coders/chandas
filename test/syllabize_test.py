import pytest

from chandas import syllabize

def test_graphemes():
    assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क् र म मे रो ना म हो".split(" ")

def test_syllables():
    assert syllabize.get_syllables(u"बिक्रममेरोनामहो") == "बिक् र म मे रो ना म हो".split(" ")