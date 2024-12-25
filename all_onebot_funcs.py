from developTools.interface.sendMes import MailMan


def list_class_methods(cls):
    """
    动态列出类的所有方法及其注释。
    :param cls: 类对象
    :return: 方法名称及注释的字典
    """
    import inspect
    methods = {}
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        methods[name] = func.__doc__.strip() if func.__doc__ else "无描述"
    return methods


if __name__ == "__main__":
    from pprint import pprint
    pprint(list_class_methods(MailMan))
