#!/usr/bin/env bash
set -x

echo "Listing iptables rules before flushing"
sysctl net.ipv4.ip_forward
/usr/sbin/iptables -L -v -n
/usr/sbin/iptables-save -t nat
/usr/sbin/iptables-save -t raw
/usr/sbin/iptables-save -t mangle
/usr/sbin/iptables-save -t filter
/usr/sbin/ip rule show

echo "Starting the flush aws-vpc-cni policy rules..."

# Set FORWARD action to ACCEPT so outgoing packets can go through POSTROUTING chains.
echo "Setting default FORWARD action to ACCEPT..."
#iptables -P FORWARD ACCEPT

# Make sure ip_forward sysctl is set to allow ip forwarding.
sysctl -w net.ipv4.ip_forward=1

#echo "Flushing all the aws-vpc-cni iptables chains in the nat table..."
#/usr/sbin/iptables-save -t nat | /usr/bin/grep -oP '^:(AWS|CNI|KUBE)[^ ]+' | /usr/bin/tr -d ':' | while /usr/bin/read line; do /usr/sbin/iptables -t nat -F ${line}; done

#echo "Flushing all the aws-vpc-cni iptables chains in the mangle table..."
#/usr/sbin/iptables-save -t mangle | /usr/bin/grep -oP '^:(AWS|CNI|KUBE)[^ ]+' | /usr/bin/tr -d ':' | while /usr/bin/read line; do /usr/sbin/iptables -t mangle -F ${line}; done

#echo "Flushing all the aws-vpc-cni iptables chains in the filter table..."
#/usr/sbin/iptables-save -t filter | /usr/bin/grep -oP '^:(AWS|CNI|KUBE)[^ ]+' | /usr/bin/tr -d ':' | while /usr/bin/read line; do /usr/sbin/iptables -t filter -F ${line}; done

#echo "Cleaning up aws-vpc-cni rules from the nat table..."
#/usr/sbin/iptables-save -t nat
#/usr/sbin/iptables-save -t nat | /usr/bin/grep -e '--comment' | /usr/bin/cut -c 3- | /usr/bin/sed 's/^ *//;s/ *$//' | /usr/bin/xargs -l1 /usr/sbin/iptables -t nat -D

#echo "Cleaning up aws-vpc-cni rules from the mangle table..."
#/usr/sbin/iptables-save -t mangle
#/usr/sbin/iptables-save -t mangle | /usr/bin/grep -e '--comment' | /usr/bin/cut -c 3- | /usr/bin/sed 's/^ *//;s/ *$//' | /usr/bin/xargs -l1 /usr/sbin/iptables -t mangle -D

#echo "Cleaning up aws-vpc-cni rules from the filter table..."
#/usr/sbin/iptables-save -t filter
#/usr/sbin/iptables-save -t filter | /usr/bin/grep -e '--comment' | /usr/bin/cut -c 3- | /usr/bin/sed 's/^ *//;s/ *$//' | /usr/bin/xargs -l1 /usr/sbin/iptables -t filter -D

#echo "Cleaning up aws-vpc-cni rules from the raw table..."
#/usr/sbin/iptables-save -t raw

#echo "Listing iptables rules after flushing"
#/usr/sbin/iptables -L -v -n

#echo "Cleaning up aws-vpc-cni routes..."
#/usr/sbin/ip route show table all
#/usr/sbin/ip route show table all | /usr/bin/grep -P 'eth(1|2)' | /usr/bin/grep -o "table \w*" | /usr/bin/grep -v local | /usr/bin/sort -u | /usr/bin/xargs -l1 /usr/sbin/ip route flush

#echo "Cleaning up aws-vpc-cni ip rules"
#/usr/sbin/ip rule del prio 512
#/usr/sbin/ip rule del prio 1024
#/usr/sbin/ip rule del prio 1536
#/usr/sbin/ip route flush cache
#/usr/sbin/ip rule show

/usr/sbin/iptables -t mangle -A PREROUTING -i eth0 -m comment --comment "NXTLYTICS, hairpin all incoming" -j CONNMARK --set-xmark 0x80/0x80
