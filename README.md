# Obtain Source Separation with [Spleeter](https://github.com/deezer/spleeter)

This service is connected with ['Manager'](https://github.com/mer-team/Tests/blob/rabbit-manager/Manager/manager.js) service through [RabbitMQ](https://www.rabbitmq.com/). Takes the original audio and separates its sources depending on the model in use.

You need to download from [spleeter releases](https://github.com/deezer/spleeter/releases/tag/v1.4.0) the pretrained model which you want to use.

Run `python3.7 separate.py`

## Input through RabbitMQ

The input is the videoID which is the name of the audio file that you want to perform the separation.

## Output
Folder with the name of the song (videoID) containing the audio files separated (e.g. accompaniment.wav and vocals.wav).

Through RabbitMQ:
```javascript
{ Service: 'SourceSeparation', Result: { vID: 'videoID' } }

```