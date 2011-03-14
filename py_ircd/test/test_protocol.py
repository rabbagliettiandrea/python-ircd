# -*- coding: utf-8 -*-

from py_ircd.test.platform import Platform

class TestProtocol(Platform):
    
    def test_normal_session(self):
        traffic_expected = [
                ('pass prova', ''),
                ('nick ciaogffff', ''),
                ('user guest 0 * :ffddsf', ':testing_srv 001'),
                ('privmsg #nonjoinato :prova', ':testing_srv 401'),
                ('join #joinato', ':testing_srv 366'),
                ('privmsg #joinato :prova', ''),
        ]
        self.assert_exchange(traffic_expected)


    def test_pass_not_given(self):
        traffic_expected = [
                ('pass ', ':testing_srv 461'),
        ]
        self.assert_exchange(traffic_expected)

        
        