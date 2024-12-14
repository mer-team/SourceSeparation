# Separate Audio Sources with [Spleeter](https://github.com/deezer/spleeter)

This service is connected with ['Manager'](https://github.com/mer-team/Tests/blob/rabbit-manager/Manager/manager.js) service through [RabbitMQ](https://www.rabbitmq.com/). Takes the original audio and separates its sources depending on the model in use.

You need to download from [spleeter releases](https://github.com/deezer/spleeter/releases/tag/v1.4.0) the pretrained model which you want to use and place it on src folder.

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
| `/Audios` | Folder where the downloaded audio files are accessed and the separated sources are saved |

### Run Local Microservice

Note: this uses our unofficial spleeter docker image as base. If needed, first read the [Build Unofficial Spleeter base Docker Image](#spleeter) (below).

Run a local RabbitMQ container, admin panel can be accessed at http://localhost:15672 :
```bash
docker run -d -e RABBITMQ_DEFAULT_USER=merUser -e RABBITMQ_DEFAULT_PASS=passwordMER -p 15672:15672 -p 5672:5672 rabbitmq:3-management-alpine
```

Build local `sourceSeparation` from source:
```bash
docker build -t source-separation:local .
```

If needed, the version of the base image to use can be passed using build-args - must be one of our spleeter images, e.g., to use the `mer-team/spleeter:2.4.0-stems-local` pass:
```bash
docker build --build-arg BASE_VERSION=2.4.0-stems-local -t source-separation:local .
```

To run the local image `source-separation`:
```bash
docker run --rm -e TIME=10 -e USER=merUser -e PASS=passwordMER -e HOST=127.0.0.1 -e PORT=5672 -e MNG_PORT=15672 --net=host -v "Audios:/Audios" source-separation:local
```

Tun the official `source-separation` image (on DockerHub) locally:
```bash
docker run -e TIME=10 -e USER=merUser -e PASS=passwordMER -e HOST=localhost -e MNG_PORT=15672 --net=host -v "<Local DIR>:/Audios" merteam/source-separation:latest
```

If needed for some reason, open an interactive shell in a source-separation container:
```bash
docker run --rm -it --entrypoint bash --net=host -v .:/output -v "Audios:/Audios" -e USER=merUser -e PASS=passwordMER source-separation:local
```

## Input through RabbitMQ
If used though RabbitMQ, the input is a JSON object containing:
* `inputFile`: name of the file to be segmented, which should be available in the `/Audios` folder.
* `segmentLength`: length (duration) of the desired segments in seconds
* `overlap`: the segment overlap in seconds (0 = no overlap, 10 = each segment contains the last 10 seconds of the previous segment)

Example:
```json
{
	"inputFile": "JiF3pbvR5G0.wav",
	"stems": 2
}
```

## Build Unofficial Spleeter base Docker image <a id="spleeter"></a>

This microservice uses Spleeter by Deezer. Unfortunately the official docker image is outdated and uses a larger than desired (for use) base image. Thus, we start by building a base image that contains spleeter. The rationale behind this is that it can be used by other services / projects in the future.

To build a local image `mer-team/spleeter` from source (see the `spleeter.dockerfile` for details, at the moment there is no GPU support):
```bash
docker build -t mer-team/spleeter:2.4.0-local -f spleeter.dockerfile .
```

If needed, both python and spleeter version can be passed as build-args:
```bash
docker build --build-arg PYTHON_VERSION=3.10 --build-arg SPLEETER_VERSION=2.4.0 -t mer-team/spleeter:2.4.0-local -f spleeter.dockerfile .
```

### Including the Spleeter Pretrained Models

By default, spleeter will download the required model when needed. To avoid this we build a second image, starting from the previous `mer-team/spleeter`, that downloads the `2stems`, `4stems` and `5stems` models to `/model` folder.

Using the `mer-team/spleeter` image as base, the pretrained models image can be build with:
```bash
docker build -t mer-team/spleeter:2.4.0-stems -f spleeter-models.dockerfile .
```

Again, both image  `BASE_VERSION` and spleeter `MODEL_VERSION` can be passed as build_args. In addition, specific spleeter stem models can be excluded (`TWO_STEMS`, `FOUR_STEMS` and `FIVE_STEMS`):
```bash
docker build --build-arg BASE_VERSION=2.4.0-local --build-arg MODEL_VERSION=1.4.0 --build-arg FIVE_STEMS=false -t mer-team/spleeter:2.4.0-stems-local -f spleeter-models.dockerfile .
```

### Test the Spleeter Image / Run Spleeter CLI

The spleeter (unofficial) image can be used to run spleeter cli commands. For instance, to launch an interative shell and separate a file:

```bash
# first run the image (contained will be removed after exit, --rm)
# note that the current folder is being mounted as /output inside the container
# so the resulting files will be available locally (host)
docker run --rm -it --entrypoint bash -v .:/output mer-team/spleeter:2.4.0-stems-local
```
Now, inside the container:
```bash
# check spleeter and python versions
root@c9e9c87478e4:/ spleeter --version
Spleeter Version: 2.4.0

root@c9e9c87478e4:/ python --version
Python 3.10.12

# get an audio file to split
curl -fsSL https://github.com/deezer/spleeter/raw/master/audio_example.mp3 -o audio_example.mp3

# use spleeter to separate the file
root@c9e9c87478e4:/ spleeter separate -p spleeter:2stems -o /output -f {filename}-{instrument}.{codec} audio_example.mp3
INFO:spleeter:File /output/audio_example-accompaniment.wav written succesfully
INFO:spleeter:File /output/audio_example-vocals.wav written succesfully

root@c9e9c87478e4:/ exit
```

## NOTES

* Building with python3.10-alpine fails when installing tensorflow
* Spleeter requires a lot of RAM. Also, Docker Desktop on windows is limited by the WSL2 RAM (limit is defined with the .wslconfig).
    * One good strategy could be split file in smaller segments before source separate
	* Increasing the WSL" limit to 16GB makes it possible to run spleeter in a 6m49s wav file (8.02GB container mem usage peak), mp3 seemed to use less (3.87), second run on the same wav = 4.67GB used.
	* 