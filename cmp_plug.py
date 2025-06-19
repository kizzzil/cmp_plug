import os
import sys
import urllib.request
import zipfile
import time
import shutil
import configparser
from progress.bar import ChargingBar, FillingCirclesBar, Bar

def get_themes_list(clientDir):
    client_themes_dir = f'{clientDir}/wp-content/themes/'
    os.chdir(client_themes_dir)
    dirlist = os.walk(client_themes_dir)
    themes = []
    for dirname, _, _ in dirlist:
        format_str = dirname[len(client_themes_dir):]
        if "/" not in format_str:
            themes.append(format_str)
    return themes

def get_plugins_list(clientDir):
    # поиск всех плагинов (считаются просто названия директорий)
    client_plug_path = f'{clientDir}/wp-content/plugins/'
    os.chdir(client_plug_path)
    dirlist = os.walk(client_plug_path)
    plugins = []
    for dirname, _, _ in dirlist:
        format_str = dirname[len(client_plug_path) + 1:]
        if "/" not in format_str:
            plugins.append(format_str)
    return plugins

def get_wp_core_version(clientDir):
    with open(f'{clientDir}/wp-includes/version.php') as f:
        # $wp_version = '6.8.1';
        lines = f.readlines()
        for line in lines:
            if "wp_version " in line:
                version = line[len("$wp_verison = ")+1:-3]
                break
    return version

def specify_plugins_version(plugins, clientDir):
    ## по найденным плагинам находятся версии
    client_plug_path = f'{clientDir}/wp-content/plugins/'
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

    return pluginsWithVersions

def specify_themes_version(themes, clientDir):
    client_themes_dir = f'{clientDir}/wp-content/themes/'
    ## по найденным плагинам находятся версии
    themesWithVersions = []
    bar = Bar('Search versions', max = len(themes) - 1)
    for theme in themes[1:]:
        bar.next()
        newPath = client_themes_dir + theme
        os.chdir(newPath)
        try:
            with open("style.css", "r", encoding="UTF8") as f:
                lines = f.readlines()
                for line in lines:
                    if "Version: " in line:
                        version = line[9:-1]
                        print(version)
                        themesWithVersions.append([theme, version])
                        break
        except: IOError
    bar.finish()
    return themesWithVersions

# def download_themes():

# def download_plugins():

# def download_wp_core():

# def unpack_themes():

# def unpack_plugins():

# def unpack_wp_core():

# def del_zip_themes():

# def del_zip_plugins():

# def del_zip_wp_core():

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
    if not os.path.exists(clientDir + "_cmp"):
        os.mkdir(clientDir + "_cmp")
    if not os.path.exists("./wordpresses"):
        os.mkdir( "./wordpresses")

    ## поиск всех плагинов (считаются просто названия директорий)
    # plugins = get_plugins_list(clientDir)
    # themes = get_themes_list(clientDir)

    # pluginsWithVersions = specify_plugins_version(plugins, clientDir)
    # themesWithVersions = specify_themes_version(themes, clientDir)

    # print(pluginsWithVersions)
    # print(themesWithVersions)

    wp_core_version = get_wp_core_version(clientDir)
    # print(wp_core_version)
    wp_download_url = f'https://ru.wordpress.org/wordpress-{wp_core_version}-ru_RU.zip'
    wp_core_zip_path = f"./wordpresses/wordpress-{wp_core_version}-ru_RU.zip"
    if not os.path.exists(f'./wordpresses/wordpress-{wp_core_version}-ru_RU'):
        urllib.request.urlretrieve(wp_download_url, wp_core_zip_path)
        wp_core_zip = zipfile.ZipFile(wp_core_zip_path, 'r')
        wp_core_zip.extractall('./wordpresses/')
        os.rename('./wordpresses/wordpress', f'./wordpresses/wordpress-{wp_core_version}-ru_RU')
    os.remove(wp_core_zip_path)
    # ## по плагину и версии можем на сайте WP скачать необходимый плагин
    # downloadedPlugins = []
    # bar = Bar('downloading plugins', max = len(pluginsWithVersions))
    # for plugin, version in pluginsWithVersions:
    #     url = f"https://downloads.wordpress.org/plugin/{plugin}.{version}.zip"
    #     try:
    #         bar.next()
    #         urllib.request.urlretrieve(url, f"{original_plug_path}/{plugin}.zip")
    #         downloadedPlugins.append(plugin)
    #     except: urllib.request.HTTPDefaultErrorHandler
    # bar.finish()
        
    # ## распаковать только загруженные
    # bar = Bar('unpacking arhives', max = len(downloadedPlugins))
    # for plugin in downloadedPlugins:
    #     bar.next()
    #     archive = zipfile.ZipFile(f"{original_plug_path}/{plugin}.zip", 'r')
    #     for file in archive.namelist():
    #         if file.startswith(f'{plugin}/'):
    #             archive.extract(file, f"{original_plug_path}")
    # bar.finish()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # for plugin in downloadedPlugins:                      #
    # #     os.remove(f"{original_plug_path}\\{plugin}.zip")  #
    # #                                                       #
    # #    У МЕНЯ НЕ ВСЕГДА РАБОТАЕТ, ПИШЕТ ЧТО УЖЕ ЗАНЯТО    #
    # #    КАКИМ-ТО ПРОЦЕССОМ. ПОКА НЕ ХОЧУ РАЗБИРАТЬСЯ       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # ### OUTPUT RESULT ###

    # print(f"всего плагинов : {len(plugins) - 1}")
    # print(f"загружено : {len(downloadedPlugins)}") 
    # print(f"незагруженные плагины: {len(plugins) - 1 - len(downloadedPlugins)}")
    # for plugin in plugins[1:]:
    #     if plugin not in downloadedPlugins:
    #         print(plugin)
