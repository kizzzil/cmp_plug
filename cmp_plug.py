import os
import sys
import urllib.request
import zipfile
import time
import shutil
import configparser
from progress.bar import ChargingBar, FillingCirclesBar, Bar
import argparse

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
        format_str = dirname[len(client_plug_path):]
        if "/" not in format_str:
            plugins.append(format_str)
    return plugins

def specify_wp_core_version(clientDir):
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

def download_wp_core(wp_core_version):
    base_path = os.path.dirname(__file__) + "/"
    os.chdir(base_path)
    wp_download_url = f'https://ru.wordpress.org/wordpress-{wp_core_version}-ru_RU.zip'
    wp_core_zip_path = f"./wordpresses/wordpress-{wp_core_version}-ru_RU.zip"
    if not os.path.exists(f'./wordpresses/wordpress-{wp_core_version}-ru_RU'):
        urllib.request.urlretrieve(wp_download_url, wp_core_zip_path)
        wp_core_zip = zipfile.ZipFile(wp_core_zip_path, 'r')
        wp_core_zip.extractall('./wordpresses/')
        os.rename('./wordpresses/wordpress', f'./wordpresses/wordpress-{wp_core_version}-ru_RU')
        os.remove(wp_core_zip_path)

def cp_wp_core(cmp_client_dir, wp_core_version):
        base_path = os.path.dirname(__file__) + "/"
        os.chdir(base_path)
        src = f'./wordpresses/wordpress-{wp_core_version}-ru_RU'
        shutil.copytree(src, cmp_client_dir)

def download_plugins(cmp_client_dir, pluginsWithVersions):
    # по плагину и версии можем на сайте WP скачать необходимый плагин
    downloadedPlugins = []
    if not os.path.exists(f'{cmp_client_dir}/wp-content/plugins/'):
        os.mkdir(f'{cmp_client_dir}/wp-content/plugins/')
    bar = Bar('downloading plugins', max = len(pluginsWithVersions))
    for plugin, version in pluginsWithVersions:
        url = f"https://downloads.wordpress.org/plugin/{plugin}.{version}.zip"
        try:
            bar.next()
            urllib.request.urlretrieve(url, f"{cmp_client_dir}/wp-content/plugins/{plugin}.zip")
            downloadedPlugins.append(plugin)
        except: urllib.request.HTTPDefaultErrorHandler
    bar.finish()
    
    return downloadedPlugins

def download_themes(cmp_client_dir, themesWithVersions):
    downloadedThemes = []
    if not os.path.exists(f'{cmp_client_dir}/wp-content/themes/'):
        os.mkdir(f'{cmp_client_dir}/wp-content/themes/')
    bar = Bar('downloading themes', max = len(themesWithVersions))
    for theme, version in themesWithVersions:
        url = f"https://downloads.wordpress.org/theme/{theme}.{version}.zip"
        try:
            bar.next()
            urllib.request.urlretrieve(url, f"{cmp_client_dir}/wp-content/themes/{theme}.zip")
            downloadedThemes.append(theme)
        except: urllib.request.HTTPDefaultErrorHandler
    bar.finish()
    return  downloadedThemes


def unzip_plugins(cmp_client_dir, downloadedPlugins):       
    ## распаковать только загруженные
    bar = Bar('unpacking arhives', max = len(downloadedPlugins))
    for plugin in downloadedPlugins:
        bar.next()
        archive = zipfile.ZipFile(f"{cmp_client_dir}/wp-content/plugins/{plugin}.zip", 'r')
        for file in archive.namelist():
            if file.startswith(f'{plugin}/'):
                archive.extract(file, f"{cmp_client_dir}/wp-content/plugins")
    bar.finish()

def unzip_themes(cmp_client_dir, downloadedThemes):      
    ## распаковать только загруженные
    bar = Bar('unpacking arhives', max = len(downloadedThemes))
    for theme in downloadedThemes:
        bar.next()
        archive = zipfile.ZipFile(f"{cmp_client_dir}/wp-content/themes/{theme}.zip", 'r')
        for file in archive.namelist():
            if file.startswith(f'{theme}/'):
                archive.extract(file, f"{cmp_client_dir}/wp-content/themes")
    bar.finish()


def delete_zip_plugins(downloaded_plugins_list, cmp_client_dir):
    for plugin in downloaded_plugins_list:                      
        os.remove(f"{cmp_client_dir}/wp-content/plugins/{plugin}.zip")

def delete_zip_themes(downloaded_themes_list, cmp_client_dir):
    for theme in downloaded_themes_list:                      
        os.remove(f"{cmp_client_dir}/wp-content/themes/{theme}.zip")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="help??")  
    parser.add_argument('-p', '--plugins', action='store_true')
    parser.add_argument('-t', '--themes', action='store_true')
    parser.add_argument('-с', '--core', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')

    args = parser.parse_args() 
    print(args)

    config = configparser.ConfigParser()
    config.read('config.txt')
    clientDir = config.get('Section', 'ClientDir')
    cmp_client_dir = clientDir + "_cmp"


    if args.core or args.all:
        if not os.path.exists("./wordpresses"):
            os.mkdir( "./wordpresses")
        print("Поиск версии ядра wordpress")
        wp_core_version = specify_wp_core_version(clientDir)
        # Загрузка ядра wp соответсвующей версии, берется из кэша если есть. 
        print(f"Загрузка ядра wordpress версии {wp_core_version}")
        download_wp_core(wp_core_version)
        print('Копирование ядра Wordpress')
        if not os.path.exists(f'{cmp_client_dir}/index.php'):
            cp_wp_core(cmp_client_dir, wp_core_version)

    if args.plugins or args.all:
        print("Создание списка плагинов")
        plugins = get_plugins_list(clientDir)
        print("Поиск версий плагинов")
        pluginsWithVersions = specify_plugins_version(plugins, clientDir)
        downloaded_plugins_list = download_plugins(cmp_client_dir, pluginsWithVersions)
        unzip_plugins(cmp_client_dir, downloaded_plugins_list)
        print("Удаление zip файлов плагинов")
        delete_zip_plugins(downloaded_plugins_list, cmp_client_dir)
    
    if args.themes or args.all:
        print("Создание списка тем")
        themes = get_themes_list(clientDir)
        print("Поиск версий тем")
        themesWithVersions = specify_themes_version(themes, clientDir)
        downloaded_themes_list = download_themes(cmp_client_dir, themesWithVersions)
        unzip_themes(cmp_client_dir, downloaded_themes_list)
        delete_zip_themes(downloaded_themes_list, cmp_client_dir)




 




    


    # ### OUTPUT RESULT ###

    # print(f"всего плагинов : {len(plugins) - 1}")
    # print(f"загружено : {len(downloadedPlugins)}") 
    # print(f"незагруженные плагины: {len(plugins) - 1 - len(downloadedPlugins)}")
    # for plugin in plugins[1:]:
    #     if plugin not in downloadedPlugins:
    #         print(plugin)
