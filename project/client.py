# -*- coding: utf-8 -*-
import os
import random
import time

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow.contrib.util as util
from grpc.beta import implementations
from skimage import transform
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2
import project.label_information as label_infomation
import os, stat
from PIL import Image
from io import StringIO, BytesIO


class ClientAPI(object):
    def __init__(self, host='39.108.183.209', port='9000'):
        self.host = host
        self.port = port

    def send_request(self, image_dir, model_name, signature_name,
                     input_name, other_k=None):
        x = time.time()
        channel = implementations.insecure_channel(self.host, int(self.port))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        image, scale = change_image_h_w(image_dir)
        abs_img_dir = 'image/' + image_dir.split('/')[-1]
        return self.process(abs_img_dir, image, input_name, model_name, other_k,
                            signature_name,
                            stub, scale)

    def process(self, abs_img_dir, image, input_name, model_name, other_k, signature_name, stub, scale):
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
        results = {'result': result,
                   'abs_img_dir': abs_img_dir,
                   'scale': scale}
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
            bboxes.append(np.array([boexes[i, 1]*results['scale'],
                                    boexes[i, 0]*results['scale'],
                                    boexes[i, 3]*results['scale'],
                                    boexes[i, 2]*results['scale']]))
        classes = np.array(classes)
        scores = np.array(scores)
        bboxes = np.array(bboxes)
        results = ClientAPI.change_image(results, classes, scores, bboxes, label_infomation.face)
        return results

    @staticmethod
    def detection_result_ssd(results):
        result = results['result']
        bboxes = np.array(result.outputs['bboxes'].float_val).reshape([-1, 4])
        scores = np.array(result.outputs['scores'].float_val).reshape([-1, ])
        classes = np.array(result.outputs['classes'].int64_val).reshape([-1, ])
        results = ClientAPI.change_image(results, classes, scores, bboxes,
                                         label_infomation.ssd_voc_en, change=True)
        return results

    @staticmethod
    def change_image(results, classes, scores, bboxes, label, change=False):
        image_dir = results['abs_img_dir']
        abs = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        image = plt.imread(os.path.join(abs, 'media', image_dir))
        colors = ClientAPI.plt_bboxes(image, classes, scores, bboxes, label, change=change)
        results['colors'] = ClientAPI.rgb_to_HEX_float(colors)
        plt.savefig(os.path.join(abs, 'media', image_dir), bbox_inches='tight')
        os.chmod(os.path.join(abs, 'media', image_dir), stat.S_IRWXO | stat.S_IRWXU)
        return results

    @staticmethod
    def rgb_to_HEX_float(colors):
        for key in list(colors.keys()):
            item = colors[key]
            color = "#"
            color += str(hex(int(item[0] * 255))).replace('x', '0')[-2:]
            color += str(hex(int(item[1] * 255))).replace('x', '0')[-2:]
            color += str(hex(int(item[2] * 255))).replace('x', '0')[-2:]
            colors[key] = color
        return colors

    @staticmethod
    def rgb_to_HEX_int(colors):
        for key in list(colors.keys()):
            item = colors[key]
            color = "#"
            color += str(hex(int(item[0]))).replace('x', '0')[-2:]
            color += str(hex(int(item[1]))).replace('x', '0')[-2:]
            color += str(hex(int(item[2]))).replace('x', '0')[-2:]
            colors[key] = color
        return colors

    @staticmethod
    def plt_bboxes(img, classes, scores, bboxes, label,
                   figsize=(10, 10), linewidth=1.5, change=False):
        """Visualize bounding boxes. Largely inspired by SSD-MXNET!
        """
        fig = plt.figure(figsize=figsize)

        plt.imshow(img)
        plt.axis('off')

        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
        plt.margins(0, 0)
        height = img.shape[0]
        width = img.shape[1]
        colors = dict()
        show_caption = True
        if len(classes) > 15:
            show_caption = False
        for i in range(classes.shape[0]):
            cls_id = int(classes[i])
            if cls_id >= 0:
                score = scores[i]
                if label[int(cls_id)] not in colors:
                    colors[label[int(cls_id)]] = (random.random(), random.random(), random.random())
                if change:
                    bboxes[i] *= [height, width, height, width]
                ymin = int(bboxes[i, 0])
                xmin = int(bboxes[i, 1])
                ymax = int(bboxes[i, 2])
                xmax = int(bboxes[i, 3])
                rect = plt.Rectangle((xmin, ymin), xmax - xmin,
                                     ymax - ymin, fill=False,
                                     edgecolor=colors[label[int(cls_id)]],
                                     linewidth=linewidth)
                plt.gca().add_patch(rect)
                if show_caption:
                    class_name = str(label[int(cls_id)])
                    plt.gca().text(xmin, ymin - 2,
                                   '{:s} | {:.3f}'.format(class_name, score),
                                   bbox=dict(facecolor=colors[label[int(cls_id)]], alpha=0.5),
                                   fontsize=12, color='white')
        return colors


def change_image_h_w(image_dir):
    img = Image.open(image_dir)
    w, h = img.size
    max_h_w = max(h, w)
    s = BytesIO()
    if max_h_w > 1000:
        scale = max_h_w/1000
        img = img.resize((int(w/scale), int(h/scale)))
        img.save(s, format='JPEG')
    else:
        img.save(s, format='JPEG')
        scale = 1
    return s.getvalue(), scale
