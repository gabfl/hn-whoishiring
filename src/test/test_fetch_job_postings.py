import os
from datetime import datetime

import unittest
from bs4 import BeautifulSoup

from .. import fetch_job_postings


class Test(unittest.TestCase):

    sample_html_path = os.path.dirname(__file__) + '/assets/sample.html'
    sample_item = """<tr class="athing comtr" id="41555035"><td><table border="0"><tr><td class="ind" indent="0"><img height="1" src="s.gif" width="0"></td>
    <td class="votelinks" valign="top"><center><a href="vote?id=41555035&amp;how=up&amp;goto=item%3Fid%3D41425910" id="up_41555035">
    <div class="votearrow" title="upvote"></div></a></center></td><td class="default"><div style="margin-top:2px;margin-bottom:-10px">
    <span class="comhead"><a class="hnuser" href="user?id=OnjaMadagascar">OnjaMadagascar</a><span class="age" title="2024-09-16T11:40:43.000000Z">
    <a href="item?id=41555035">48 minutes ago</a></span><span id="unv_41555035"></span><span class="navs">|
    <a aria-hidden="true" class="clicky" href="#41554922">next</a><a class="togg clicky" href="javascript:void(0)" id="41555035" n="1">[–]</a>
    <span class="onstory"></span></span></span></div><br><div class="comment">
    <div class="commtext c00">Sealth | Designer &amp; Back end Course Designer| Full-Time</p></div><div class="reply"><p><font size="1"><u>
    <a href="reply?id=41555035&amp;goto=item%3Fid%3D41425910%2341555035" rel="nofollow">reply</a></u></font></p></div></div></td></tr></table></td></tr>"""

    def test_load_url(self):
        res = fetch_job_postings.load_url('http://perdu.com')
        self.assertTrue(res.startswith('<html><head>'))

    def test_load_file(self):
        res = fetch_job_postings.load_file(self.sample_html_path)
        self.assertTrue(res.startswith('<html lang="en" op="item">'))

    def test_get_all_comments(self):
        source = fetch_job_postings.load_file(self.sample_html_path)
        soup = fetch_job_postings.BeautifulSoup(source, 'html.parser')
        res = fetch_job_postings.get_all_comments(soup)
        self.assertEqual(len(res), 474)

    def test_is_reply(self):
        # Create soup from sample item
        soup = BeautifulSoup(
            self.sample_item, 'html.parser')

        res = fetch_job_postings.is_reply(soup)
        self.assertFalse(res)

        # replace indent="0 with indent="1"
        soup = BeautifulSoup(
            self.sample_item.replace('indent="0"', 'indent="1"'), 'html.parser')

        res = fetch_job_postings.is_reply(soup)
        self.assertTrue(res)

    def test_parse_from_comment(self):
        # Create soup from sample item
        soup = BeautifulSoup(
            self.sample_item, 'html.parser')

        (comment, hn_user, hn_id) = fetch_job_postings.parse_from_comment(soup)

        self.assertEqual(
            comment, '<div class="commtext c00">Sealth | Designer &amp; Back end Course Designer| Full-Time</div>')
        self.assertEqual(hn_user, 'OnjaMadagascar')
        self.assertEqual(hn_id, '41555035')
