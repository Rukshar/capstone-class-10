import unittest
from unittest.mock import patch, Mock
from datetime import datetime
from src.jukebox.jukebox_functions import count_votes

class TestJukeboxFunctions(unittest.TestCase):

    @patch('datetime.now')
    def test_count_votes(self, mock_lise):
        mock_session = Mock()
        mock_session.return_value = ['1']

        mock_lise.return_value = datetime.date(day=2, month=10, year=2010)

        count_votes(mock_session)

        return ''