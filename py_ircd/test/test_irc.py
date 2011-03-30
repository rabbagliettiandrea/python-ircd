# -*- coding: utf-8 -*-

from py_ircd.test.mock_client import MockClient
from py_ircd.test.platform import Platform

class TestIRC(Platform):
    
    def test_short_session(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        traffic_expected = [
                ('privmsg #nonjoinato :prova', ':testing_srv 401'),
                ('join #joinato', ':testing_srv 366'),
                ('privmsg #joinato :prova', ''),
        ]
        self.assert_exchange(client, traffic_expected)

    def test_2user_chat(self):
        client_1 = MockClient()
        client_2 = MockClient()
        self.hello(client_1, psw='passwd', nick='nick1', user='user1')
        self.hello(client_2, psw='passwd', nick='nick2', user='user2')
        self.join(client_1, '#test_channel')
        self.join(client_2, '#test_channel')
        client_1.t_send_line('privmsg #test_channel :Some tests, python reigns!')
        self.assert_data_contains(client_2, 'Some tests, python reigns!')
                
    def test_pass_not_given(self):
        client = MockClient()
        self.assert_exchange(client, ('pass ', ':testing_srv 461'))
        
    def test_pass_already_registered(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        self.assert_exchange(client, ('pass passwd', ':testing_srv 462'))
        
    def test_multiple_join(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        client.t_send_line('join #chan3, #chan2 ,#chan1')
        self.assertEqual(set(client.joined_channels.keys()), set(['#chan1', '#chan2', '#chan3']))
        
    def test_join_with_secret_key(self):
        client_creator = MockClient()
        client_2 = MockClient()
        self.hello(client_creator, nick='nick1', user='user1')
        self.join(client_creator, '#test_channel')
        client_creator.t_send_line('mode +t secretFoo')
        self.assert_exchange(client_2, ('join #test_channel', ':testing_srv 475'))
        self.assert_exchange(client_2, ('join #test_channel secretFoo', ':testing_srv 366'))
        
    def test_part_all_from_join_0(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        client.t_send_line('join #chan3, #chan2 ,#chan1')
        client.t_send_line('join 0')
        self.assertEqual(len(client.joined_channels.keys()), 0)
        
        