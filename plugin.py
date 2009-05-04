###
# Copyright (c) 2009, Richard Darst
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs

import time
import meeting
meeting = reload(meeting)

class MeatBot(callbacks.Plugin):
    """Add the help for "@plugin help MeatBot" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(MeatBot, self)
        self.__parent.__init__(irc)
                        
        self.Meetings = { }
    
    # Instead of using real supybot commands, I just listen to ALL
    # messages coming in and respond to those beginning with our
    # prefix char.  I found this helpful from a not duplicating logic
    # standpoint (as well as other things).  Ask me if you have more
    # questions.

    # This captures all messages coming into the bot.
    def doPrivmsg(self, irc, msg):
        nick = msg.nick
        channel = msg.args[0]
        payload = msg.args[1]

        # The following is for debugging.  It's excellent to get an
        # interactive interperter inside of the live bot.  use
        # code.interact instead of my souped-up version if you aren't
        # on my computer:
        #if payload == 'interact':
        #    from rkddp.interact import interact ; interact()

        # Get our Meeting object, if one exists.  Have to keep track
        # of different servers/channels.
        # (channel, network) tuple is our lookup key.
        Mkey = (channel,irc.msg.tags['receivedOn']) 
        M = self.Meetings.get(Mkey, None)

        # Start meeting if we are requested
        if payload[:13] == '#startmeeting':
            if M is not None:
                irc.error("Can't start another meeting, one is in progress.")
                return
            M = meeting.Meeting(channel=channel, owner=nick,
                                oldtopic=irc.state.channels[channel].topic)
            self.Meetings[Mkey] = M
            # This callback is used to send data to the channel:
            def _setTopic(x):
                irc.sendMsg(ircmsgs.topic(channel, x))
            def _sendReply(x):
                irc.sendMsg(ircmsgs.privmsg(channel, x))
            M._setTopic = _setTopic
            M._sendReply = _sendReply
        # If there is no meeting going on, then we quit
        if M is None: return
        # Add line to our meeting buffer.
        M.addline(nick, payload)
        # End meeting if requested:
        if payload[:11] == '#endmeeting':
            #M.save()  # now do_endmeeting in M calls the save functions
            del self.Meetings[Mkey]

Class = MeatBot


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
