import tornado.ioloop
import tornado.web
import json
import requests
import subprocess
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os.path
from mutagen.mp3 import MP3


S2T_USERNAME="<YOUR SPEECH2TEXT USER>"
S2T_PASSWD="<YOUR SPEECH2TEXT PASSWORD>"
ALCHEMY_KEY = "<YOUR ALCHEMY API KEY>"

class InsightHandler(tornado.web.RequestHandler):

    MAX_WORKERS = 1000
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def request_s2t(self, input_file):

        text_response = requests.post(
            url="https://stream.watsonplatform.net/speech-to-text/api/v1/recognize",
            headers={"Content-Type": "audio/wav"},
            data=open(input_file, "rb"),
            params={"continuous": "true"},
            auth=(S2T_USERNAME, S2T_PASSWD),
            verify=False)

        result = text_response._content
        return result

    @run_on_executor
    def alchemy_request(self, text):
        url="http://gateway-a.watsonplatform.net/calls/text/TextGetRankedKeywords"
        r = requests.post(
            url=url,
            params={'apikey': ALCHEMY_KEY, 'text': text, 'outputMode': 'json'},
            headers={'application':'x-www-form-urlencoded'})
        res = json.loads(r._content.decode('utf8'))
        return res

    def _split_wav_file(self, audio_file, audio_chunk_in_s, approx_audio_length):

        split_files = []
        # Split first y min into x sec chunks
        for i in zip(
                range(1, approx_audio_length-1, audio_chunk_in_s),
                range(audio_chunk_in_s, approx_audio_length, audio_chunk_in_s)):
            output_file = "splits/" + audio_file.strip(".wav") + "_" + str(i[0]) + "_" + str(i[1]) + ".wav"
            cmd = [
                "qwavcut",
                "-B " + str(i[0]) + "s",
                "-E " + str(i[1]) + "s",
                "-o " + output_file,
                audio_file
            ]
            print(cmd)
            subprocess.call(" ".join(cmd), shell=True)
            split_files.append(output_file)

        return split_files

    def convert_to_wav(self, path_to_mp3):
        if not os.path.isfile(path_to_mp3 + ".wav"):
            cmd = ["soundconverter", "-b " + path_to_mp3, "-m wav", "-s .wav"]
            print(cmd)
            subprocess.call(" ".join(cmd), shell=True)
        return path_to_mp3 + ".wav"

    @tornado.gen.coroutine
    def speech2text(self, audio_file, length_of_podcast):

        audio_chunk_in_s = 60
        approx_audio_length = int(length_of_podcast)

        split_files = self._split_wav_file(audio_file, audio_chunk_in_s, approx_audio_length)

        # Create requests
        results = yield [self.request_s2t(f) for f in split_files]

        full_transcript = []
        for result in results:
            result_as_json = json.loads(result.decode('utf8'))
            full_transcript.append(result_as_json["results"][0]["alternatives"][0]["transcript"])

        return " ".join(full_transcript)

    def download_podcast_url(self, url, path):
        # Will do quick-and-dirth caching by not re-downloading file
        if not os.path.isfile(path):
            print("Downloading...")
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(4000):
                        f.write(chunk)
        else:
            print("Already saw this url, will use existing copy...")
        return path

    @staticmethod
    def find_length_of_mp3(path):
        audio = MP3(path)
        return audio.info.length

    @tornado.gen.coroutine
    def post(self):
        print(self.request.body.decode('utf8'))
        url = json.loads(self.request.body.decode('utf8'))["url"]

        # Use this to make us skip re-downloading same file
        # multiple times.
        hasher = hashlib.md5()
        hasher.update(url.encode('utf-8'))
        url_hash = hasher.hexdigest()

        json_dump_file = url_hash + ".json"

        # Ugliest "db" you can think of...
        if os.path.isfile(json_dump_file):
            print("I already have the terms, will just load them...")
            terms = ""
            with open(json_dump_file) as data_file:
                terms = json.load(data_file)
            self.write(terms)
        else:
            print("I need to get the terms from watson...")
            path_to_file = self.download_podcast_url(url, url_hash)
            length_of_podcast = self.find_length_of_mp3(path_to_file)
            path_to_wav = self.convert_to_wav(path_to_file)
            text = yield self.speech2text(path_to_wav, length_of_podcast)
            terms = yield self.alchemy_request(text)

            with open(url_hash + ".json", 'w') as outfile:
                json.dump(terms, outfile)

            self.write(terms)


static_path = "static/"
application = tornado.web.Application([
    (r"/insight", InsightHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path})
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
