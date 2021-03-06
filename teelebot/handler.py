# -*- coding:utf-8 -*-
'''
@creation date: 2019-8-23
@last modify: 2020-6-27
'''
import configparser
import os
import sys

def config():
    __version__ = "1.8.6_dev"
    __author__ = "github:plutobell"

    config = {}

    if len(sys.argv) == 3 and sys.argv[1] in ("-c", "-C"):
        config_dir = os.path.abspath(sys.argv[2])
        #print(config_dir)
    elif len(sys.argv) == 1 or  len(sys.argv) == 2 and sys.argv[1] in ("check", "sdist", "bdist_wheel", "bdist_rpm"):
        if not os.path.exists(os.path.abspath(os.path.expanduser('~')) + "/.teelebot"):
            os.mkdir(os.path.abspath(os.path.expanduser('~')) + "/.teelebot")
        config_dir = os.path.abspath(os.path.expanduser('~')) + "/.teelebot/config.cfg"
        #config_dir = os.path.dirname(os.path.abspath(__file__)) + "/config.cfg"
        #print(config_dir)
    else:
        print("参数缺失或错误!")
        sys.exit(0)

    conf = configparser.ConfigParser()
    conf.read(config_dir)
    options = conf.options("config")

    default_args = ["key", "webhook", "debug", "root", "timeout"]
    for default_arg in default_args:
        if default_arg not in options:
            print("配置文件缺失必要的参数!")
            return False

    for option in options:
        config[str(option)] = conf.get("config", option)

    if any([ "version" in config.keys(), "author" in config.keys() ]):
        print("配置文件存在错误!")
        os._exit(0)

    if config["webhook"] == "True":
        webhook_args = ["cert_pub", "server_address", "server_port", "local_address" ,"local_port"]
        for w in webhook_args:
            if w not in config.keys():
                print("请检查配置文件中是否存在以下字段：\n" +\
                    "cert_pub server_address server_port local_address local_port")
                return False

    if "plugin_dir" in config.keys():
        plugin_dir = os.path.abspath(config["plugin_dir"]) + r'/'
    else:
        plugin_dir = os.path.dirname(os.path.abspath(__file__)) + "/plugins/"

    if not os.path.isdir(plugin_dir): #插件目录检测
        #os.makedirs(plugin_dir)
        os.mkdir(plugin_dir)
        with open(plugin_dir + "__init__.py", "w") as f:
            pass
    elif not os.path.exists(plugin_dir + "__init__.py"):
        with open(plugin_dir + "__init__.py", "w") as f:
            pass

    if "pool_size" in config.keys():
        if int(config["pool_size"]) < 1 or int(config["pool_size"]) > 100:
            print("线程池尺寸超出范围!(1-100)")
            return False
    else:
        config["pool_size"] = "40"

    if config["debug"] == "True":
        config["debug"] = True
    elif config["debug"] == "False":
        config["debug"] = False

    if config["webhook"] == "True":
        config["webhook"] = True
    elif config["webhook"] == "False":
        config["webhook"] = False

    config["author"] = __author__
    config["version"] = __version__
    config["plugin_dir"] = plugin_dir
    config["plugin_bridge"] = bridge(config["plugin_dir"])
    config["plugin_info"] = __plugin_info(config["plugin_bridge"].values(), config["plugin_dir"])

    #print(config)
    return config

def bridge(plugin_dir):
    plugin_bridge = {}
    plugin_list = []

    plugin_lis = os.listdir(plugin_dir)
    for plugi in plugin_lis:
        if os.path.isdir(plugin_dir + plugi) and plugi != "__pycache__":
            plugin_list.append(plugi)
    for plugin in plugin_list:
        with open(plugin_dir + plugin + r"/__init__.py", encoding="utf-8") as f:
            row_one = f.readline().strip()[1:]
            if row_one != "~~": #Hidden plugin
                plugin_bridge[row_one] = plugin

    #print(plugin_bridge)
    return plugin_bridge

def __plugin_info(plugin_list, plugin_dir):
    plugin_info = {}
    for plugin in plugin_list:
        mtime = os.stat(plugin_dir + plugin + "/" + plugin + ".py").st_mtime
        plugin_info[plugin] = mtime

    return plugin_info



