import requests
import json
import time
import sys
import os
import re
from typing import List, Dict, Any, Optional

def get_version():
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, "version_info.txt")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"StringStruct\(u'ProductVersion',\s*u'([^']+)'\)", content)
                if match:
                    return match.group(1)
        
        return "0.0.0"
    except Exception as e:
        return "未知版本"

def show_muse_banner():
    banner = r"""
          _____                    _____                    _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \         
        /::\____\                /::\____\                /::\    \                /::\    \        
       /::::|   |               /:::/    /               /::::\    \              /::::\    \       
      /:::::|   |              /:::/    /               /::::::\    \            /::::::\    \      
     /::::::|   |             /:::/    /               /:::/\:::\    \          /:::/\:::\    \     
    /:::/|::|   |            /:::/    /               /:::/__\:::\    \        /:::/__\:::\    \    
   /:::/ |::|   |           /:::/    /                \:::\   \:::\    \      /::::\   \:::\    \   
  /:::/  |::|___|______    /:::/    /      _____    ___\:::\   \:::\    \    /::::::\   \:::\    \  
 /:::/   |::::::::\    \  /:::/____/      /\    \  /\   \:::\   \:::\    \  /:::/\:::\   \:::\    \ 
/:::/    |:::::::::\____\|:::|    /      /::\____\/::\   \:::\   \:::\____\/:::/__\:::\   \:::\____\
\::/    / ~~~~~/:::/    /|:::|____\     /:::/    /\:::\   \:::\   \::/    /\:::\   \:::\   \::/    /
 \/____/      /:::/    /  \:::\    \   /:::/    /  \:::\   \:::\   \/____/  \:::\   \:::\   \/____/ 
             /:::/    /    \:::\    \ /:::/    /    \:::\   \:::\    \       \:::\   \:::\    \     
            /:::/    /      \:::\    /:::/    /      \:::\   \:::\____\       \:::\   \:::\____\    
           /:::/    /        \:::\__/:::/    /        \:::\  /:::/    /        \:::\   \::/    /    
          /:::/    /          \::::::::/    /          \:::\/:::/    /          \:::\   \/____/     
         /:::/    /            \::::::/    /            \::::::/    /            \:::\    \         
        /:::/    /              \::::/    /              \::::/    /              \:::\____\        
        \::/    /                \::/____/                \::/    /                \::/    /        
         \/____/                  ~~                       \/____/                  \/____/                                                                                                        
    """
    print(banner)
    version = get_version()
    print(f"MUSE-BiliMagicMarket-Scanner v{version}")
    print("=" * 88)
    print()


