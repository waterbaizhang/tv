import os
import yaml
import requests
import geoip2.database
from urllib.request import urlopen
from collections import defaultdict

# GeoIP服务
geoip_reader = geoip2.database.Reader('/path/to/GeoLite2-Country.mmdb')  # 下载并指定路径

# 读取urls.txt文件
def read_urls_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# 解析yaml文件
def parse_yaml_from_url(url):
    try:
        response = urlopen(url)
        data = response.read().decode('utf-8')
        return yaml.safe_load(data)
    except Exception as e:
        print(f"Error downloading or parsing YAML from {url}: {e}")
        return None

# 根据IP获取国家名称
def get_country_from_ip(ip):
    try:
        response = geoip_reader.city(ip)
        return response.country.name
    except geoip2.errors.AddressNotFoundError:
        return "Unknown"

# 合并proxies节点
def merge_proxies(proxies_list):
    merged_proxies = defaultdict(dict)
    for proxies in proxies_list:
        if proxies is not None:
            for proxy in proxies.get('proxies', []):
                server = proxy.get('server')
                if server and server not in merged_proxies:
                    country_name = get_country_from_ip(server)  # 解析IP得到国家名
                    proxy['name'] = f"{country_name}_1"  # 生成名字
                    merged_proxies[server] = proxy
    return list(merged_proxies.values())

# 合并proxy-groups节点
def merge_proxy_groups(proxy_groups, proxies):
    return {
        'proxy-groups': proxy_groups,
        'proxies': proxies
    }

# 更新final.yaml文件
def update_final_yaml(merged_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(merged_data, f, allow_unicode=True, default_flow_style=False)

# 主执行流程
def main():
    urls = read_urls_file('urls.txt')
    proxies_list = []

    for url in urls:
        yaml_data = parse_yaml_from_url(url)
        if yaml_data:
            proxies_list.append(yaml_data)

    merged_proxies = merge_proxies(proxies_list)
    proxy_groups = merged_proxies  # 可自定义如何合并proxy-groups，暂时简单处理

    merged_data = merge_proxy_groups(proxy_groups, merged_proxies)
    update_final_yaml(merged_data, 'final.yaml')

if __name__ == "__main__":
    main()
