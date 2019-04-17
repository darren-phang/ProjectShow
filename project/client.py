# -*- coding: utf-8 -*-
from grpc.beta import implementations
import numpy as np
import time
import tensorflow as tf
import tensorflow.contrib.util as util
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2
import random
from PIL import Image
import matplotlib.pyplot as plt
from skimage import transform
import os


class ClientAPI(object):
    def __init__(self, host='39.108.183.209', port='9000'):
        self.host = host
        self.port = port

    def send_request(self, image_dir, model_name, signature_name,
                     input_name, restore=True, other_k=None):
        x = time.time()
        channel = implementations.insecure_channel(self.host, int(self.port))

        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        abs_img_dir = ''
        # 打开图片并裁剪成600*600
        if restore:
            image_name = image_dir.split('/')[-1].split('.')[0]
            image_restore = np.array(plt.imread(image_dir))
            img_resize = transform.resize(image_restore, (500, 750))
            abs = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            abs_img_dir = 'image_adjust/' + image_name + '_adjust.jpg'
            plt.imsave(os.path.join(abs, 'media', abs_img_dir), img_resize)
            image = open(os.path.join(abs, 'media', abs_img_dir), 'rb').read()
        else:
            image = open(image_dir, 'rb').read()
            abs_img_dir = 'image/' + image_dir.split('/')[-1]
        print('send request')
        request = predict_pb2.PredictRequest()
        # 端口里面的名字什么的，设置的第一级为test，第二级为predict_images
        request.model_spec.name = model_name
        request.model_spec.signature_name = signature_name
        # protobuf 序列化并发送请求和接受结果
        request.inputs[input_name].CopyFrom(util.make_tensor_proto(image, dtype=tf.string))
        if other_k is not None:
            for key in list(other_k.keys()):
                name, _type = key.split(':')
                if _type == 'int':
                    this_type = tf.int32
                elif _type == 'float':
                    this_type = tf.float32
                request.inputs[name].CopyFrom(util.make_tensor_proto(other_k[key], dtype=this_type))

        result = stub.Predict(request, 90.0)  # 时限
        # 处理返回的信息
        results = {'result': result, 'abs_img_dir': abs_img_dir}
        return results

    @staticmethod
    def classification_result(results):
        result = results['result']
        labels = result.outputs['classes'].string_val
        result = np.array(result.outputs['scores'].float_val)
        label_and_percentage = {}
        for i, label in enumerate(labels):
            label_and_percentage[str(label.decode())] = float(result[i])
        return label_and_percentage

    @staticmethod
    def detection_result_face(results):
        result = results['result']
        boexes = np.array(result.outputs['predict_boxes'].float_val).reshape([-1, 5])
        classes = []
        scores = []
        bboxes = []
        for i in range(boexes.shape[0]):
            classes.append(1)
            scores.append(boexes[i, 4])
            bboxes.append(np.array([boexes[i, 1], boexes[i, 0],
                                   boexes[i, 3], boexes[i, 2]]))
        classes = np.array(classes)
        scores = np.array(scores)
        bboxes = np.array(bboxes)
        results = ClientAPI.change_image(results, classes, scores, bboxes)
        return results

    @staticmethod
    def detection_result_ssd(results):
        pass

    @staticmethod
    def change_image(results, classes, scores, bboxes):
        image_dir = results['abs_img_dir']
        abs = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        image = plt.imread(os.path.join(abs, 'media', image_dir))
        ClientAPI.plt_bboxes(image, classes, scores, bboxes)
        plt.savefig(os.path.join(abs, 'media', image_dir))

        return results

    @staticmethod
    def plt_bboxes(img, classes, scores, bboxes, figsize=(10, 10), linewidth=1.5):
        """Visualize bounding boxes. Largely inspired by SSD-MXNET!
        """
        fig = plt.figure(figsize=figsize)
        plt.imshow(img)
        plt.axis('off')
        height = img.shape[0]
        width = img.shape[1]
        colors = dict()
        for i in range(classes.shape[0]):
            cls_id = int(classes[i])
            if cls_id >= 0:
                score = scores[i]
                if cls_id not in colors:
                    colors[cls_id] = (random.random(), random.random(), random.random())
                ymin = int(bboxes[i, 0])
                xmin = int(bboxes[i, 1])
                ymax = int(bboxes[i, 2])
                xmax = int(bboxes[i, 3])
                rect = plt.Rectangle((xmin, ymin), xmax - xmin,
                                     ymax - ymin, fill=False,
                                     edgecolor=colors[cls_id],
                                     linewidth=linewidth)
                plt.gca().add_patch(rect)
                class_name = str(cls_id)
                plt.gca().text(xmin, ymin - 2,
                               '{:s} | {:.3f}'.format(class_name, score),
                               bbox=dict(facecolor=colors[cls_id], alpha=0.5),
                               fontsize=12, color='white')


if __name__ == '__main__':
    api = ClientAPI()
    api.send_request('/Users/darrenpang/Documents/图片/goldfish.jpeg')
