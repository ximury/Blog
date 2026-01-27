import re


class IPUtils:
    @staticmethod
    def ip4_to_int(ip):
        # 1000000 2.7s
        ip4_to_int = sum([256**j * int(i) for j, i in enumerate(ip.split(".")[::-1])])
        return ip4_to_int

    @staticmethod
    def ip_to_number(ip_address):
        # 1000000 1.2s
        ip = str(ip_address).split(".")
        ip_binary = (
            (int(ip[0]) << 24) + (int(ip[1]) << 16) + (int(ip[2]) << 8) + int(ip[3])
        )
        return ip_binary

    @staticmethod
    def number_to_ip(number):
        ip = ".".join([str(number // (256**i) % 256) for i in range(3, -1, -1)])
        return ip

    @staticmethod
    def get_ip_mask_range(ip, mask, ip_utils_cls):
        """
        获取掩码ip的整数范围(包括网络地址和广播地址)
        Args:
            ip:
            mask:
            ip_utils_cls:

        Returns:

        """
        if mask:
            # 子网掩码
            sub_mask = "0b{0:0<32}".format(int("".join(["1" for i in range(mask)])))
            # 网络地址
            network = ip_utils_cls.ip_to_number(ip) & int(sub_mask, 2)  # 与运算，获取网络地址
            # 主机地址
            host = "0b{0:0>32}".format(int("".join(["1" for i in range(32 - mask)])))
            # 广播地址
            broad = network | int(host, 2)  # 或运算，将主机号置为1
            print("network:{}, broad:{}".format(network, broad))
            start_ip_int, end_ip_int = network, broad
        else:
            start_ip_int = end_ip_int = ip_utils_cls.ip_to_number(ip)
        return start_ip_int, end_ip_int

    @staticmethod
    def get_ip_range_by_net_segment(net_segment, ip_utils_cls):
        data = net_segment.split("/")
        start_ip_int, end_ip_int = ip_utils_cls.get_ip_mask_range(
            data[0], int(data[1]), ip_utils_cls
        )
        return start_ip_int, end_ip_int

    @staticmethod
    def exchange_mask_to_int(mask: int):
        bin_arr = ["0" for i in range(32)]
        for i in range(mask):
            bin_arr[i] = "1"
        tmp_mask = ["".join(bin_arr[i * 8 : i * 8 + 8]) for i in range(4)]
        tmp_mask = [str(int(tmp_str, 2)) for tmp_str in tmp_mask]
        return ".".join(tmp_mask)

    @staticmethod
    def get_mask(cidr: str):
        mask = cidr.split("/")[1]
        return IPUtils.exchange_mask_to_int(int(mask))

    @staticmethod
    def is_ipv4(ip):
        check = re.search(
            "^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$",
            ip,
        )
        if check:
            return True
        else:
            return False

    @staticmethod
    def is_net_segment(ip, ip_utils_cls):
        data = ip.split("/")
        if not len(data) == 2:
            return False
        if not ip_utils_cls.is_ipv4(data[0]):
            return False
        if 0 <= int(data[1]) <= 32:
            return True
        else:
            return False

    @staticmethod
    def check_ip(ip):
        data = ip.split("/")
        if len(data) == 1:
            res = IPUtils.is_ipv4(ip)
            if res:
                return True, ""
            else:
                return False, "IP格式错误"
        elif len(data) == 2:
            if 0 <= int(data[1]) <= 32:
                return True, ""
            else:
                return False, "子网掩码错误"
        else:
            return False, "IP格式错误"


if __name__ == "__main__":
    ip_utils = IPUtils()
    ip = "172.17.129.56"
    num = ip_utils.ip_to_number(ip)
    print(f"num: {num}")
    ip1 = ip_utils.number_to_ip(num)
    print(f"IP: {ip1}")
    net_segment = "172.17.129.56/31"
    ip_range = ip_utils.get_ip_range_by_net_segment(net_segment, ip_utils)
    print(f"IP range: {ip_range}")
    ip_start = ip_utils.number_to_ip(ip_range[0])
    ip_end = ip_utils.number_to_ip(ip_range[1])
    print(f"start: {ip_start}, end: {ip_end}")

