from pytube import YouTube
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import re
import threading

class Application:

    def __init__(self, root):
        self.root = root
        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg="#ffffff")  # Update background color

        top_label = Label(self.root, text="YouTube Download Manager", fg="#ff6347", font=("Helvetica", 36, "bold"))
        top_label.grid(pady=(20, 10))

        link_label = Label(self.root, text="Please Paste Any YouTube Video Link Below", font=("Helvetica", 16))
        link_label.grid(pady=(0, 10))

        self.youtubeEntryVar = StringVar()

        self.youtubeEntry = Entry(self.root, width=70, textvariable=self.youtubeEntryVar, font=("Helvetica", 14))
        self.youtubeEntry.grid(pady=(0, 15), ipady=5)

        self.youtubeEntryError = Label(self.root, text="", font=("Helvetica", 12), fg="red")
        self.youtubeEntryError.grid(pady=(0, 8))

        self.youtubeFileSaveLabel = Label(self.root, text="Choose Directory", font=("Helvetica", 16))
        self.youtubeFileSaveLabel.grid()

        self.youtubeFileDirectoryButton = Button(self.root, text="Directory", font=("Helvetica", 12), command=self.openDirectory)
        self.youtubeFileDirectoryButton.grid(pady=(10, 3))

        self.fileLocationLabel = Label(self.root, text="", font=("Helvetica", 12), fg="blue")
        self.fileLocationLabel.grid()

        self.youtubeChooselabel = Label(self.root, text="Choose the Download Type", font=("Helvetica", 16))
        self.youtubeChooselabel.grid()

        self.downloadChoices = [("Audio MP3", 1), ("Video MP4", 2)]

        self.ChoicesVar = StringVar()
        self.ChoicesVar.set(1)

        for text, mode in self.downloadChoices:
            self.youtubeChoices = Radiobutton(self.root, text=text, font=("Helvetica", 12), variable=self.ChoicesVar, value=mode)
            self.youtubeChoices.grid()

        self.downloadButton = Button(self.root, text="Download", width=10, font=("Helvetica", 12), command=self.checkyoutubelink)
        self.downloadButton.grid(pady=(30, 5))

        self.quitButton = Button(self.root, text="Quit", font=("Helvetica", 12), command=self.root.quit)
        self.quitButton.grid(pady=(10, 10), sticky=E)

    def checkyoutubelink(self):
        self.matchyoutubelink = re.match("^https://www.youtube.com/.", self.youtubeEntryVar.get())
        if not self.matchyoutubelink:
            self.youtubeEntryError.config(text="Invalid YouTube Link", fg="red")
        elif not hasattr(self, 'FolderName'):
            self.fileLocationLabel.config(text="Please Choose a Directory", fg="red")
        else:
            self.downloadWindow()

    def downloadWindow(self):
        self.newWindow = Toplevel(self.root)
        self.root.withdraw()
        self.newWindow.state("zoomed")
        self.newWindow.grid_rowconfigure(0, weight=0)
        self.newWindow.grid_columnconfigure(0, weight=1)

        self.app = SecondApp(self.newWindow, self.youtubeEntryVar.get(), self.FolderName, self.ChoicesVar.get())

    def openDirectory(self):
        self.FolderName = filedialog.askdirectory()

        if len(self.FolderName) > 0:
            self.fileLocationLabel.config(text=self.FolderName, fg="green")
            return True
        else:
            self.fileLocationLabel.config(text="Please Choose A Directory", fg="red")

class SecondApp:

    def __init__ (self, downloadWindow, youtubelink, FolderName, Choices):
        self.downloadWindow = downloadWindow
        self.youtubelink = youtubelink
        self.FolderName = FolderName
        self.Choices = Choices

        self.yt = YouTube(self.youtubelink)
        self.yt.register_on_progress_callback(self.show_progress)
        self.yt.register_on_complete_callback(self.complete_download)

        if Choices == "1":
            self.video_type = self.yt.streams.filter(only_audio=True).first()
        else:
            self.video_type = self.yt.streams.get_highest_resolution()

        self.MaxFileSize = self.video_type.filesize

        self.loadingLabel = Label(self.downloadWindow, text="Downloading in Progress...", font=("Helvetica", 24, "bold"))
        self.loadingLabel.grid(pady=(100, 0))

        self.loadingPercent = Label(self.downloadWindow, text="0%", fg="green", font=("Helvetica", 24))
        self.loadingPercent.grid(pady=(50, 0))

        self.progressbar = ttk.Progressbar(self.downloadWindow, length=500, orient="horizontal", mode="determinate")
        self.progressbar.grid(pady=(50, 0))
        self.progressbar["value"] = 0

        self.quitButton = Button(self.downloadWindow, text="Quit", font=("Helvetica", 12), command=self.downloadWindow.quit)
        self.quitButton.grid(pady=(10, 10), sticky=E)

        threading.Thread(target=self.downloadFile).start()

    def downloadFile(self):
        self.video_type.download(self.FolderName)

    def show_progress(self, stream, chunk, bytes_remaining):
        percent = (100 * (self.MaxFileSize - bytes_remaining)) / self.MaxFileSize
        self.downloadWindow.after(0, self.update_progress, percent)

    def update_progress(self, percent):
        self.loadingPercent.config(text=f"{percent:.2f}%")
        self.progressbar["value"] = percent

    def complete_download(self, stream, file_handle):
        self.downloadWindow.after(0, self.update_complete)

    def update_complete(self):
        self.progressbar.stop()
        self.loadingLabel.config(text="Download Finished", fg="green")
        self.loadingPercent.grid_forget()
        self.progressbar.grid_forget()

        self.downloadFinished = Label(self.downloadWindow, text="Download Finished", font=("Helvetica", 24, "bold"))
        self.downloadFinished.grid(pady=(150, 0))

        self.downloadedFileName = Label(self.downloadWindow, text=self.yt.title, font=("Helvetica", 18))
        self.downloadedFileName.grid(pady=(50, 0))

        MB = float(self.MaxFileSize / 1000000)
        self.downloadFileSize = Label(self.downloadWindow, text=f"{MB:.2f} MB", font=("Helvetica", 18))
        self.downloadFileSize.grid(pady=(50, 0))

if __name__ == "__main__":
    window = Tk()
    window.title("YouTube Download Manager")
    window.state("zoomed")

    app = Application(window)

    mainloop()
