import unittest
from unittest.mock import patch, Mock
from datetime import datetime
from src.jukebox.jukebox_functions import count_votes


class TestJukeboxFunctions(unittest.TestCase):

    @patch('datetime.now')
    def test_count_votes(self, mock_datetime):
        mock_session = Mock()
        mock_session.return_value = ['1']
        mock_datetime.return_value = datetime.date(day=2, month =10, year=2019)
        test = count_votes(mock_session)
        self.assertEqual(mock_session.return_value, 1)

# if __name__ == '__main__':
#     unittest.main()