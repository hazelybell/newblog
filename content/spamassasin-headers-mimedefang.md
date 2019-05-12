Title: Adding Standard SpamAssasin Headers with MIMEDefang
Date: 2019-05-11
Category: Blog
Tags: ops, mail, spam

I decided to try out MIMEDefang with SpamAssasin as a Milter to detect
incoming spam and reject it on my mailserver. However, I wanted to see
the regular headers you get from SpamAssasin when you run it directly
in my mails. The problem is, MIMEDefang doesn't let SpamAssasin modify
the mail in anyway, you have to tell MIMEDefang what modifications to
make to headers. So, I came up with the following solution for getting
MIMEDefang to add headers just like the headers you get when you run
SpamAssasin directly:

    :::perl
    if ($Features{"SpamAssassin"}) {
        print STDERR "SpamAssassin!";
        if (-s "./INPUTMSG" < 1024*1024) {
            # Only scan messages smaller than 1MiB.  Larger messages
            # are extremely unlikely to be spam, and SpamAssassin is
            # dreadfully slow on very large messages.
            my $status = spam_assassin_status();
            $status->learn();
            my $hits = $status->get_hits;
            my $req = $status->get_required_hits();
            my $tests = $status->get_names_of_tests_hit();
            my $report = $status->get_report();
            my $autolearn = $status->get_autolearn_status();
            my $saversion = $status->get_tag('VERSION');
            my $terse = $status->get_tag('REPORT');
            my $bayes = $status->get_tag('BAYES');
            my $toksummary = $status->get_tag('TOKENSUMMARY');
            my $hammy = $status->get_tag('HAMMYTOKENS');
            my $spammy = $status->get_tag('SPAMMYTOKENS');
            $status->finish();
            my($score);
            if ($hits < 40) {
                $score = "*" x int($hits);
            } else {
                $score = "*" x 40;
            }
            # We add a header which looks like this:
            # X-Spam-Score: 6.8 (******) NAME_OF_TEST,NAME_OF_TEST
            # The number of asterisks in parens is the integer part
            # of the spam score clamped to a maximum of 40.
            # MUA filters can easily be written to trigger on a
            # minimum number of asterisks...
            action_change_header("X-Spam-Score", "$hits ($score) $names");
            action_change_header("X-Spam-Level", "$score");
            action_change_header("X-Spam-Flag",
                ($hits > $req) ? "YES" : "NO"
            );
            action_change_header("X-Spam-Status",
                (($hits > $req) ? "Yes," : "No,")
                . " score=$hits"
                . " required=$req"
                . " tests=$names"
                . " version=$saversion"
                . " autolearn=$autolearn"
            );
            action_change_header("X-Spam-Report",
                $terse
            );
            action_change_header("X-Spam-Bayes",
                "score=$bayes"
                . " Tokens: $toksummary"
                . "\nHammy: $hammy"
                . "\nSpammy: $spammy"
            );
            md_syslog('info',
                (($hits > $req) ? "spam" : "ham")
                . " " . $hits
                . " " . $RelayAddr
            );
        }
    }



