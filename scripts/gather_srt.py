import os
import shutil  # import the shutil module to use the file copying functions

from app.core import get_document_folder


def main():
    os.chdir(get_document_folder())
    root_folder = "./projects"  # change this to the root folder you want to scan
    output_folder = "./gathered"  # change this to the folder where you want to copy the SRT files
    os.makedirs(output_folder, exist_ok=True)

    srt_files = []  # create an empty list to store the SRT file paths

    # use os.walk to iterate through all the files and subdirectories in the root folder
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".srt"):  # check if the file extension is .srt
                srt_path = os.path.join(dirpath, filename)  # create the full path to the SRT file
                srt_files.append(srt_path)  # append the SRT file path to the list

    # copy the SRT files to the output folder
    for srt_file in srt_files:
        shutil.copy(srt_file, output_folder)

    print(f"Copied {len(srt_files)} SRT files to {output_folder}")


if __name__ == '__main__':
    main()
