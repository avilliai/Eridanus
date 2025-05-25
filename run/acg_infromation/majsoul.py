from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image
from run.acg_infromation.service.majsoul.majsoul_plugin import check_for_majsoul_personal_info
from run.group_fun.service.wife_you_want import manage_group_status
from run.streaming_media.service.Link_parsing.Link_parsing import majsoul_PILimg

def main(bot, config):
    logger=bot.logger

    @bot.on(GroupMessageEvent)
    async def majsoul_personal_info_regiter(event: GroupMessageEvent):
        context=event.pure_text
        user_id = str(event.sender.user_id)
        if context == '雀魂注册':
            await bot.send(event, "请发送您的雀魂用户名\n例如：雀魂注册 445")
            return
        if context.startswith("雀魂注册"):
            logger.info("雀魂个人信息注册ing")
            context = context.replace("雀魂注册", "").replace(" ", "")
            await manage_group_status(user_id, 'user_info_colloction', 'majsoul',str(context))
            majsoul_json=await check_for_majsoul_personal_info(context,type=0,target_name=context)
            message=False
            if majsoul_json["status"] is False:
                message = f"无法验证身份，信息可能无法获取"
            elif majsoul_json["status"] is True:
                message = f"身份已验证，欢迎使用雀魂查询功能"
            if message:
                await bot.send(event, f"您已成功绑定账号：{context}\n{message}")
        if context =="雀魂个人信息":
            logger.info("雀魂个人信息查询")
            majsoul_json=await check_for_majsoul_personal_info(context,type=0,target_id=user_id)
            message=False
            if majsoul_json["status"] is False:
                message = f"无法验证身份，信息可能无法获取"
            elif majsoul_json["status"] is True:
                message = f"身份已验证，欢迎使用雀魂查询功能"
            if message:
                await bot.send(event, f"您当前绑定的雀魂账号：{majsoul_json['uesr_name']}\n{message}")

    @bot.on(GroupMessageEvent)  # 个人雀魂信息查询
    async def check_for_majsoul_personal_info_run(event: GroupMessageEvent):
        context=event.pure_text
        user_id = str(event.sender.user_id)
        user_name = str(event.sender.nickname)
        if not context.startswith("雀魂"):
            return
        context = context.replace("雀魂", "")
        list_check_personal_info=['信息','查询','账号']
        four_majsoul_personal_info=['四麻查询','四麻信息']
        four_majsoul_personal_record=['四麻记录','四麻战绩','四麻历史记录','四麻历史']
        three_majsoul_personal_info = ['三麻查询', '三麻信息']
        three_majsoul_personal_record = ['三麻记录', '三麻战绩', '三麻历史记录', '三麻历史']
        list_record_personal_info=['战绩','记录','历史记录','历史']


        check_flag = False
        if check_flag is False:
            for check_personal_info in list_check_personal_info:
                if context.startswith(check_personal_info):
                    check_flag=0
                    break

        if check_flag is False:
            for check_personal_info in four_majsoul_personal_info:
                if context.startswith(check_personal_info):
                    check_flag=1
                    break

        if check_flag is False:
            for check_personal_info in four_majsoul_personal_record:
                if context.startswith(check_personal_info):
                    check_flag = 2
                    break

        if check_flag is False:
            for check_personal_info in three_majsoul_personal_info:
                if context.startswith(check_personal_info):
                    check_flag = 3
                    break

        if check_flag is False:
            for check_personal_info in three_majsoul_personal_record:
                if context.startswith(check_personal_info):
                    check_flag = 4
                    break

        if check_flag is False:
            for check_personal_info in list_record_personal_info:
                if context.startswith(check_personal_info):
                    check_flag = 5
                    break

        if check_flag is False:
            #await bot.send(event, "请正确输入雀魂查询命令")
            return

        context = context.replace(check_personal_info, "").replace(" ", "")
        majsoul_json = await check_for_majsoul_personal_info(context, type=check_flag, target_id=user_id)
        if majsoul_json["status"] is False:
            await bot.send(event, majsoul_json["text"])
            return
        if config.acg_infromation.config["绘图框架"]['majsoul_search'] is False:
            await bot.send(event, majsoul_json["text"])
            return

        if check_flag in [2,4,5]:canvas_width=1400
        else:canvas_width=1200
        majsoul_pil_context=f'{majsoul_json["text"]}\n#”雀魂查询“ 指令菜单：#\n雀魂信息、雀魂记录、雀魂注册\n雀魂四麻查询、雀魂三麻查询、雀魂四麻记录、雀魂三麻记录'
        majsoul_pil_json=await majsoul_PILimg(text=majsoul_pil_context,filepath='data/pictures/cache/',type_soft=majsoul_json["type"],canvas_width=canvas_width)
        if majsoul_pil_json['status']:
            bot.logger.info('雀魂图片制作成功，开始推送~~~')
            await bot.send(event, Image(file=majsoul_pil_json['pic_path']))