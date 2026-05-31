#include <iostream>
#include <cstring>
#include <ctime>

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <unistd.h>

// ─── Get current timestamp ───────────────────────────
std::string get_time() {
    time_t now = time(0);
    char buf[20];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
    return std::string(buf);
}

// ─── Parse and print one packet ─────────────────────
void process_packet(unsigned char* buffer, int size) {
    // первые байты — это IP заголовок
    struct iphdr* ip = (struct iphdr*)buffer;

    // источник и назначение
    struct in_addr src, dst;
    src.s_addr = ip->saddr;
    dst.s_addr = ip->daddr;

    std::string src_ip = inet_ntoa(src);
    std::string dst_ip = inet_ntoa(dst);

    // смотрим протокол
    if (ip->protocol == IPPROTO_TCP) {
        // TCP заголовок идёт после IP заголовка
        // ip->ihl — длина IP заголовка в 32-битных словах
        struct tcphdr* tcp = (struct tcphdr*)(buffer + ip->ihl * 4);

        int src_port = ntohs(tcp->source);
        int dst_port = ntohs(tcp->dest);

        // флаги TCP
        std::string flags = "";
        if (tcp->syn) flags += "SYN ";
        if (tcp->ack) flags += "ACK ";
        if (tcp->fin) flags += "FIN ";
        if (tcp->rst) flags += "RST ";

        std::cout << get_time()
                  << " | " << src_ip
                  << " | " << dst_ip
                  << " | TCP"
                  << " | " << dst_port
                  << " | " << flags
                  << std::endl;
        std::cout.flush();

    } else if (ip->protocol == IPPROTO_UDP) {
        struct udphdr* udp = (struct udphdr*)(buffer + ip->ihl * 4);

        int dst_port = ntohs(udp->dest);

        std::cout << get_time()
                  << " | " << src_ip
                  << " | " << dst_ip
                  << " | UDP"
                  << " | " << dst_port
                  << " | "
                  << std::endl;
        std::cout.flush();
    }
}

// ─── Main ────────────────────────────────────────────
int main() {
    // создаём сырой сокет — видит ВСЕ пакеты
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);

    if (sock < 0) {
        std::cerr << "Error: cannot create raw socket (run as root)" << std::endl;
        return 1;
    }

    std::cerr << "Sniffer started..." << std::endl;

    unsigned char buffer[65535];

    while (true) {
        // получаем пакет
        int size = recvfrom(sock, buffer, sizeof(buffer), 0, nullptr, nullptr);

        if (size < 0) {
            std::cerr << "Error receiving packet" << std::endl;
            continue;
        }

        process_packet(buffer, size);
    }

    close(sock);
    return 0;
}
