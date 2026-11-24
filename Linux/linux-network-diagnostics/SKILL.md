---
name: linux-network-diagnostics
description: Diagnoses Linux connectivity, DNS, routing, port, firewall, and packet-loss problems layer by layer using ip, ss, dig, curl, tcpdump, and nftables. Use for "cannot connect", intermittent timeouts, slow transfers, DNS failures, and service reachability checks.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: linux
---

# Linux Network Diagnostics

## Overview

Network failures are layered. A DNS failure looks like a connection failure; a firewall drop looks like a timeout; an MTU problem looks like a hang after the TLS handshake. Diagnose from the bottom up and prove each layer before moving on.

Capture evidence with commands, not assumptions.

## When to use

- A host cannot reach a service, or a service cannot be reached.
- DNS resolution is slow, inconsistent, or wrong.
- Connections time out, reset, or hang mid-transfer.
- Packet loss or latency is suspected.
- A firewall or proxy change broke traffic.

## Layer checklist

| Layer | Question | Command |
| --- | --- | --- |
| Link | Is the interface up? | `ip -br link` |
| Address | Does it have an IP? | `ip -br addr` |
| Route | Is there a path? | `ip route get 1.1.1.1` |
| DNS | Does the name resolve? | `dig +short example.com` |
| Port | Is something listening? | `ss -tulpn` |
| Transport | Can a TCP connection open? | `nc -vz host 443` |
| TLS | Does the handshake complete? | `openssl s_client -connect host:443 -servername host` |
| Application | Does the request succeed? | `curl -v https://host/health` |
| Firewall | Is traffic allowed? | `nft list ruleset` / `iptables -S` |
| Path | Where is latency or loss? | `mtr -rwzbc 20 host` |

## Workflow

### 1. Define the symptom precisely

Record:

- Source host, destination host, port, and protocol.
- Whether it ever worked and what changed.
- Whether it fails for all clients or one.
- Whether it fails by IP as well as by name.
- The exact error: refused, timeout, reset, DNS, TLS, or HTTP status.

### 2. Check link and address

```bash
ip -br link
ip -br addr
ethtool <interface> | head -30
nmcli device status
```

Look for `DOWN`, missing addresses, duplicate IPs, or a interface in an unexpected network namespace.

### 3. Check routing

```bash
ip route
ip route get 1.1.1.1
ip -6 route
```

If the route is missing, check the default gateway, policy routing (`ip rule`), and multiple routing tables (`ip route show table all`).

### 4. Check DNS

```bash
resolvectl status
dig +short example.com
dig +trace example.com
getent hosts example.com
cat /etc/resolv.conf
```

Compare `dig` (direct DNS) with `getent` (NSS, including `/etc/hosts` and LDAP). A difference points to NSS or caching.

### 5. Check listening ports

```bash
ss -tulpn
ss -tnp state established
ss -s
lsof -nP -iTCP -sTCP:LISTEN
```

A service bound to `127.0.0.1` is not reachable from another host. Check the bind address, not only the port.

### 6. Test reachability and latency

```bash
ping -c 4 <host>
mtr -rwzbc 20 <host>
traceroute -T -p 443 <host>
nc -vz -w 5 <host> 443
```

ICMP may be blocked while TCP works. Do not conclude "host down" from a failed ping alone.

### 7. Check the firewall

```bash
nft list ruleset
iptables -S
iptables -L -n -v
ufw status verbose
firewall-cmd --list-all
```

Look at counters: a rule with zero packets is not the cause. Check both IPv4 and IPv6. Check the `INPUT`, `FORWARD`, and `OUTPUT` chains, plus NAT.

### 8. Test the application and TLS

```bash
curl -v --connect-timeout 5 https://example.com/health
curl -v --resolve example.com:443:203.0.113.10 https://example.com/
openssl s_client -connect example.com:443 -servername example.com </dev/null
```

`--resolve` bypasses DNS for one request. If it works, DNS is the problem. `openssl s_client` separates TLS from HTTP.

### 9. Capture packets

```bash
tcpdump -ni any host 203.0.113.10 and port 443 -c 50
tcpdump -ni any -w /tmp/capture.pcap 'tcp[tcpflags] & (tcp-syn|tcp-rst) != 0'
```

Look for SYN without SYN-ACK (firewall or routing), RST (closed port or reject rule), retransmissions (loss), and TLS alerts.

### 10. Check proxy and environment

```bash
env | grep -i proxy
curl -v --noproxy '*' https://example.com/
```

A stale `HTTP_PROXY` or `NO_PROXY` breaks tools inconsistently. Compare a tool that honors the proxy with one that does not.

## Gotchas

- DNS caching hides changes. Check the resolver, the local cache, and the TTL.
- Split-horizon DNS returns different answers inside and outside the network.
- IPv6 may be preferred and broken while IPv4 works. Test `curl -4` and `curl -6`.
- MTU issues appear as a hang after the TLS ClientHello. Test with `ping -M do -s 1472`.
- A service bound to `127.0.0.1` is not listening on the external interface.
- Containers and network namespaces have their own interfaces, routes, and firewall rules. Use `nsenter` or `docker exec` to inspect the right namespace.
- `ss` needs root to show other users' processes. `-p` may show nothing without privileges.
- `tcpdump` needs `CAP_NET_RAW` or root. Capture on `any` and filter aggressively.
- ICMP being blocked does not mean the host is unreachable.
- A firewall rule with a zero packet counter is not the rule dropping traffic.
- TLS SNI matters: connecting by IP without `-servername` can return the wrong certificate.
- Clock skew breaks TLS and Kerberos. Check `timedatectl`.

## Output contract

```markdown
## Symptom
<source, destination, port, error, scope, timeline>

## Evidence by layer
| Layer | Result | Command |
| --- | --- | --- |
| Link | up | ip -br link |
| Address | 10.0.0.5/24 | ip -br addr |
| Route | via 10.0.0.1 | ip route get |
| DNS | 203.0.113.10 | dig +short |
| Port | open | nc -vz |
| TLS | handshake ok | openssl s_client |
| HTTP | 200 | curl -v |

## Root cause
<one paragraph>

## Fix
<command or config change>

## Verification
<command and expected result>

## Follow-up
<monitoring, firewall rule, DNS record>
```

## Checklist

- [ ] Symptom and scope recorded.
- [ ] Link and address checked.
- [ ] Route checked.
- [ ] DNS checked with both `dig` and `getent`.
- [ ] Listening address and port checked.
- [ ] TCP reachability tested.
- [ ] Firewall rules and counters checked.
- [ ] TLS and application tested.
- [ ] Packet capture taken if needed.
- [ ] Root cause distinguished from symptom.
- [ ] Fix verified and follow-up recorded.

## Related skills

- `linux-performance-triage` when the network is slow rather than down.
- `linux-security-hardening` for firewall and SSH configuration.
- `container-log-diagnostics` when the failing service runs in a container.
