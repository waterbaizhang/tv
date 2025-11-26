import yaml
import requests

subscription_file = "clash.txt"
output_file = "clash.yaml"

# 基础配置模板
base_config = {
    "port": 7890,
    "socks-port": 7891,
    "allow-lan": True,
    "mode": "Rule",
    "log-level": "info",
    "proxies": [],
    "proxy-groups": [],
    "rules": []
}

all_proxies = []
all_proxy_groups = []

# 读取 clash.txt 中每行 URL
with open(subscription_file, "r") as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

for url in urls:
    try:
        print(f"Fetching {url}...")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        cfg = yaml.safe_load(r.text)

        # 合并 proxies
        if "proxies" in cfg:
            all_proxies.extend(cfg["proxies"])

        # 合并 proxy-groups
        if "proxy-groups" in cfg:
            for group in cfg["proxy-groups"]:
                existing = next((g for g in all_proxy_groups if g["name"] == group["name"]), None)
                if existing:
                    existing["proxies"].extend(group.get("proxies", []))
                else:
                    all_proxy_groups.append(group)

        # 合并 rules
        if "rules" in cfg:
            base_config["rules"].extend(cfg["rules"])

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")

# 去重 proxies（通过 name 去重）
seen_names = set()
unique_proxies = []
for p in all_proxies:
    if p["name"] not in seen_names:
        unique_proxies.append(p)
        seen_names.add(p["name"])

base_config["proxies"] = unique_proxies
base_config["proxy-groups"] = all_proxy_groups

# 输出最终 YAML
with open(output_file, "w") as f:
    yaml.dump(base_config, f, sort_keys=False)

print(f"Generated {output_file} with {len(unique_proxies)} proxies")
