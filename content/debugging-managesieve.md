Title: Debugging Dovecot's Managesieve
Date: 2019-05-12
Category: Blog
Tags: ops, mail, dovecot, sieve

I was trying to figure out why my sieve filters weren't being enabled from
the mail client I use, KMail, which has managesieve protocol support. The 
Dovecot documentation has a troubleshooting section for managesieve
[here](https://wiki2.dovecot.org/Pigeonhole/ManageSieve/Troubleshooting), 
but it isn't really clear. There is a small suggestion that
"you can use Dovecot's rawlog facility" to help debug managesieve, but
no instructions were given. I managed to get it working by doing the
following. First in my `20-managesieve.conf` I put the following:

```text
protocols = $protocols sieve

service managesieve-login {
  inet_listener sieve {
    port = 4190
  }
}

service managesieve {
  executable = managesieve postlogin
  process_limit = 1024
}

protocol sieve {
}

service postlogin {
  executable = script-login -d rawlog
  unix_listener postlogin {
  }
}
```

Specifically, the line with `executable =` and the `service postlogin`
block are important, unless `service postlogin` is defined somewhere else
in your config.

Second, you have to make a `dovecot.rawlog` directory in the users home
directory for every user you want to enable the rawlog for. The raw logs
will appear in this directory like,
`~/dovecot.rawlog/20190512-171623-25459.in`
and
`~/dovecot.rawlog/20190512-171623-25459.out`
for each connection. However they won't appear if the directory doesn't
already exist. They only include a protocol trace from *after* the user
logs in.
