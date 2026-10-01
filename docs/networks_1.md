# Introduction to Internet Protocols (Part I)

> Author: Ruan Yifeng. Source: [the original article on Ruan Yifeng's blog](https://www.ruanyifeng.com/blog/2012/05/internet_protocol_suite_part_i.html), published on 2012-05-31. This is this site's English translation for study; the article retains the original historical context and simplified explanations.
>
> Last maintained: 2026-10-01. This date records maintenance of the content on this site. The article introduces fundamental concepts through historical examples, and its technical descriptions reflect the original publication date. External links have not all been individually verified. The original illustrations are retained and may contain Chinese labels.

![Introduction to the Internet and the protocols that connect computers.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052901.jpg)

*Figure: Introduction to the Internet and the protocols that connect computers.*

We use the Internet every day. Have you ever wondered how it works?

Billions of computers around the world are connected and communicate with one another. A network interface card in Shanghai sends a signal, and another network interface card in Los Angeles receives it, even though neither knows the other's physical location. Isn't that remarkable?

At the heart of the Internet is a series of protocols, collectively called the Internet Protocol Suite. They define in detail how computers connect and form networks. Understanding these protocols means understanding the principles behind the Internet.

The following are my study notes. These protocols are so complex and extensive that I wanted to put together a concise framework to help me understand them as a whole. To keep the explanation accessible, I have made many simplifications. Some details are incomplete or imprecise, but the explanation should still convey how the Internet works.

\=================================================

## **1. Overview**

### **1.1 The Five-Layer Model**

The Internet is implemented in several layers. Each layer has its own function, much like a building in which each floor is supported by the one below.

Users interact only with the topmost layer, without being aware of the layers underneath. To understand the Internet, we need to start at the bottom and work upward through the function of each layer.

There are different models for dividing the layers: some have seven layers and others have four. I find a five-layer model easier to explain.

![The five layers, from bottom to top: Physical, Link, Network, Transport, and Application.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052902.png)

*Figure: The five layers, from bottom to top: Physical, Link, Network, Transport, and Application.*

As shown above, the bottom layer is the Physical Layer and the top layer is the Application Layer. The three layers between them, from bottom to top, are the Link Layer, Network Layer, and Transport Layer. The lower a layer is, the closer it is to the hardware; the higher it is, the closer it is to the user.

The names themselves are not particularly important. What matters here is that the Internet is divided into several layers.

### **1.2 Layers and Protocols**

Each layer serves a particular function. To implement those functions, everyone must follow common rules.

A set of rules that everyone follows is called a protocol.

Each layer of the Internet defines many protocols. Together, these are called the Internet Protocol Suite, which forms the core of the Internet. Explaining the function of each layer therefore largely means introducing its main protocols.

## **2. The Physical Layer**

Let's begin with the bottom layer.

What is the first step in networking computers? Connecting them, of course. We can use fiber-optic cables, electrical cables, twisted-pair cables, radio waves, and other means.

![The Physical Layer connects computers and carries signals representing bits.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052903.png)

*Figure: The Physical Layer connects computers and carries signals representing bits.*

**This is the Physical Layer: the physical means of connecting computers. It primarily specifies the network's electrical characteristics and is responsible for transmitting electrical signals representing 0s and 1s.**

## **3. The Link Layer**

### **3.1 Definition**

A stream of 0s and 1s has no meaning on its own. We need rules for interpreting it: how many electrical signals make up a group, and what does each bit mean?

**This is the function of the Link Layer. It sits above the Physical Layer and determines how 0s and 1s are grouped.**

### **3.2 Ethernet**

In the early days, each company had its own way of grouping electrical signals. Gradually, a protocol called [Ethernet](https://zh.wikipedia.org/wiki/%E4%BB%A5%E5%A4%AA%E7%BD%91) became dominant.

Ethernet specifies that a group of electrical signals forms a data packet called a frame. Each frame consists of two parts: a header and data.

![An Ethernet frame contains a header and a data portion.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052904.png)

*Figure: An Ethernet frame contains a header and a data portion.*

The header contains information about the packet, such as its sender, recipient, and data type. The data portion contains the packet's actual content.

The header is fixed at 18 bytes. The data portion is at least 46 bytes and at most 1500 bytes. The complete frame is therefore between 64 and 1518 bytes long. If the data is too long, it must be split into multiple frames for transmission.

### **3.3 MAC Addresses**

As mentioned above, an Ethernet packet's header includes information about its sender and recipient. How are they identified?

Ethernet requires all devices connected to the network to have a network interface card. Packets travel from one network interface card to another. The addresses of these cards serve as the packet's sending and receiving addresses, and are called MAC addresses.

![A network interface card provides the hardware interface to the network.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052905.jpg)

*Figure: A network interface card provides the hardware interface to the network.*

Each network interface card receives a globally unique MAC address when it is manufactured. The address is 48 bits long and is usually written as 12 hexadecimal digits.

![A MAC address consists of 12 hexadecimal digits: 6 for the manufacturer and 6 for the card identifier.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052906.png)

*Figure: A MAC address consists of 12 hexadecimal digits: 6 for the manufacturer and 6 for the card identifier.*

The first 6 hexadecimal digits identify the manufacturer, and the last 6 are a serial number assigned by that manufacturer. A MAC address lets us identify a network interface card and the path a packet needs to take.

### **3.4 Broadcasting**

Defining addresses is only the first step. Several other steps are needed.

First, how does one network interface card learn another card's MAC address?

A protocol called ARP solves this problem. We will discuss it later. For now, remember that an Ethernet packet needs the recipient's MAC address before it can be sent.

Second, even with a MAC address, how does the system deliver a packet to the correct recipient?

Ethernet uses a rather simple method in this explanation: instead of sending the packet directly to the recipient, it sends it to every computer on the local network and lets each computer decide whether it is the recipient.

![Broadcasting in the original simplified model: computer 1 sends to computer 2, while computers 3, 4, and 5 also receive the frame.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052907.png)

*Figure: Broadcasting in the original simplified model: computer 1 sends to computer 2, while computers 3, 4, and 5 also receive the frame.*

In the figure above, computer 1 sends a packet to computer 2. Computers 3, 4, and 5 on the same subnet also receive it. They read the header, find the recipient's MAC address, and compare it with their own MAC address. If the addresses match, they accept the packet for further processing; otherwise, they discard it. This method of transmission is called broadcasting.

With a packet format, MAC addresses for network interface cards, and broadcasting as a transmission method, the Link Layer can transfer data between multiple computers.

## **4. The Network Layer**

### **4.1 Why the Network Layer Is Needed**

Ethernet uses MAC addresses to send data. In theory, a network interface card in Shanghai could locate one in Los Angeles using only MAC addresses; it would be technically possible.

However, this approach has a major drawback. Ethernet broadcasting gives every member of the network a copy of each packet. This is inefficient and limited to the sender's subnet. If two computers are on different subnets, a broadcast cannot pass between them. This design makes sense: it would be disastrous if every computer on the Internet received every packet.

The Internet is a huge network made up of countless subnets. It is almost impossible to imagine that computers in Shanghai and Los Angeles would be on the same subnet.

![Separate subnets need routing to exchange packets.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052914.png)

*Figure: Separate subnets need routing to exchange packets.*

We therefore need a way to distinguish which MAC addresses belong to the same subnet and which do not. Within the same subnet, packets can be broadcast; otherwise, they must be routed. Routing means deciding how to distribute packets to different subnets. It is a large topic and is beyond the scope of this article. Unfortunately, a MAC address cannot tell us this: it relates to the manufacturer, not to the network where the card is located.

**This led to the Network Layer. Its function is to introduce another set of addresses so that we can tell whether computers belong to the same subnet. These addresses are called network addresses.**

Once the Network Layer is introduced, each computer has two kinds of address: a MAC address and a network address. There is no inherent relationship between them. The MAC address is associated with the network interface card, whereas the network address is assigned by an administrator. Their pairing is incidental.

The network address helps us identify the computer's subnet, while the MAC address delivers the packet to the target network interface card within that subnet. Logically, we must therefore deal with the network address first, then the MAC address.

### **4.2 IP**

The protocol that specifies network addresses is called IP. The addresses it defines are called IP addresses.

At the time of the original article, version 4 of IP, or IPv4, was widely used. It defines a network address as a 32-bit value.

![An IPv4 address consists of four groups of 8 bits, written as four decimal numbers.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052908.png)

*Figure: An IPv4 address consists of four groups of 8 bits, written as four decimal numbers.*

By convention, an IP address is written as four decimal numbers separated by dots, ranging from 0.0.0.0 to 255.255.255.255.

Every computer on the Internet is assigned an IP address. The address has two parts: the first represents the network, and the second represents the host. For example, 172.16.254.1 is a 32-bit address. If its first 24 bits, 172.16.254, represent the network, then its last 8 bits, the final 1, represent the host. Computers on the same subnet must have matching network portions, so 172.16.254.2 would be on the same subnet as 172.16.254.1 in this example.

The problem is that an IP address alone does not tell us which part represents the network. For 172.16.254.1, we cannot tell whether the network portion consists of the first 24 bits, the first 16 bits, or even the first 28 bits just by looking at the address.

How can we use IP addresses to determine whether two computers belong to the same subnet? We need another parameter: the subnet mask.

A subnet mask describes the subnet's structure. It has the same form as an IP address: a 32-bit binary number. All bits in the network portion are 1, and all bits in the host portion are 0. For example, if the network portion of 172.16.254.1 is the first 24 bits and the host portion is the last 8 bits, its subnet mask is 11111111.11111111.11111111.00000000, or 255.255.255.0 in decimal notation.

Once we know the subnet mask, we can determine whether any two IP addresses belong to the same subnet. We perform a bitwise AND between each IP address and the subnet mask: the result is 1 only when both bits are 1, and is 0 otherwise. We then compare the results. Matching results mean the addresses are on the same subnet; different results mean they are not.

For example, suppose 172.16.254.1 and 172.16.254.233 both have the subnet mask 255.255.255.0. Are they on the same subnet? Applying the AND operation to each address produces 172.16.254.0 in both cases, so they are.

To summarize, the article describes two main purposes of IP: assigning an IP address to each computer and determining which addresses belong to the same subnet.

### **4.3 IP Packets**

Data sent according to IP takes the form of IP packets. Naturally, an IP packet includes IP address information.

Earlier, however, we saw that Ethernet packets contain MAC addresses and have no field for IP addresses. Do we need to change the Ethernet format to add such a field?

No. We can place the IP packet directly inside the Ethernet packet's data portion, so the Ethernet specification does not need to change. This illustrates the benefit of the Internet's layered structure: changes at a higher layer do not require changes to the structure of the lower layer.

More specifically, an IP packet also consists of a header and data.

![An IP packet has its own header and data portion.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052909.png)

*Figure: An IP packet has its own header and data portion.*

The header mainly contains information such as the version, length, and IP addresses. The data portion holds the packet's actual content. Once the IP packet is placed inside an Ethernet packet, the Ethernet packet looks like this:

![An IP packet is carried inside the data portion of an Ethernet frame.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052910.png)

*Figure: An IP packet is carried inside the data portion of an Ethernet frame.*

An IP packet's header is between 20 and 60 bytes long, and the complete packet can be at most 65,535 bytes. In theory, its data portion can therefore be at most 65,515 bytes. As mentioned above, an Ethernet packet's data portion can be no longer than 1500 bytes. If an IP packet exceeds 1500 bytes, it must be split into several Ethernet packets and sent separately.

### **4.4 ARP**

There is one final point to explain about the Network Layer.

Because an IP packet is sent inside an Ethernet packet, we need two addresses: the other party's MAC address and its IP address. Usually, we already know its IP address, as we will explain later, but we do not know its MAC address.

We therefore need a mechanism for obtaining a MAC address from an IP address.

There are two cases. First, if the hosts are on different subnets, we cannot obtain the remote host's MAC address this way. Instead, we send the packet to a gateway connecting the subnets and let the gateway handle it.

Second, if the hosts are on the same subnet, we can use ARP to obtain the other host's MAC address. ARP sends a packet, carried inside an Ethernet packet, containing the IP address of the host being queried. The destination MAC address is set to FF:FF:FF:FF:FF:FF, indicating a broadcast address. Every host on the subnet receives the packet, extracts the IP address, and compares it with its own. A host with a matching address responds with its MAC address; other hosts discard the packet.

With ARP, we can obtain the MAC address of a host on the same subnet and send packets to any host within that subnet.

## **5. The Transport Layer**

### **5.1 Why the Transport Layer Is Needed**

With MAC addresses and IP addresses, we can establish communication between any two hosts on the Internet.

The next problem is that many programs on a single host may need the network at the same time. For example, you may be browsing the web while chatting with a friend online. When a packet arrives from the Internet, how do we know whether it contains web page data or chat data?

We need another parameter that identifies the program, or process, for which the packet is intended. This parameter is called a port. In this simplified explanation, it is a number identifying a program that uses the network interface. Each packet is sent to a particular port on the host, allowing different programs to receive the data they need.

A port is an integer between 0 and 65535, which fits in 16 bits. Ports from 0 to 1023 are reserved by the system, so users select ports greater than 1023. Whether browsing the web or chatting online, an application selects a port at random and contacts the corresponding port on the server.

**The Transport Layer establishes port-to-port communication. The Network Layer, by comparison, establishes host-to-host communication. Once we identify a host and a port, we can communicate between programs.** Unix systems therefore refer to the host-and-port combination as a socket. Sockets make it possible to develop network applications.

### **5.2 UDP**

We now need to include port information in the packet, which requires another protocol. The simplest implementation is called UDP. Its format essentially adds port numbers before the data.

A UDP packet also consists of a header and data.

![A UDP packet has a header identifying the ports, followed by application data.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052911.png)

*Figure: A UDP packet has a header identifying the ports, followed by application data.*

The header primarily identifies the source and destination ports, and the data portion contains the actual content. The entire UDP packet is then placed inside an IP packet's data portion. As explained earlier, the IP packet itself is carried inside an Ethernet packet. The complete Ethernet packet now looks like this:

![Encapsulation: an Ethernet frame carries an IP packet, which carries a UDP packet.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052912.png)

*Figure: Encapsulation: an Ethernet frame carries an IP packet, which carries a UDP packet.*

A UDP packet is very simple. Its header is only 8 bytes long, and its total length cannot exceed 65,535 bytes; the original explanation describes it as fitting inside an IP packet.

### **5.3 TCP**

UDP's advantage is its simplicity and ease of implementation. Its drawback is limited reliability: once a packet is sent, the sender cannot tell whether the other party has received it.

TCP was developed to address this problem and improve network reliability. It is a complex protocol, but, as a rough analogy, we can think of it as UDP with acknowledgments. Each packet sent requires an acknowledgment. If a packet is lost, no acknowledgment arrives, and the sender knows that it must retransmit the packet.

TCP can therefore prevent data from being lost. Its disadvantages are a complex process, a difficult implementation, and greater resource consumption.

Like UDP packets, TCP packets are embedded in the data portion of IP packets. The original article describes TCP data as having no overall length limit and therefore theoretically being arbitrarily long. For network efficiency, it says that individual TCP packets are usually kept no longer than an IP packet so that they do not need to be split further.

## **6. The Application Layer**

Once an application receives data from the Transport Layer, it must interpret that data. Because the Internet has an open architecture, data comes from many different sources. Its format must be agreed on in advance; otherwise, it cannot be interpreted.

**The Application Layer defines the formats of application data.**

For example, TCP can carry data for many kinds of application, including email, the World Wide Web, and FTP. Different protocols are needed to specify the formats of email, web pages, and FTP data. These application protocols make up the Application Layer.

This is the highest layer and the one that directly faces users. Its data is placed in the data portion of a TCP packet. The Ethernet packet now looks like this:

![The complete layered structure: Ethernet contains IP, IP contains TCP, and TCP carries application data.](https://www.ruanyifeng.com/blogimg/asset/201205/bg2012052913.png)

*Figure: The complete layered structure: Ethernet contains IP, IP contains TCP, and TCP carries application data.*

We have now covered all five layers of the Internet, from bottom to top. This explains how the Internet is organized from a system perspective. In [the next article](https://www.ruanyifeng.com/blog/2012/06/internet_protocol_suite_part_ii.html), I will reverse the perspective and follow the layers from top to bottom to see how they work together to complete a network data exchange for a user.

(End)
