

import os
import time

import traceback
from PIL import Image
import random
import re

from framework_common.utils.install_and_import import install_and_import


# 初始化 Selenium
def init_driver():
    selenium = install_and_import("selenium")
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    chromedriver_path = "E:\chromedriver\chromedriver.exe"  # 替换为你的 chromedriver 路径
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式（隐藏浏览器窗口），如果需要可注释掉
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def text_handle(content,img_list):
    context_output=''
    context_chara=[]
    context_chara_check = ''
    content = content.split("\n")
    main_flag=0
    staff_flag=0
    topic_flag=0
    chara_flag=0
    update_flag=0
    cv_flag=0
    img_chara_count = 0
    for i in img_list:
        if i.startswith('chara'):
            break
        img_chara_count +=1

    game_id=None
    game_name='封面'
    for context_check in content:
        match = re.search(r"游戏ID:\s*(\d+)", context_check)
        if match:
            game_id = match.group(1)
    print(f'\n\ngame_id:{game_id}\n\n')
    if game_id is None:
        game_id=random.randint(0,len(content)-1)

    for context_check in content:
        #print(context_check)
        if '【PC' in context_check and topic_flag == 0:
            context_output+='#'+context_check+'\n\n'

            for i in img_list:
                if 'PC' in i:
                    game_name=i
                    context_output += 'url:'+"https://gal.manshuo.ink/usr/uploads/galgame/"+game_id+"/"+ game_name + '\n\n'
                    break

            topic_flag=1
        elif '更多信息' in context_check:
            main_flag = 0
        elif '游戏介绍' in context_check:
            context_output += '#' + '故事介绍' + '\n\n'
            main_flag=1
        elif main_flag==1:
            context_output += context_check + '\n'
        elif '发行日期' in context_check:
            context_output = '> ' + context_check + '\n\n' + context_output
        elif 'Staff' in context_check:
            context_output += '\n##' + context_check + '\n'
            staff_flag=1
        elif staff_flag==1:
            if '原画' in context_check:
                context_output += '\n- ' + context_check + ': '
            elif '脚本' in context_check:
                context_output += '\n- ' + context_check + ': '
            elif '歌曲' in context_check:
                context_output += '\n- ' + context_check + ': '
            elif '音乐' in context_check:
                context_output += '\n- ' + context_check + ': '
            elif '角色' in context_check:
                context_output += '\n\n\n##' + context_check + '\n'
                staff_flag=0
                chara_flag=1
            else:
                context_output += context_check + ' | '
        elif chara_flag==1:
            if '由 月幕OpenAPI & HikarinagiAPI 驱动' in context_check:
                context_output_middle = '> ' + context_check + '\n'
            elif '数据来源：月幕Galgame - 美少女游戏档案 | 反馈错误(反馈时请附带游戏ID)' in context_check:
                chara_flag=2
                context_output += '\n\n' + context_output_middle + context_check + '\n\n'

            if context_chara_check != '':
                if 'CV' in context_check:

                    try:

                        img_chara="!["+img_list[img_chara_count]+"](https://gal.manshuo.ink/usr/uploads/galgame/"+game_id+"/"+img_list[img_chara_count]+")"
                    except:
                        img_chara=''
                    context_chara.append([context_chara_check, context_check,img_chara])
                    #context_chara +=f'{context_chara_check}\n{context_check}\n\n'
                    img_chara_count += 1
            context_chara_check = context_check

        elif chara_flag == 2:
            #print(context_chara)
            context_chara_output = ''
            if context_chara != []:
                count=len(context_chara)
                y=len(context_chara)//3
                x=len(context_chara)%3
                print(f'x:{x},y:{y},count:{count}')
                if x != 0: y+=1
                for y1 in range(y):
                    if int(y1) == int(y-1) :
                        for x1 in range(3):
                            context_chara.append([' ', ' ', ' '])
                    if int(y1) != int(y):
                        context_chara_output += (f"\n{context_chara[y1*3][0]}|{context_chara[y1*3+1][0]}|{context_chara[y1*3+2][0]}\n"
                                            f":---:|:--:|:---:\n"
                                            f"{context_chara[y1*3][2]}{context_chara[y1*3][1]}|"
                                            f"{context_chara[y1*3+1][2]}{context_chara[y1*3+1][1]}|"
                                            f"{context_chara[y1*3+2][2]}{context_chara[y1*3+2][1]}\n")

            context_output += '\n\n'+context_chara_output
            if update_flag ==0:
                context_output += '\n\n' + '----------' + '\n\n'+'\n\n#游戏截图\n\n'
                img_screen_list=[]
                img_chara_screen_game=''
                for i in img_list:
                    if i.startswith('图片'):
                        img_screen_list.append(i)
                for i in img_screen_list:
                    img_chara_screen_game += "\n\n![" + i + "](https://gal.manshuo.ink/usr/uploads/galgame/" + game_id + "/" + i + ")\n\n"
                context_output+=img_chara_screen_game
            if '更新' in context_check:
                context_output += '\n\n> ' + context_check + '\n\n'
                update_flag=1
            else:
                update_flag = 2
                chara_flag=0
        elif update_flag==2:
            context_output += '\n\n'+'----------' + '\n\n' + '#游戏资源' + '\n\n'
            context_output +=(f"封面|链接\n:---:|:---:\n![{game_name}](https://gal.manshuo.ink/usr/uploads/galgame/{game_id}/{game_name})|"
                              f"![世伊Gal资源站](https://gal.manshuo.ink/usr/uploads/galgame/title_page.png)[hide][世伊Gal资源站:{game_name}](https://alist.gcbe.eu.org:10400)[/hide]")
            break

    return context_output



