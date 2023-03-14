from PySide6.QtCore import QFile, QSaveFile, QIODevice, Signal, QThread, Slot
from urllib.request import urlopen
from urllib.error import URLError, HTTPError, ContentTooShortError

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
            try:
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
            except HTTPError as e:
                print(f"QThread {self.name} encountered an HTTPError ({e.code}) in creating the request")
                print(f"Headers:\n{e.headers}\n")
                print(e.reason)
            except ContentTooShortError as e:
                print(f"QThread {self.name} encountered a ContentTooShortError in reading the response")
                print(f"Truncated Data:\n{e.content}\n")
                print(e.reason) 
            except URLError as e:
                print(f"QThread {self.name} encountered a URLError in creating the request")
                print(e.reason)           
        else:
            error = self.buffer.errorString()
            print(f"Cannot open device: {error}")
        self.thread_complete.emit(self.name)

    ###########################################################################

    @Slot()
    def terminate(self):
        print(f"QThread {self.name} terminated")
        super().terminate()