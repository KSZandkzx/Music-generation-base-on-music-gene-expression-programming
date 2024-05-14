import os

def delete_files_with_extension(folder_path, extension):
    # 获取文件夹中的所有文件
    file_list = os.listdir(folder_path)

    # 删除指定后缀的文件
    for file_name in file_list:
        if file_name.endswith(extension):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
            print(f'Deleted: {file_path}')

# 调用函数删除指定类型的文件
folder_path = './othermethod/5'  # 文件夹路径
for extension in ['.mid','.txt','.wav','.mp3']:
    delete_files_with_extension(folder_path, extension)