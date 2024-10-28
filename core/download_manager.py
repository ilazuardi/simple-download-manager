# core/download_manager.py
import requests
import threading
import os
import time

class DownloadManager:
    def __init__(self, num_threads=4, max_retries=3):
        self.num_threads = num_threads
        self.max_retries = max_retries
        self.paused_downloads = {}

    def download_chunk(self, url, start, end, filename, part_num, retries=0):
        """Download a specific chunk of the file with retry logic."""
        headers = {'Range': f'bytes={start}-{end}'}
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            with open(f"{filename}.part{part_num}", 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded chunk {part_num}")
        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                wait_time = 2 ** retries
                print(f"Retrying chunk {part_num} in {wait_time} seconds...")
                time.sleep(wait_time)
                self.download_chunk(url, start, end, filename, part_num, retries + 1)
            else:
                print(f"Failed to download chunk {part_num}: {e}")

    def start_download(self, url, filename):
        """Divide the download into chunks and start threads."""
        response = requests.head(url)
        file_size = int(response.headers.get('content-length', 0))
        chunk_size = file_size // self.num_threads

        threads = []
        for i in range(self.num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < self.num_threads - 1 else file_size
            thread = threading.Thread(
                target=self.download_chunk, args=(url, start, end, filename, i)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.combine_chunks(filename)
        print(f"Download complete: {filename}")

    def combine_chunks(self, filename):
        """Combine all downloaded chunks into one file."""
        with open(filename, 'wb') as final_file:
            for i in range(self.num_threads):
                part_filename = f"{filename}.part{i}"
                with open(part_filename, 'rb') as part_file:
                    final_file.write(part_file.read())
                os.remove(part_filename)

    def pause_download(self, filename):
        print(f"Paused download: {filename}")
        self.paused_downloads[filename] = True

    def resume_download(self, url, filename):
        print(f"Resuming download: {filename}")
        self.paused_downloads.pop(filename, None)
        self.start_download(url, filename)
