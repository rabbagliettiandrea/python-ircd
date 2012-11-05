# -*- coding: utf-8 -*-

from py_ircd.test.mock_client import MockClient
from py_ircd.test.platform import Platform


class TestIRC(Platform):
    
    def test_short_session(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        traffic_expected = [
                ('privmsg #nonjoinato :prova', 'ERR_CANNOTSENDTOCHAN'),
                ('join #joinato', 'RPL_ENDOFNAMES'),
                ('privmsg #joinato :prova', ''),
        ]
        self.assert_exchange(client, self.assertIn, traffic_expected)

    def test_2user_chat(self):
        client_1 = MockClient()
        client_2 = MockClient()
        self.hello(client_1, psw='passwd', nick='nick1', user='user1')
        self.hello(client_2, psw='passwd', nick='nick2', user='user2')
        client_1.t_send_line('join #test_channel')
        client_2.t_send_line('join #test_channel')
        client_1.t_send_line('privmsg #test_channel :Some tests, python reigns!')
        self.assert_data_contains(client_2, 'Some tests, python reigns!')
                
    def test_pass_not_given(self):
        client = MockClient()
        self.assert_exchange(client, self.assertIn, ('pass ', 'ERR_NEEDMOREPARAMS'))
        
    def test_pass_already_registered(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        self.assert_exchange(client, self.assertIn, ('pass passwd', 'ERR_ALREADYREGISTRED'))
        
    def test_multiple_join(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        client.t_send_line('join #chan3, #chan2 ,#chan1')
        self.assertEqual(set(client.joined_channels.keys()), set(['#chan1', '#chan2', '#chan3']))
        
    def test_join_with_secret_key(self):
        client_creator = MockClient()
        client = MockClient()
        self.hello(client_creator, nick='nick1', user='user1')
        client.t_send_line('join #test_channel')
        client_creator.t_send_line('mode #test_channel +k secretfoo')
        self.assert_exchange(client, self.assertIn, ('join #test_channel', 'ERR_ALREADYREGISTRED'))
        self.assert_exchange(client, self.assertIn, ('join #test_channel secretfoo', 'RPL_ENDOFNAMES'))
        
    def test_part_all_from_join_0(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        client.t_send_line('join #chan3, #chan2 ,#chan1')
        client.t_send_line('join 0')
        
    def test_part_some_with_msg(self):
        client_1 = MockClient()
        client_2 = MockClient()
        self.hello(client_1, nick='nick1', user='user1')
        self.hello(client_2, nick='nick2', user='user2')
        client_1.t_send_line('join #chan3, #chan2 ,#chan1')
        client_2.t_send_line('join #chan3,#chan2, #chan1')
        client_1.t_send_line('part #chan3, #chan2 :this is a part message!!')
        self.assert_data_contains(client_2, '#chan2 :this is a part message!!', '#chan3 :this is a part message!!')

    def test_mode_noparams(self):
        client_1 = MockClient()
        client_2 = MockClient()
        self.hello(client_1, nick='nick1', user='user1')
        self.hello(client_2, nick='nick2', user='user2')
        client_1.t_send_line('join #chan')
        client_2.t_send_line('mode #chan')
        self.assert_data_contains(client_2, 'RPL_CHANNELMODEIS', 'RPL_CREATIONTIME')
        self.assert_exchange(client_1, self.assertIn, ('mode nick2', 'ERR_USERSDONTMATCH'))
        self.assert_exchange(client_1, self.assertIn, ('mode nick1', 'RPL_UMODEIS'))
        self.assert_exchange(client_1, self.assertIn, ('mode nickFOO', 'ERR_NOSUCHNICK'))

    def test_mode_set_some(self):
        client = MockClient()
        self.hello(client, nick='nick1', user='user1')
        self.assert_exchange(client, self.assertEqual, ('mode nick1 +ia', ':nick1 MODE nick1 :+i'))
        self.assert_exchange(client, self.assertEqual, ('mode nick1 -i', ':nick1 MODE nick1 :-i'))
        self.assertEqual(len(client.modes), 0)