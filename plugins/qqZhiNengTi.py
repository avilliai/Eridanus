import asyncio
import httpx

prompt=[{"role": "user", "content": "谁赢得了2020年的世界职业棒球大赛?"},
                  {"role": "assistant", "content": "洛杉矶道奇队在2020年赢得了世界职业棒球大赛冠军."},
                  {"role": "user", "content": "它在哪里举办的?"}]
r=asyncio.run(main(prompt,"dhZQEEdWXFYp","ZULqrpGmEhNYNlL2fDHWGcQPcI87hfmZ"))
print(r)