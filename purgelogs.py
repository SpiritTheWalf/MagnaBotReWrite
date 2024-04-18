import os


def delete_log_files():
    current_directory = os.getcwd()
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.log'):
            file_path = os.path.join(current_directory, file_name)
            os.remove(file_path)
            print(f"Deleted: {file_path}")


if __name__ == "__main__":
    delete_log_files()