# 保存图片截图到本地
def save_image_screenshot(element, index, output_dir=None,img_url=None,img_name=None):
    selenium = install_and_import("selenium")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    if output_dir is None:
        output_dir='screenshots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if '.gif' in img_url:
        return False
    try:

        img_path = os.path.join(output_dir, f"{img_name}.png")  # 使用索引命名文件
        driver = init_driver()
        driver.get(img_url)  # 在新窗口加载图片 URL
        time.sleep(2)  # 等待图片加载

        image_element = driver.find_element(By.TAG_NAME, "img")  # 假设图片是 <img> 标签

        # 获取图片的位置信息和尺寸 (图片左上角的坐标及宽高)
        location = image_element.location  # 图片左上角的坐标（x, y）
        size = image_element.size  # 图片的大小（宽度和高度）

        # 保存整个页面的截图
        screenshot_path = os.path.join(output_dir, f"image_{index}_fullscreen.png")
        driver.save_screenshot(screenshot_path)

        # 用 Pillow 打开截图
        img = Image.open(screenshot_path)

        # 计算裁剪区域
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        #print(f"left:{left}, top:{top}, right:{right}, bottom:{bottom}")
        cropped_image = img.crop((left+1, top+1, right, bottom))  # 裁剪图片

        cropped_image.save(img_path)
        os.remove(screenshot_path)
        print(f"图片已保存: {img_path}")
        return True
    except Exception as e:
        print(f"图片截图失败, 错误: {e}")
        traceback.print_exc()
        return False

# 滚动页面加载图片
def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 滚动到底部
    time.sleep(2)  # 等待加载
    driver.execute_script("window.scrollTo(0, 0);")  # 回到顶部
    time.sleep(2)  # 再次等待

# 等待图片加载完成
def wait_for_image_to_load(driver, image,times=None,img_name=None):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", image)  # 滚动到图片位置
        time.sleep(1)  # 等待图片加载
        if times is not None or '图片' in img_name:
            print('已延长等待时间')
            time.sleep(5)

        # 检查图片的 naturalWidth 是否大于 0，表示图片已经加载
        is_loaded = driver.execute_script(
            "return arguments[0].complete && arguments[0].naturalWidth > 0;", image
        )
        return is_loaded
    except Exception as e:
        print('图片加载出错！！！！')
        if times is None:times = 1
        if times <=2:
            print(f"检查图片加载失败，重试次数：{times}")
            times += 1
            return wait_for_image_to_load(driver, image,times=times)
        return False



