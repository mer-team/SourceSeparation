# Obtain Source Separation with [Spleeter](https://github.com/deezer/spleeter)

This service is connected with ['Manager'](https://github.com/mer-team/Tests/blob/rabbit-manager/Manager/manager.js) service through [RabbitMQ](https://www.rabbitmq.com/). Takes the original audio and separates its sources depending on the model in use.

You need to download from [spleeter releases](https://github.com/deezer/spleeter/releases/tag/v1.4.0) the pretrained model which you want to use  and place it on src folder.

Run `python3.7 separate.py`

## Input through RabbitMQ

The input is the videoID which is the name of the audio file that you want to perform the separation.

## Output
Folder with the name of the song (videoID) containing the audio files separated (e.g. accompaniment.wav and vocals.wav).

Through RabbitMQ:
```javascript
{ Service: 'SourceSeparation', Result: { vID: 'videoID' } }

```

### Docker Params
| Arg | Default | Description |
| --- | --- | --- |
| HOST | localhost | RabbitMQ host |
| USER | guest | HTTP basic auth username  |
| PASS | guest | HTTP basic auth password |
| PORT | 5672 | RabbitMQ Port |
| MNG_PORT | 15672 | RabbitMQ Management Port |
| TIME | 10 | Timeout to check if the service is up |

### Volumes
| Container Path | Description |
| --- | --- |
| `/Audios` | Folder where the downloaded audio files are accessed |
| `/Separation` | Folder where the separated sources are saved |

### Run Local Microservice
Run Rabbit
```
docker run -d -e RABBITMQ_DEFAULT_USER=merUser -e RABBITMQ_DEFAULT_PASS=passwordMER -p 15672:15672 -p 5672:5672 rabbitmq:3-management-alpine
```

Build local `sourceSeparation` from source
```
docker build -t sourceseparation:local .
```

Run local `sourceSeparation`
```
docker run -e TIME=10 -e USER=merUser -e PASS=passwordMER -e HOST=localhost -e MNG_PORT=15672 --net=host -v "<Local DIR>:/Audios" -v "<Local DIR>:/Separation" sourceseparation:local
```

Run official `sourceSeparation` image locally
```
docker run -e TIME=10 -e USER=merUser -e PASS=passwordMER -e HOST=localhost -e MNG_PORT=15672 --net=host -v "<Local DIR>:/Audios" -v "<Local DIR>:/Separation" merteam/sourceseparation:latest
```