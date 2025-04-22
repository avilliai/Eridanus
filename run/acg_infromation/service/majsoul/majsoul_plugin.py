import asyncio

from run.acg_infromation.service.majsoul.majsoul_info.init import majsoulInfo, TrimajsoulInfo, RecordInfo, TriRecordInfo
from run.group_fun.service.wife_you_want import manage_group_status
import copy

json_init={'status':False,'content':{},'text':'初始化','pic_path':{},'type_soft':'雀魂牌谱屋','uesr_name':'初始化'}

async def check_for_majsoul_personal_info(context,type=0,target_id=None,target_name=None,room_set=None):
    # type 0:默认用户雀魂信息查询
    # type 1:雀魂四麻查询
    # type 2:雀魂四麻牌局查询
    # type 3:雀魂三麻查询
    # type 4:雀魂三麻牌局查询
    # type 5:雀魂牌局查询
    #目标数据库：majsoul
    json_majsoul = copy.deepcopy(json_init)
    if target_id is not None:
        target_name_search = await manage_group_status(target_id,'user_info_colloction','majsoul')
        if target_name_search == 0 and target_name is None:
            json_majsoul['text'] = "您还未‘雀魂注册’哦～"
            return json_majsoul
        elif target_name_search == 0 and target_name is not None:
            await manage_group_status(target_id, 'user_info_colloction', 'majsoul',target_name)
        else:
            target_name=f'{target_name_search}'
        json_majsoul['uesr_name'] = target_name
    context_check=context.replace(' ','')
    if context_check == "金场" or context_check == "金" or context_check == "金之间":
        room_set = "金"
    elif context_check == "玉场" or context_check == "玉" or context_check == "玉之间":
        room_set = "玉"
    elif context_check == "王座" or context_check == "王座之间":
        room_set = "王座"
    if room_set is not None:
        target_name=f'{room_set} {target_name}'
    type=int(type)
    if type == 0:
        status,context_text = await majsoulInfo(target_name)
        json_majsoul['type'] = '雀魂四麻查询'
        if status is False:
            status, context_text = await TrimajsoulInfo(target_name)
            json_majsoul['type'] = '雀魂三麻查询'
            if status is False:
                json_majsoul['text'] = context_text
                json_majsoul['status'] = False
                return json_majsoul
        if status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul
    elif type == 1:
        status, context_text = await majsoulInfo(target_name)
        json_majsoul['type'] = '雀魂四麻查询'
        if status is False:
            json_majsoul['text'] = context_text
            json_majsoul['status'] = False
            return json_majsoul
        elif status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul
    elif type == 2:
        status, context_text = await RecordInfo(target_name)
        json_majsoul['type'] = '雀魂四麻牌局查询'
        if status is False:
            json_majsoul['text'] = context_text
            json_majsoul['status'] = False
            return json_majsoul
        elif status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul
    elif type == 3:
        status, context_text = await TrimajsoulInfo(target_name)
        json_majsoul['type'] = '雀魂三麻查询'
        if status is False:
            json_majsoul['text'] = context_text
            json_majsoul['status'] = False
            return json_majsoul
        elif status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul
    elif type == 4:
        status, context_text = await TriRecordInfo(target_name)
        json_majsoul['type'] = '雀魂三麻牌局查询'
        if status is False:
            json_majsoul['text'] = context_text
            json_majsoul['status'] = False
            return json_majsoul
        elif status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul
    elif type == 5:
        status, context_text = await RecordInfo(target_name)
        json_majsoul['type'] = '雀魂四麻牌局查询'
        if status is False:
            status, context_text = await TriRecordInfo(target_name)
            json_majsoul['type'] = '雀魂三麻牌局查询'
            if status is False:
                json_majsoul['text'] = context_text
                json_majsoul['status'] = False
                return json_majsoul
        if status is True:
            json_majsoul['status'] = True
            json_majsoul['text'] = context_text
            return json_majsoul



if __name__ == '__main__':
    pass
    asyncio.run(TriRecordInfo("CGhitomi"))