# 提取图片截图和文本
def scrape_images_and_text_with_screenshots(url):
    selenium = install_and_import("selenium")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    images_check = []
    time_wait = 30
    print(f'正在等待网页打开，请等待至少 {time_wait+10}s ...')
    driver = init_driver()
    driver.get(url)  # 加载网页
    for time_count in range(time_wait+1):
        time.sleep(1)
        if time_count%10 == 0 :
            #if time_count==0:continue
            print(f'您已经等待{time_count+10}s ...')

    scroll_page(driver)  # 滚动页面以加载所有资源

    # 提取文本
    text = driver.find_element(By.TAG_NAME, "body").text  # 获取页面正文
    content = text.split("\n")
    game_id = None
    for context_check in content:
        match = re.search(r"游戏ID:\s*(\d+)", context_check)
        if match:
            game_id = match.group(1)
    # 提取所有图片元素并截图
    images = driver.find_elements(By.TAG_NAME, "img")  # 找到所有 <img> 标签
    for index, img in enumerate(images):
        try:
            flag = 0
            if img.is_displayed():  # 检查图片是否可见
                img_url = img.get_attribute("src")  # 获取图片的 src 属性（URL）
                img_name = img.get_attribute("alt")
                for name_check in {'等级','头像','徽章','光之友','表情','Hikarinagi - 一个ACGN文化社区','DL','steam'}:
                    if f'{name_check}' in img_name :flag=1
                img_name = img_name.replace("/", "-").replace(" ", "").replace("【", "").replace("】", "").replace("[", "").replace("]", "").replace("～", "").replace("-", "_")
                if img_name == '':
                    flag=2
                    img_name=f'chara_{index}'
                if flag==1:continue
                print(f"图片 URL: {img_url}\n 图片名称: {img_name}")
                is_loaded = wait_for_image_to_load(driver, img,img_name=img_name)  # 确保图片加载完成
                if is_loaded:
                    check=save_image_screenshot(img, index,img_url=img_url,img_name=img_name,output_dir=game_id)  # 保存图片截图
                    if check:
                        images_check.append(f"{img_name}.png")
                else:
                    print(f"图片未完全加载，跳过: {img.get_attribute('src')}")
        except Exception as e:
            print(f"处理图片元素失败，错误: {e}")
            traceback.print_exc()
    driver.quit()
    output_context = text_handle(text, images_check)
    # 保存文本到文件
    if game_id is None:
        filename='sreenshot'
    else:
        filename=game_id
    with open(f"{filename}.txt", "w", encoding="utf-8") as text_file:
        text_file.write(output_context)
    print(f"文本内容已保存到 {filename}.txt 文件中！")
    #print(f'\n\n{output_context}')
    return images_check


# 提取图片截图和文本
def scrape_images_get_url(url):
    selenium = install_and_import("selenium")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    images_check = []
    driver = init_driver()
    driver.get(url)  # 加载网页
    # 提取所有图片元素并截图
    images = driver.find_elements(By.TAG_NAME, "img")  # 找到所有 <img> 标签
    for index, img in enumerate(images):
        try:
            flag = 0
            if img.is_displayed():  # 检查图片是否可见
                img_url = img.get_attribute("src")  # 获取图片的 src 属性（URL）
                img_name = img.get_attribute("alt")
                for name_check in {'等级','头像','徽章','光之友','表情','avatar','有希日记','steam','boxmoe_header_banner_img'}:
                    if f'{name_check}' in img_name :
                        flag=1
                is_loaded = wait_for_image_to_load(driver, img,img_name=img_name)  # 确保图片加载完成
                if is_loaded:
                    if flag==0:
                        images_check.append(img_url)
        except Exception as e:
            #print(f"处理图片元素失败，错误: {e}")
            traceback.print_exc()

    driver.quit()
    return images_check

# 主函数
def main():
    url = input("请输入要爬取的网页 URL: ").strip()
    images_url=scrape_images_get_url(url)
    print(f'images_url:{images_url}')
if __name__ == "__main__":
    main()