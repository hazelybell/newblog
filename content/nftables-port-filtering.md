Title: Port Triggering with Linux nftables
Slug: nftables-port-triggering
Date: 2021-10-28
Category: Blog
Tags: ops, networking, linux, netfilter, nftables, xbox, gaming, switch

In order to improve networking on consoles, primarily the Nintendo Switch,
while using an Ubuntu Linux-powered box as a home router, I came up with the
following solution. It uses Linux's nftables to produce a port-triggering
effect and earn's the Nintendo's top NAT score of "A" *without* any extra or
custom kernel modules.

The effect relies on nftable's use of "named maps," which are described poorly
here: [Named Maps](https://wiki.nftables.org/wiki-nftables/index.php/Maps).
By combining this concept with the concepts in the page about updating sets
[here](https://wiki.nftables.org/wiki-nftables/index.php/Updating_sets_from_the_packet_path),
I was able to get port triggering working.

I've set this up only for UDP.
There's no reason why it wouldn't work with TCP, but as far as I know, TCP
port triggering isn't widely used, or used at all, for gaming.
I've also focused on IPv4. The only reason for this is that my ISP doesn't
yet provide IPv6 service.

The following snippets use Jinja2 templating, so please, replace anything in
double braces like `{{ this }}` with the relevant information if you're copying
this config to your own config.

The first step is to set up a basic masquerade NAT.

```nftables
table inet mychains {
    chain input_filter {
        type filter hook input priority filter;
        policy accept; # this is not a firewall, allow all incoming packets
        
        # This is where you'd add firewall rules to protect the router machine,
        # but not other machines on the NAT.
    }
    chain forward_filter {
        type filter hook forward priority 0;
        policy accept; # this is not a firewall, forward all packets
        
        # This is where you'd add firewall rules to protect
        # other machines on the NAT, but not the router machine.
    }
    chain output_filter {
        type filter hook output priority 0;
        policy accept; # this is not a firewall, allow all outbound packets

        # This is where you'd add firewall rules to protect other machines
        # from any potentially untrusted software on the router machine,
        # but usually it's not used in basic firewalls since we assume
        # the router is running only trusted software and hasn't been hacked.
    }
    chain postrouting_nat {
        type nat hook postrouting priority srcnat;
        policy accept;
        
        # Perform basic masquerading.
        oifname {{ outside_interface }} masquerade;
    }
    chain prerouting_nat {
        type nat hook prerouting priority dstnat;
        policy accept;
        
        # This is where we'd do basic portmapping.
        # Here's an example of mapping {{ port }} to {{ host.ip }}.
        iifname {{ outside_interface }} meta l4proto {tcp, udp} th dport {{ port }} dnat ip to {{ host.ip }};
    }
}
```

This is inadequate, since it relies entirely on the Linux kernel's "conntrack" 
connection tracking mechanism.
Basic STUN (Simultaneous Traversal UDP NAT) works, which is sufficient for
most applications and gets us a Nintendo NAT grade of "B".
In this setup if our hosts wants to recieve a UDP packet on an unmapped port
it first has to send a UDP packet on the same port to the 
*same remote host and port*.
For example, if 198.51.100.222 is inside (behind) this NAT, and sends a UDP
packet from port 50069 to 203.0.113.0:3544, 
afterwards 198.51.100.222 can recieve packets on port 50069, but
*only from 203.0.113.0:3544*.

What we want to do is change this scenario so that if 198.51.100.222
sends a UDP packet from port 50069, afterwards it can recieve packets on port
50069 from *anywhere*.

The first step is to define a nftables named map:

```nftables
    map porttoip {
        type inet_service: ipv4_addr;
        size 65535;
        
        # This sets up our "map" aka hash table, associative array,
        # dictionary, whatever. This will store key-value pairs in the format
        # PORT: ADDRESS as defined in the type line.
    }
```

The second step is to define some UDP ports that we definitely don't want
to allow to be triggered.

```nftables
# These are ports that we don't want to be triggered.
# Some of them are ports we want to reserve for the machine doing the routing.
# Some of them should also be firewalled, however, for this config,
# we're relying on the security of the machine doing the routing.
define RESERVE_PORTS = {
    0-665, # Privileged ports. Inncludes things like DNS, DHCP, and WoL
    # Skip 666 - Port used by DOOM
    667-986, # Privileged ports. Games shouldn't use these with a few exceptions
    # Skip 987 - Port used by Sony Playstation
    988-1024, # Privileged ports. Games shouldn't use these with a few exceptions
    1080, # SOCKS/MiniUPnPd
    1081, # SOCKS/MiniUPnPd
    1194, # OpenVPN
    1293, # IPSec
    1350, # Commonly Scanned
    1433, 1434, # MSSQL (Commonly Scanned)
    1417-1420, # Timbuktu Remote Control (Commonly Scanned)
    1512, # Insecure Windows Junk
    1723, # PPTP (Commonly Scanned)
    1801, # Insecure Windows Junk
    1812, 1813, # Insecure Enterprise Junk
    1900, # SSDP/UPnP (LAN-only DNS & service discovery)
    2001, # Cisco (sans.org Firewall Checklist)
    2049, # Linux/OS X NFS (Insecure Linux Junk)
    2222, # DirectAdmin (Commonly Scanned)
    2251, # Distributed Framework (Commonly Scanned)
    2375, # Docker (Commonly Scanned)
    2535, # MADCAP
    2869, # UPnP
    3020, # Insecure Windows Junk
    3260, # iSCSI (Insecure Enterprise Junk)
    3283, # Apple Remote Desktop
    3306, # MySQL (Commonly Scanned)
    3389, # Windows Remote Desktop (Commonly Scanned)
    3702, # Windows Printers
    4001, # Cisco (sans.org Firewall Checklist)
    4045, # LockD (sans.org Firewall Checklist)
    4444, # Commonly Scanned
    4899, # Remote Administration
    5000, # UPnP
    5351, # NAT-PMP (similar to UPnP)
    5353, # LAN DNS (LAN-only DNS & service discovery)
    5355, # LLMNR (LAN-only DNS & service discovery)
    5332, # PostgreSQL (Commonly Scanned)
    5555, # MS CRM (Commonly Scanned)
    5900, # VNC Remote Desktop (Commonly Scanned)
    5938, # TeamViewer Remote Desktop
    6000-6255, # X11 (Insecure Linux Junk)
    6379, # Redis (Commonly Scanned)
    2323, # Alternate Telnet (Commonly Scanned)
    8000, 8008, 8080, 8081, 8443, 8888, # HTTP Alternates (Commonly Scanned)
    9200, # ElasticSearch (Commonly Scanned)
}

# Interesting ports NOT reserved (Excluded from the above list)
# Though these may be a security issue...
1935, # RTMP (Media Streaming)
5004, 5005, # RTP & RTCP
5060, # SIP
6881, # BitTorrent
```

The third step is to have outbound udp packets fill in our map. We do this
by modifying the `postrouting_nat` chain and adding a new chain: `new_outgoing`.

```nftables
    chain nat_postrouting {
        type nat hook postrouting priority srcnat;
        policy accept;
        # Note that we have to jump before masquerade, otherwise the jump
        # will never run.
        oifname {{ outside_interface }} jump new_outgoing;
        oifname {{ outside_interface }} masquerade;
    }
    chain new_outgoing {
        # We don't care about anything but UDP.
        # This is the line to change if you want to do this with TCP too.
        meta l4proto != udp return;
        
        # We should only care about packets going to addresses on the outside.
        ip daddr {{ inside_network }} return;
        
        # Reserve these ports for explicit port forwarding or services running
        # on the router machine.
        # Add a line for TCP if you want to do TCP too.
        udp sport $RESERVE_PORTS return;
        
        # Don't worry about packets belonging to connections that conntrack
        # is already natting. This includes connections that masquerade is
        # working with just fine already.
        ct status {snat, dnat} return;
        
        # Log the packet, so we can see why things are getting added.
        log prefix "trigger ";
        
        # Add the port to the mapping we defined. This is the actual part
        # where the port gets "triggered". We remember who used the port,
        # so we can send inbound packets to them later.
        add @porttoip { udp sport: ip saddr }
    }
```
The next step is to have inbound udp packets that don't have anywhere to go,
go to the ip address that last triggered that port. We do this by adding
a "late prerouting" chain. This is like the `prerouting_nat` chain we defined
above, but it has a priority with a higher number (400 vs -100), which will
cause it to have the *lowest* priority (it will run *last*).
This will hopefully allow any other DNAT rules (and masquerade),
and more importantly runs after connection tracking.

Then we send any packets coming from outside the NAT to a custom `late_incoming`
chain. `late_incoming` works a lot like `new_outgoing`, but instead of storing
the triggered ports, we retrieve and apply them.

```nftables
    chain late_prerouting {
        type nat hook prerouting priority 400;
        policy accept;
        iifname {{ outside_interface }} jump late_incoming;
    }
    chain late_incoming {
        # We don't care about anything but UDP.
        # This a the line to change if you want to do this with TCP too.
        meta l4proto != udp return;
        
        # We should only care about packets coming addresses on the outside.
        ip saddr {{ inside_network }} return;
        
        # Reserve these ports for explicit port forwarding or services running
        # on the router machine.
        udp sport $RESERVE_PORTS return;
        tcp sport $RESERVE_PORTS return;

        # Don't worry about packets belonging to connections that conntrack
        # is already natting. This includes connections that masquerade is
        # working with just fine already.
        ct status {snat, dnat} return;
        
        # Log the packet, so we can see why things are using the triggered
        # ports. But only one packet per connection, please.
        ip version 4 ct state {new, invalid, untracked} log prefix "ingress ";
        
        # If the packet is UDP and the destination port
        # matches one of the triggered ports we saved
        # in our map, then send it to the host that triggered it.
        # But only for udp ports. Add a line for TCP if you want that.
        meta l4proto udp dnat ip to udp dport map @porttoip;
    }
```

And... that's about it. Unfortunately, it's not particularly robust. If two
different machines want the same port, only the machine that triggers it *last*
will get it.
I've designed it to give the much more robust mechanisms built into linux
first shot at handling things. The triggered ports are only used as a last
resort.

This is not particularly secure, either.
If anything, this reduces network security compared to a basic linux NAT.
Exploited computers, consoles, phones, IoT devices, etc. can easily use this to
open ports for themselves.
It doesn't do anything to prevent address spoofing from causing all sorts
of mayhem.

This is not ready for
production use outside of a single-user home network, for sure. It's also not
a firewall or particularly secure in any way.

Here's a full ruleset example. It's designed for some details
to be filled in by Ansible/Jinja2.

```nftables
#!/usr/sbin/nft -f

flush ruleset

define PRIVATE_RANGES = {
            0.0.0.0/8,
            10.0.0.0/8,
            100.64.0.0/10,
            127.0.0.0/8,
            169.254.0.0/16,
            172.16.0.0/12,
            192.0.0.0/24,
            192.0.2.0/24,
            192.168.0.0/16,
            198.18.0.0/15,
            198.51.100.0/24,
            203.0.113.0/24
}

define PRIVATE_RANGES6 = {
    ::1/128,
    2001:db8::/32,
    4000::/3,
    6000::/3,
    8000::/3,
    a000::/3,
    c000::/3,
    e000::/3,
}

define RESERVE_PORTS = {
    22,
    1080,
    1081,
    67,
    53,
    80,
    443
}

table inet my {
    chain input {
        type filter hook input priority 0;
        policy accept;
        iif lo accept;
        iifname != {{ outside_interface }} accept;
        ip saddr $PRIVATE_RANGES accept;
        ip6 saddr $PRIVATE_RANGES6 accept;
        meta l4proto ipv6-icmp accept;
        meta l4proto icmp accept;
        meta l4proto igmp accept;
        ct state related,established accept;
        # These should all be new packets coming from the internet
        jump new_pkts;
        ct state new log prefix "new_pkt ";
        ct state invalid log prefix "inv_pkt ";
        ct state untracked log prefix "unt_pkt ";
    }
    chain new_pkts {
        tcp dport $RESERVE_PORTS accept;
        udp dport $RESERVE_PORTS accept;
    }
    chain forward {
        type filter hook forward priority 0;
        policy accept;
{% for host in network.nethosts %}
{% if 'ports' in host %}
{% for port in host.ports %}
        oifname {{ outside_interface }} ip saddr != {{ host.ip }} tcp sport {{ port }} jump port_stealing;
        oifname {{ outside_interface }} ip saddr != {{ host.ip }} udp sport {{ port }} jump port_stealing;
{% endfor %}
{% endif %}
{% endfor %}
    }
    chain port_stealing {
        log prefix "port_stealing ";
        reject with icmp type admin-prohibited;
    }
    chain output {
        type filter hook output priority 0;
        policy accept;
    }
    map porttoip {
        type inet_service: ipv4_addr;
    }
    chain nat_postrouting {
        type nat hook postrouting priority srcnat;
        policy accept;
        oifname {{ outside_interface }} jump new_outgoing;
        oifname {{ outside_interface }} masquerade;
    }
    chain new_outgoing {
        meta l4proto != udp return;
        ip daddr {{ inside_ip }}/{{ inside_nm }} return;
        udp sport $RESERVE_PORTS return;
        udp sport { 0-1024 } return;
        ct state != { new, invalid, untracked } return;
        log prefix "trigger ";
        add @porttoip { udp sport: ip saddr }
    }
    chain nat_prerouting {
        type nat hook prerouting priority dstnat;
        policy accept;
{% for host in network.nethosts -%}
{% if 'ports' in host -%}
{% for port in host.ports -%}
        iifname {{ outside_interface }} meta l4proto {tcp, udp} th dport {{ port }} dnat ip to {{ host.ip }};
{% endfor %}
{% endif %}
{% endfor %}
    }
    chain late_prerouting {
        type nat hook prerouting priority 400;
        policy accept;
        iifname {{ outside_interface }} jump late_ingress;
    }
    chain late_ingress {
        tcp dport $RESERVE_PORTS return;
        udp dport $RESERVE_PORTS return;
        tcp dport { 0-1081 } return;
        udp dport { 0-1081 } return;
        meta l4proto tcp return;
        ct status {snat, dnat} return;
        ip version 4 ct state {new, invalid, untracked} log prefix "ingress ";
        dnat ip to udp dport map @porttoip;
    }
}
```
For low-throughput home networks, you may also want to add additional connection
tracking helpers, and set connection tracking sysctl knobs to give
conntrack the best chance of just handling stuff for itself.

Additional connection trackers are available as modules:
```
nf_conntrack_netbios_ns
nf_conntrack_tftp
nf_conntrack_ftp
nf_conntrack_pptp
nf_conntrack_netlink
nf_conntrack_sip
nf_conntrack_snmp
nf_conntrack_amanda
nf_conntrack_irc
nf_conntrack_broadcast
nf_conntrack_sane
nf_conntrack_h323
nf_conntrack_bridge
nf_conntrack_rtsp # available from package nat-rtsp-dkms
```

sysctl knobs you might set follow.
Some of the timeouts are just set to 10x their default value.
```
net.netfilter.nf_conntrack_checksum = 0
net.netfilter.nf_conntrack_generic_timeout = 3600
net.netfilter.nf_conntrack_max = 262144
net.netfilter.nf_conntrack_helper = 1
net.netfilter.nf_conntrack_tcp_be_liberal = 1
net.netfilter.nf_conntrack_tcp_loose = 1
net.netfilter.nf_conntrack_udp_timeout = 300
net.netfilter.nf_conntrack_udp_timeout_stream = 1200
net.netfilter.nf_conntrack_tcp_max_retrans = 3
net.netfilter.nf_conntrack_tcp_timeout_close = 100
net.netfilter.nf_conntrack_tcp_timeout_close_wait = 600
net.netfilter.nf_conntrack_tcp_timeout_established = 432000
net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 1200
net.netfilter.nf_conntrack_tcp_timeout_last_ack = 300
net.netfilter.nf_conntrack_tcp_timeout_max_retrans = 3000
net.netfilter.nf_conntrack_tcp_timeout_syn_recv = 600
net.netfilter.nf_conntrack_tcp_timeout_syn_sent = 1200
net.netfilter.nf_conntrack_tcp_timeout_time_wait = 1200
net.netfilter.nf_conntrack_tcp_timeout_unacknowledged = 3000
```
