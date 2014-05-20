from os import makedirs, path
import irc3
from datetime import datetime


@irc3.plugin
class ChannelLogger(object):
    """
    A plugin is a class which take the IrcBot as argument
    """
    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.log

    @irc3.event(irc3.rfc.PRIVMSG)
    def privmsg_logger(self, mask, event, target, data):
        """log irc msg """
        bot = self.bot
        nick = mask.nick
        self.chanlogger(event, target, nick, data)

    @irc3.event(irc3.rfc.JOIN_PART_QUIT)
    def join_quit_logger(self, mask, event, channel, data):
        """log irc msg """
        bot = self.bot
        nick = mask.nick
        if event == 'QUIT':
            channels = self.bot.config['paulla.ircbot.plugins.ChannelLogger']['channels']
            for chan in channels:
                self.chanlogger(event, '#' + chan, nick, data, mask)
        else:
            self.chanlogger(event, channel, nick, data, mask)

    def chanlogger(self, event, channel, nick, data, mask=None):
        now = datetime.now().replace(microsecond = 0)
        log_format = self.bot.config['paulla.ircbot.plugins.ChannelLogger']['format_file'].replace('#channel', channel)
        log_dir = self.bot.config['paulla.ircbot.plugins.ChannelLogger']['directory']
        logfile = now.strftime(log_format)
        logfile = path.join(log_dir, logfile)
        if nick != 'NickServ':
            if not path.exists(path.dirname(logfile)):
                makedirs(path.dirname(logfile))
            if event == 'PRIVMSG':
                if data.startswith('\x01ACTION'):
                    line = "* %s %s" % (nick, data.replace('\x01', '').replace('ACTION', ''))
                else:
                    line = "<%s> %s" % (nick, data)
            elif event == 'JOIN':
                line = '*** %s <%s> has joined %s' % (nick, mask, channel)
            elif event == 'PART':
                line = '*** %s <%s> has left %s' % (nick, mask, channel)
            elif event == 'QUIT':
                line = '*** %s <%s> has quit IRC (%s)' % (nick, mask, data)
            else:
                pass
            with open(logfile, 'a') as f:
                f.write(now.isoformat() + ' ' + line + '\n')

    @irc3.extend
    def privmsg(self, target, message):
        """send a privmsg to target"""
        if target and message:
            messages = irc3.utils.split_message(message, 200)
            for message in messages:
                self.bot.send('PRIVMSG %s :%s' % (target, message))
                self.chanlogger('PRIVMSG', target, self.bot.nick, message)
