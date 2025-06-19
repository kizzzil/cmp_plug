import os
import sys
import urllib.request
import zipfile
import time
import configparser
from progress.bar import ChargingBar, FillingCirclesBar, Bar


if __name__ == '__main__':
    # DISCRIPTION
    # Cкрипт для автоматического определения версий плагинов клиента  
    # и автоматической загрузки и распоковки оригинальных плагинов 
    # соответствующих версий с сайта wordpress.org 

    # Для начала необходимо скачать архив плагинов с сайта клиента, 
    # распокавать его и сюда вставить путь к этой папке 

    ## эти переменные заменить на свои по такому же принципу
    config = configparser.ConfigParser()
    config.read('config.txt')
    clientDir = config.get('Section', 'ClientDir')
    client_plug_path = f'{clientDir}/wp-content/plugins/'
    # original_plug_path = "/home/kizzzil/Work/plugins/"

    # client_plug_path = "/home/kizzzil/Work/Client/wp-content/plugins"
    # original_plug_path = "/home/kizzzil/Work/plugins/"

    ## поиск всех плагинов (считаются просто названия директорий)
    os.chdir(client_plug_path)
    dirlist = os.walk(client_plug_path)
    plugins = []
    for dirname, _, _ in dirlist:
        format_str = dirname[len(client_plug_path) + 1:]
        if "/" not in format_str:
            plugins.append(format_str)

    ## по найденным плагинам находятся версии
    pluginsWithVersions = []
    bar = Bar('Search versions', max = len(plugins) - 1)
    for plugin in plugins[1:]:
        bar.next()
        newPath = client_plug_path + "/" + plugin
        os.chdir(newPath)
        try:
            f = open("readme.txt", "r", encoding="UTF8")
            number_str = 0
            while number_str < 100:
                line = f.readline()
                if "Stable tag: " in line:
                    slashInd = line.find("\n")
                    version = line[12:slashInd]
                    pluginsWithVersions.append([plugin, version])
                    break
                number_str += 1
            f.close()
        except: IOError
    bar.finish()

    ## по плагину и версии можем на сайте WP скачать необходимый плагин
    downloadedPlugins = []
    bar = Bar('downloading plugins', max = len(pluginsWithVersions))
    for plugin, version in pluginsWithVersions:
        url = f"https://downloads.wordpress.org/plugin/{plugin}.{version}.zip"
        try:
            bar.next()
            urllib.request.urlretrieve(url, f"{original_plug_path}/{plugin}.zip")
            downloadedPlugins.append(plugin)
        except: urllib.request.HTTPDefaultErrorHandler
    bar.finish()
        
    ## распаковать только загруженные
    bar = Bar('unpacking arhives', max = len(downloadedPlugins))
    for plugin in downloadedPlugins:
        bar.next()
        archive = zipfile.ZipFile(f"{original_plug_path}/{plugin}.zip", 'r')
        for file in archive.namelist():
            if file.startswith(f'{plugin}/'):
                archive.extract(file, f"{original_plug_path}")
    bar.finish()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # for plugin in downloadedPlugins:                      #
    #     os.remove(f"{original_plug_path}\\{plugin}.zip")  #
    #                                                       #
    #    У МЕНЯ НЕ ВСЕГДА РАБОТАЕТ, ПИШЕТ ЧТО УЖЕ ЗАНЯТО    #
    #    КАКИМ-ТО ПРОЦЕССОМ. ПОКА НЕ ХОЧУ РАЗБИРАТЬСЯ       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    ### OUTPUT RESULT ###

    print(f"всего плагинов : {len(plugins) - 1}")
    print(f"загружено : {len(downloadedPlugins)}") 
    print(f"незагруженные плагины: {len(plugins) - 1 - len(downloadedPlugins)}")
    for plugin in plugins[1:]:
        if plugin not in downloadedPlugins:
            print(plugin)
