import os
import sys
import pytsk3
import pyewf
from .utils import WINDAUBE_DEFAULT_USERS, FS_TYPES


class EwfImgInfo(pytsk3.Img_Info):
    """An Img_Info implementation for handling EWF images."""
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super().__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()
    
class Filesystem:
    """A wrapper class for accessing the file system of an image."""
    def __init__(self, image_handle, offset):
        self._fs_handle = pytsk3.FS_Info(image_handle, offset=offset)
        self.system_users = []

    def open(self, filename):
        return self._fs_handle.open(filename)
    
    def listDirectory(self, path : str= "/"):
        directory = self._fs_handle.open_dir(path)
        return [file_handle.info.name.name for file_handle in directory]
    
    def getSystemUsers(self):
        actualUsers = self.listDirectory("Users")
        self.system_users = [u for u in actualUsers if u not in WINDAUBE_DEFAULT_USERS.values()]
        return self.system_users

    def close(self):
        pass


class EwfExtractor:
    """A class for extracting files from an EWF image."""
    def __init__(self, ewf_filename, output_dir, files_to_extract, log_file_name):
        self.ewf_filename = ewf_filename
        self.output_dir = output_dir
        self.files_to_extract = files_to_extract
        self.ewf_handle = None
        self.image_handle = None
        self.partition_table = None
        self.filesystems = []
        self.mft = None
        self.log_file_name = log_file_name

    def open(self):
        """Opens the EWF image and initializes the necessary handles."""
        self.ewf_handle = pyewf.handle()
        self.ewf_handle.open(pyewf.glob(self.ewf_filename))
        self.image_handle = EwfImgInfo(self.ewf_handle)
        self.partition_table = pytsk3.Volume_Info(self.image_handle)

    def getDataPartition(self):
        for partition in self.partition_table:
            for fs_type in FS_TYPES.values():
                if fs_type in partition.desc:
                    return partition

    def extract_file(self, filename, outfilename, log):
        try:
            fileobject = self.filesystems[-1].open(filename)
            if fileobject:
                with open(os.path.join(self.output_dir, outfilename), 'wb') as outfile:
                    filedata = fileobject.read_random(0, fileobject.info.meta.size)
                    outfile.write(filedata)
                print(f"Extracted {filename} to {outfilename}")
            else:
                error = f"Failed to extract {filename}: could not open file object"
                log.write(error + "\n")
        except Exception as e:
            error = f"Failed to extract {filename}: {e}"
            log.write(error + "\n")

    def create_directory_if_not_exists(self, path, log):
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
                log.write(f"Directory created at {path}\n")
        except Exception as e:
            log.write(f"Error creating directory at {path}: {e}\n")

    def extract_files(self):
        partition = self.getDataPartition()
        filesystem = Filesystem(self.image_handle, offset=(partition.start * 512))
        self.filesystems.append(filesystem)
        errors = []
        self.create_directory_if_not_exists(self.output_dir, self.log_file_name)
        with open(os.path.join(self.output_dir, self.log_file_name), "w") as log:
            for f in self.files_to_extract:
                outputDirectory = self.output_dir + os.path.basename(f)
                try:
                    self.extract_file(f, outputDirectory, log)
                except Exception as e:
                    errors.append((f, str(e)))
                    log.write(f"{f}: {e}\n")
            filesystem.close()
            self.filesystems.pop()
            fails = len(self.files_to_extract) - len(errors)
            if fails == 0:
                print("No files were extracted.")
            elif fails > 0:
                print(f"{fails} files failed to extract. See log file for details.")
                for filename, error in errors:
                    log.write(f"{filename}: {error}\n")
            else:
                print(f"{errors} files were extracted successfully.")

    def close(self):
        self.ewf_handle.close()

