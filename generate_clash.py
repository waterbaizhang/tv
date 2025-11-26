import yaml
import requests

subscription_file = "clash.txt"
output_file = "clash.yaml"

# 基础配置
base_config = {
    "port": 7890,
    "socks-port": 7891,
    "allow-lan": True,
    "mode": "Rule",
    "log-level": "info",
    "proxies": [],
    "proxy-groups": []
}

proxies = []

with open(subscription_file, "r") as f:
    for line in f:
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            # 解析 YAML 并添加 proxies
            cfg = yaml.safe_load(r.text)
            if "proxies" in cfg:
                proxies.extend(cfg["proxies"])
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

base_config["proxies"] = proxies

# 输出合并后的订阅文件
with open(output_file, "w") as f:
    yaml.dump(base_config, f, sort_keys=False)

print(f"Generated {output_file} with {len(proxies)} proxies")