class BilibiliMarketScanner:
    def __init__(self):
        self.base_url = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"
        self.headers = {
            'authority': 'mall.bilibili.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
            'content-type': 'application/json',
            'origin': 'https://mall.bilibili.com',
            'referer': 'https://mall.bilibili.com/neul-next/index.html?page=magic-market_index',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
        }
        self.matched_items = []

    def set_cookies(self, cookies: str):
        self.headers['cookie'] = cookies

    def scan_market(self, keywords: List[str]) -> List[Dict[str, Any]]:
            
        self.matched_items = []
        next_id = None
        page_count = 0
        
        print(f"开始扫描，关键词: {', '.join(keywords)}")
        
        while True:
            page_count += 1
            print(f"正在扫描第 {page_count} 页...")
            
            payload = json.dumps({
                "nextId": next_id
            })
            
            try:
                response = requests.post(self.base_url, headers=self.headers, data=payload)
                
                if response.status_code == 412:
                    print(f"遇到412状态码，暂停5分钟后继续... 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    time.sleep(300)
                    print("暂停结束，继续扫描...")
                    continue
                elif response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    break
                    
                response_data = response.json()
                
                if "data" not in response_data:
                    print("响应数据格式异常")
                    print(f"响应内容: {response.text}")
                    break
                    
                next_id = response_data["data"].get("nextId")
                
                if next_id is None:
                    print("已扫描完所有页面")
                    break
                    
                items = response_data["data"].get("data", [])
                
                for item in items:
                    item_name = item.get("c2cItemsName", "")
                    
                    for keyword in keywords:
                        if keyword.lower() in item_name.lower():
                            if item not in self.matched_items:
                                self.matched_items.append(item)
                                print(f"找到匹配商品: {item_name} - 价格: {item.get('showPrice', 'N/A')}")
                                self.save_results("市集扫描结果.json")
                            break
                            
            except requests.exceptions.RequestException as e:
                print(f"网络请求异常: {e}")
                print("等待3秒后重试...")
                time.sleep(3)
                continue
            except json.JSONDecodeError as e:
                print(f"JSON解析异常: {e}")
                print("等待3秒后重试...")
                time.sleep(3)
                continue
            except Exception as e:
                print(f"未知异常: {e}")
                print("等待3秒后重试...")
                time.sleep(3)
                continue
                
            time.sleep(5)
            
        return self.matched_items

    def save_results(self, filename: str = "scan_results.json"):
        if not self.matched_items:
            print("没有找到匹配的商品")
            return
            
        try:
            simplified_items = []
            for item in self.matched_items:
                simplified_item = {
                    'c2cItemsName': item.get('c2cItemsName'),
                    'showPrice': item.get('showPrice'),
                    'c2cItemsId': item.get('c2cItemsId'),
                    'url': f"https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&itemsId={item.get('c2cItemsId')}"
                }
                simplified_items.append(simplified_item)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(simplified_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败: {e}")

    def print_summary(self):
        if not self.matched_items:
            print("没有找到匹配的商品")
            return
            
        print(f"\n=== 扫描结果摘要 ===")
        print(f"共找到 {len(self.matched_items)} 件匹配商品")
        
        sorted_items = sorted(self.matched_items, key=lambda x: x.get('price', float('inf')))
        
        print("\n商品列表:")
        for item in sorted_items:
            name = item.get('c2cItemsName', 'N/A')
            item_id = item.get('c2cItemsId', 'N/A')
            price = item.get('price', 'N/A')
            print(f"- {name} (ID: {item_id}) - 价格: {price}")
            
        if sorted_items:
            min_price_item = sorted_items[0]
            print(f"\n最低价商品: {min_price_item.get('c2cItemsName', 'N/A')} - 价格: {min_price_item.get('price', 'N/A')}")


def main():
    while True:
        try:
            show_muse_banner()
            print("本程序将扫描所有B站魔力赏市集商品，找出符合关键词的商品")
            print("扫描结果将保存到: 市集扫描结果.json")
            print("")
            cookies = input("请输入您的cookies: ").strip()
            if not cookies:
                print("错误: cookies不能为空")
                continue
            
            keywords_input = input("请输入搜索关键词(多个关键词用逗号分隔): ").strip()
            if not keywords_input:
                print("错误: 关键词不能为空")
                continue
            
            keywords = [kw.strip() for kw in re.split('[,，]', keywords_input) if kw.strip()]
            
            scanner = BilibiliMarketScanner()
            scanner.set_cookies(cookies)
            
            print(f"\n准备扫描，关键词: {', '.join(keywords)}")
            print("按 Ctrl+C 可以随时停止扫描\n")
            
            results = scanner.scan_market(keywords)
            
            scanner.print_summary()
            
        except KeyboardInterrupt:
              print("\n程序已被用户中断")
              
              if 'scanner' in locals() and hasattr(scanner, 'matched_items'):
                  scanner.print_summary()
                  print("已保存的结果仍在 '市集扫描结果.json' 中")
                  
                  while True:
                      choice = input("\n继续扫描(C)/退出(T)/重新开始(S): ").strip().upper()
                      if choice == 'C':
                          print("\n继续扫描...\n")
                          try:
                              results = scanner.scan_market(keywords)
                              scanner.print_summary()
                              break
                          except KeyboardInterrupt:
                              continue
                      elif choice == 'T':
                          print("程序已退出")
                          return
                      elif choice == 'S':
                          print("\n重新开始程序...\n")
                          break
                      else:
                          print("请输入 C、T 或 S")
                  
                  if choice == 'C' or choice == 'S':
                      continue
              else:
                  while True:
                      choice = input("\n退出(T)/重新开始(S): ").strip().upper()
                      if choice == 'T':
                          print("程序已退出")
                          return
                      elif choice == 'S':
                          print("\n重新开始程序...\n")
                          break
                      else:
                          print("请输入 T 或 S")
        except Exception as e:
            import traceback
            print(f"程序运行出错: {e}")
            print("\n完整错误详情:")
            print(traceback.format_exc())
        
        while True:
            choice = input("\n退出(T)/重新开始(S): ").strip().upper()
            if choice == 'T':
                print("程序已退出")
                return
            elif choice == 'S':
                print("\n重新开始程序...\n")
                break
            else:
                print("请输入 T 或 S")


if __name__ == "__main__":
    main()