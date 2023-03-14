from PySide6.QtCore import QFile, QSaveFile, QIODevice, Signal, QThread
from urllib.request import urlopen

class DownloaderThread(QThread):

    # Signal to add a file's full size to the progress bar's maximum
    add_total_progress = Signal(int)
    #Signal to add the current file progress to the progress bar's current progress
    add_current_progress = Signal(int)
    # Signal to indicate the file has completed downloading
    thread_complete = Signal(str)

    def __init__(self, url, file, name):
        super().__init__()
        self.url = url
        self.file = file
        self.name = name
        self.buffer: QSaveFile = None
    ###########################################################################

    def run(self):
        # if file exists, delete to redownload
        if QFile.exists(self.file):
            QFile.remove(self.file)

        # Do the work!
        self.buffer = QSaveFile(self.file)
        self.buffer.setDirectWriteFallback(True)
        if self.buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            # HTTP GET
            chunk_size = 1024
            kb = 1024
            with urlopen(self.url) as resp:
                self.add_total_progress.emit(int(resp.info()["Content-Length"])/kb)
                while True:
                    chunk = resp.read(chunk_size)
                    if chunk is None:
                        continue
                    elif chunk == b"":
                        break
                    self.buffer.write(chunk)
                    self.add_current_progress.emit(chunk_size/kb) # sending progress in kb to not overflow the progress bar
            self.buffer.commit()
            self.thread_complete.emit(self.name)
        else:
            error = self.buffer.errorString()
            print(f"Cannot open device: {error}")

    ###########################################################################
