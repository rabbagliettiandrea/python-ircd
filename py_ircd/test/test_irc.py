# -*- coding: utf-8 -*-

from py_ircd.test.mock_client import MockClient
from py_ircd.test.platform import Platform


class TestIRC(Platform):
    
    def test_normal_session(self):
        client = MockClient()
        traffic_expected = [
                ('pass prova', ''),
                ('nick ciaogffff', ''),
                ('user guest 0 * :ffddsf', ':testing_srv 001'),
                ('privmsg #nonjoinato :prova', ':testing_srv 401'),
                ('join #joinato', ':testing_srv 366'),
                ('privmsg #joinato :prova', ''),
        ]
        self.assert_exchange(client, traffic_expected)

    def test_2user_chat(self):
        client_1 = MockClient()
        client_2 = MockClient()
        self.hello(client_1, nick='nick1', user='user1')
        self.hello(client_2, nick='nick2', user='user2')
        self.assert_exchange(client_1, ('join #test_channel', ':testing_srv 366'))
        self.assert_exchange(client_2, ('join #test_channel', ':testing_srv 366'))
        client_1.t_send_line('privmsg #test_channel :Some tests, python reigns!')
        self.assert_data_contains(client_2, 'Some tests, python reigns!')
                

    def test_pass_not_given(self):
        client = MockClient()
        self.assert_exchange(client, ('pass ', ':testing_srv 461'))

        
        