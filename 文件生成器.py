import os
import random
import string

def generate_random_file(filename, size_mb):
    size_bytes = size_mb * 1024 * 1024   # 1MB = 1024KB, 1KB = 1024B
    with open(filename, 'w') as f:
        while size_bytes > 0:
            chunk_size = min(size_bytes, 1024)  # 写入1KB的数据
            f.write(''.join(random.choices(string.ascii_letters + string.digits, k=1))*chunk_size)
            # chunk = ''.join(random.choices(string.ascii_letters + string.digits, k=chunk_size))
            size_bytes -= chunk_size

if __name__ == "__main__":
    for i in range(2):
        generate_random_file(str(i), 60)


    # open('5GB','wb').write(b'\x00'*2**30*5)
    #获取控制台长度
    # import os
    # rows, columns = os.popen('stty size', 'r').read().split()