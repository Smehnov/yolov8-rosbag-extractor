from pathlib import Path
import json
from rosbags.highlevel import AnyReader
import numpy as np
from PIL import Image
import glob

from ultralytics import YOLO

model = YOLO(f'yolov8n.pt')
names = model.names


def process_file(filepath):
    labels = set()

    result = {}
    objects = []
    with AnyReader([Path(filepath)]) as reader:
        print(reader.connections)
        connections = [x for x in reader.connections if
                       x.topic in ['/spot/camera/frontright/image', '/spot/camera/frontleft/image']]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
            w = msg.width

            im = Image.fromarray(np.reshape(msg.data, (-1, w)))
            im = im.rotate(-90, expand=True)
            im.save('temp.png')
            results = model.predict(source='temp.png', classes=0, conf=0.75)
            # boxes = results[0].boxes.xyxy
            # results[0].boxes.conf

            for r in results:
                boxes = r.boxes.xyxy.tolist()
                if (len(boxes) == 0):
                    continue
                objects.append({
                    'topic': connection.topic,
                    'timestamp': timestamp,
                    'boxes': boxes,
                    'confs': r.boxes.conf.tolist()

                })
                for c in r.boxes.cls:
                    labels.add(names[int(c)])
    result = {
        'objects': objects,
        'labels': labels
    }
    return result


def main():
    filepaths = glob.glob('/input/*')
    result = process_file(filepaths[0])
    print(result)
    with open("/output.result", "w") as f:
        f.write(json.dumps(result))

if __name__=='__main__':
    main()
