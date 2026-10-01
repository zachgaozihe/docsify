# Introduction to Internet Protocols (Part II)

> Author: Ruan Yifeng. Source: [the original article on Ruan Yifeng's blog](https://www.ruanyifeng.com/blog/2012/06/internet_protocol_suite_part_ii.html), published on 2012-06-11. This is this site's English translation for study; the article retains the original historical context and simplified explanations.
>
> Last maintained: 2026-10-01. This date records maintenance of the content on this site. The article introduces fundamental concepts through historical examples, and its technical descriptions reflect the original publication date. External links have not all been individually verified. The original illustrations are retained and may contain Chinese labels.

[The previous article](networks_1.md) explained the overall design of the Internet and the thinking behind each protocol layer, working from the bottom upward.

That was the designer's perspective. Today, I want to switch to the user's perspective and see how a user interacts with these protocols from the top down.

\==============================================================

![A visual introduction to following Internet protocols from the user's perspective.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061109.jpg)

*Figure: A visual introduction to following Internet protocols from the user's perspective.*

(Continued from Part I)

## **7. A Brief Recap**

Let's briefly review what we have covered.

We now know that network communication consists of exchanging data packets. Computer A sends a packet to computer B; computer B receives it and replies with another packet. This lets the two computers communicate. The basic packet structure looks like this:

![The complete layered structure: Ethernet contains IP, IP contains TCP, and TCP carries application data.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052913.png)

*Figure: The complete layered structure: Ethernet contains IP, IP contains TCP, and TCP carries application data.*

To send this packet, we need two addresses:

> * The other party's MAC address
> * The other party's IP address

These addresses allow the packet to reach its recipient. As discussed earlier, however, MAC addresses have a limitation: if the computers are on different subnets, we cannot obtain the remote computer's MAC address this way. The packet must be forwarded through a gateway.

![Computer 1 on subnet A reaches computer 4 on subnet B through gateways A and B.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061101.jpg)

*Figure: Computer 1 on subnet A reaches computer 4 on subnet B through gateways A and B.*

In the figure above, computer 1 wants to send a packet to computer 4. It first checks whether computer 4 belongs to the same subnet. Finding that it does not, using the method described later, it sends the packet to gateway A. Gateway A uses routing protocols to determine that computer 4 is on subnet B and forwards the packet to gateway B. Gateway B then forwards it to computer 4.

To send a packet to gateway A, computer 1 needs gateway A's MAC address. The packet's destination addresses therefore depend on the situation:

<table><tbody><tr><td>Situation</td><td>Packet addresses</td></tr><tr><td>Same subnet</td><td>The other party's MAC address and IP address</td></tr><tr><td>Different subnets</td><td>The gateway's MAC address and the other party's IP address</td></tr></tbody></table>

Before sending a packet, the computer must determine whether the recipient is on the same subnet and select the appropriate MAC address. Next, we will see how this happens in practice.

## **8. Setting Up an Internet Connection**

### **8.1 Static IP Addresses**

Suppose you buy a new computer, plug in a network cable, and turn it on. Can it access the Internet immediately?

![An illustration accompanying the discussion of configuring a new computer's Internet connection.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061110.jpg)

*Figure: An illustration accompanying the discussion of configuring a new computer's Internet connection.*

Usually, some configuration is required. Sometimes an administrator or ISP provides the following four parameters. Entering them into the operating system allows the computer to connect:

> * The computer's IP address
> * The subnet mask
> * The gateway's IP address
> * The DNS server's IP address

The figure below shows the settings window in Windows.

![The Windows network settings provide fields for the IP address, subnet mask, default gateway, and DNS server.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061111.png)

*Figure: The Windows network settings provide fields for the IP address, subnet mask, default gateway, and DNS server.*

In the original explanation, all four parameters are required; we will explain their roles later. Because these values are fixed, the computer uses the same IP address each time it starts. This is called connecting with a static IP address.

These settings can be intimidating for ordinary users. Also, if one computer keeps an IP address permanently, other computers cannot use that address, which reduces flexibility. For these two reasons, most users connect with a dynamic IP address.

### **8.2 Dynamic IP Addresses**

A dynamic IP address is assigned automatically after the computer starts, without manual configuration. The protocol used for this is [DHCP](https://zh.wikipedia.org/zh/DHCP).

In this explanation, a computer on each subnet manages the subnet's IP addresses. This computer is called the DHCP server. A new computer joining the network sends it a DHCP request packet to obtain an IP address and the related network parameters.

Earlier, we said that a computer needs the other party's MAC address and IP address to send a packet within the same subnet. But a computer that has just joined the network knows neither address. How can it send a packet?

DHCP provides a clever solution.

### **8.3 DHCP**

First, DHCP is an Application Layer protocol built on UDP, so the complete packet has this structure:

![A DHCP message is carried by UDP inside an IP packet and an Ethernet frame.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061102.png)

*Figure: A DHCP message is carried by UDP inside an IP packet and an Ethernet frame.*

1. The Ethernet header at the front specifies the sender's MAC address, which is the local network interface card's address, and the recipient's MAC address, which belongs to the DHCP server. Because the recipient's address is not yet known, a broadcast address is used: FF-FF-FF-FF-FF-FF.

2. The IP header specifies the source and destination IP addresses. At this point, the local computer knows neither. It therefore sets the source address to 0.0.0.0 and the destination address to 255.255.255.255.

3. The UDP header specifies the source and destination ports. DHCP defines these as port 68 for the sender and port 67 for the recipient.

Once constructed, the packet can be sent. It is broadcast over Ethernet, so every computer on the subnet receives it. Because its destination MAC address is FF-FF-FF-FF-FF-FF, the MAC address alone does not identify a particular recipient. Each receiving computer must also examine the IP addresses. The DHCP server recognizes the source address 0.0.0.0 and destination address 255.255.255.255 as part of a request for it to handle, while other computers can discard the packet.

Next, the DHCP server reads the request data, assigns an IP address, and sends a DHCP response packet. The response has a similar structure. In the article's example, the Ethernet header contains the two network interface cards' MAC addresses. The IP header contains the DHCP server's IP address as the source and 255.255.255.255 as the destination. The UDP header specifies source port 67 and destination port 68. The assigned IP address and the network's parameters are included in the data portion.

When the new computer receives this response, it learns its IP address, subnet mask, gateway address, DNS server, and other parameters.

### **8.4 Connection Settings: A Summary**

The key point of this section is that, whether an IP address is static or dynamic, the first step in connecting to the Internet is to obtain four parameters. They are worth repeating:

> * The computer's IP address
> * The subnet mask
> * The gateway's IP address
> * The DNS server's IP address

With these values, the computer can surf the Internet. Next, let's look at an example of how Internet protocols work when a user visits a web page.

## **9. An Example: Visiting a Web Page**

### **9.1 The Local Computer's Parameters**

Assume that the user has completed the steps in the previous section and configured the following network parameters:

> * The computer's IP address: 192.168.1.100
> * Subnet mask: 255.255.255.0
> * Gateway IP address: 192.168.1.1
> * DNS server IP address: 8.8.8.8

The user opens a browser and enters www.google.com in the address bar to visit Google.

![The browser requests www.google.com after the local computer has been configured.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061103.png)

*Figure: The browser requests www.google.com after the local computer has been configured.*

This means the browser must send Google a packet containing a request for a web page.

### **9.2 DNS**

We know that sending a packet requires the recipient's IP address. At present, however, we know only the domain name www.google.com, not its IP address.

[DNS](https://en.wikipedia.org/wiki/Domain_Name_System) can translate this domain name into an IP address. Since the DNS server's address is 8.8.8.8, we send a DNS packet to that address on port 53.

![DNS resolves the name www.google.com to the historical example IP address 172.194.72.105.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061105.png)

*Figure: DNS resolves the name www.google.com to the historical example IP address 172.194.72.105.*

The DNS server responds with Google's IP address, which is 172.194.72.105 in this historical example. We now know the recipient's IP address.

### **9.3 The Subnet Mask**

Next, we need to determine whether this IP address belongs to the same subnet. This requires the subnet mask.

The subnet mask is 255.255.255.0. The local computer performs a bitwise AND between this mask and its own IP address, 192.168.1.100: a result bit is 1 if both input bits are 1, and is 0 otherwise. The result is 192.168.1.0. It performs the same AND operation on Google's IP address, 172.194.72.105, obtaining 172.194.72.0. Because the results differ, Google and the local computer are on different subnets.

To send packets to Google, we must therefore forward them through gateway 192.168.1.1. The destination MAC address will be the gateway's MAC address.

### **9.4 The Application Layer Protocol**

The example uses HTTP for browsing the web. The complete packet has the following structure:

![An HTTP request is carried by TCP, inside IP and Ethernet.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061106.png)

*Figure: An HTTP request is carried by TCP, inside IP and Ethernet.*

The HTTP portion looks something like this:

```text
GET / HTTP/1.1
Host: www.google.com
Connection: keep-alive
User-Agent: Mozilla/5.0 (Windows NT 6.1) ......
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip,deflate,sdch
Accept-Language: zh-CN,zh;q=0.8
Accept-Charset: GBK,utf-8;q=0.7,*;q=0.3
Cookie: ... ...
```

Assume this portion is 4960 bytes long. It will be embedded in a TCP packet.

### **9.5 TCP**

The TCP packet needs port numbers. Google's default HTTP port is 80. The local computer's sending port is a randomly generated integer between 1024-65535; assume it is 51775.

The TCP header is 20 bytes long. Including the embedded HTTP data, the total length is 4980 bytes.

### **9.6 IP**

The TCP packet is then embedded in an IP packet. This packet needs both parties' IP addresses, which we already know: the source is 192.168.1.100, the local computer, and the destination is 172.194.72.105, Google.

The IP header is 20 bytes long. Including the embedded TCP packet, the total length is 5000 bytes.

### **9.7 Ethernet**

Finally, the IP packet is embedded in an Ethernet packet. The Ethernet packet needs both parties' MAC addresses. The source is the local network interface card's MAC address, and the destination is the MAC address of gateway 192.168.1.1, obtained through ARP.

The data portion of an Ethernet packet can be at most 1500 bytes, but our IP packet is 5000 bytes long. The IP packet must therefore be split into four packets. Because each has its own 20-byte IP header, the four IP packet lengths are 1500, 1500, 1500, and 560 bytes in the original example.

![The original fragmentation example divides a 5000-byte IP packet into packets of 1500, 1500, 1500, and 560 bytes, including their IP headers.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061107.png)

*Figure: The original fragmentation example divides a 5000-byte IP packet into packets of 1500, 1500, 1500, and 560 bytes, including their IP headers.*

### **9.8 The Server's Response**

After being forwarded through several gateways, these four Ethernet packets reach Google's server at 172.194.72.105.

Using the ordering information in the IP headers, Google reassembles the four packets and extracts the complete TCP packet. It reads the HTTP request inside, produces an HTTP response, and sends it back using TCP.

When the local computer receives the HTTP response, it can display the web page. This completes a network communication exchange.

![The browser displays the web page after receiving the HTTP response.](https://www.ruanyifeng.com/blogimg/asset/201206/bg2012061104.jpg)

*Figure: The browser displays the web page after receiving the HTTP response.*

This concludes the example. Although simplified, it gives a broad picture of the complete communication process using Internet protocols.

(End)
