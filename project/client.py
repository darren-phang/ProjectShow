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
from memory_profiler import profile

class ClientAPI(object):
    def __init__(self, host='39.108.183.209', port='9000'):
        self.host = host
        self.port = port
        self.dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def send_request(self, image_dir, model_name, signature_name,
                     input_name, _id, other_k=None):
        channel = implementations.insecure_channel(self.host, int(self.port))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        image, scale = change_image_h_w(image_dir)
        abs_img_dir = os.path.join('image', _id, image_dir.split('/')[-1])
        return self.process(abs_img_dir, image, input_name, model_name, other_k,
                            signature_name,
                            stub, scale)

    def send_request_by_image(self, img, model_name, signature_name,
                              input_name, other_k=None):
        channel = implementations.insecure_channel(self.host, int(self.port))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        return self.process('None', img, input_name, model_name, other_k,
                            signature_name,
                            stub, 0)

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
        # os.popen("chmod 777 " + os.path.join(self.dir_path, 'media', abs_img_dir)).readlines()
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
            bboxes.append([boexes[i, 0]*results['scale'],
                           boexes[i, 1]*results['scale'],
                           boexes[i, 2]*results['scale'],
                           boexes[i, 3]*results['scale']])
        colors = dict()
        label = label_infomation.face
        for i in range(len(classes)):
            cls_id = int(classes[i])
            if cls_id >= 0:
                if label[int(cls_id)] not in colors:
                    colors[label[int(cls_id)]] = (random.random(), random.random(), random.random())

        # classes = np.array(classes)
        # scores = np.array(scores)
        # bboxes = np.array(bboxes)
        # results = ClientAPI.change_image(results, classes, scores, bboxes, label_infomation.face)
        # return results
        return {"classes": classes, "scores": scores, "bboxes": bboxes,
                "colors": ClientAPI.rgb_to_HEX_float(colors), "name": label_infomation.face_list}

    @staticmethod
    def detection_result_ssd(results):
        result = results['result']
        _bboxes = np.array(result.outputs['bboxes'].float_val).reshape([-1, 4])
        _scores = np.array(result.outputs['scores'].float_val).reshape([-1, ])
        _classes = np.array(result.outputs['classes'].int64_val).reshape([-1, ])
        # results = ClientAPI.change_image(results, classes, scores, bboxes,
        #                                  label_infomation.ssd_voc_en, change=True)
        # return results
        classes = []
        scores = []
        bboxes = []
        for i in range(_bboxes.shape[0]):
            classes.append(int(_classes[i]))
            scores.append(_scores[i])
            bboxes.append([_bboxes[i, 1],
                           _bboxes[i, 0],
                           _bboxes[i, 3],
                           _bboxes[i, 2]])
        colors = dict()
        label = label_infomation.ssd_voc_en
        for i in range(len(classes)):
            cls_id = int(classes[i])
            if cls_id >= 0:
                if label[int(cls_id)] not in colors:
                    colors[label[int(cls_id)]] = (random.random(), random.random(), random.random())

        return {"classes": classes, "scores": scores, "bboxes": bboxes,
                "colors": ClientAPI.rgb_to_HEX_float(colors), "name": label_infomation.ssd_voc_en_list}

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
        if len(classes) > 10:
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
    with Image.open(image_dir) as img:
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
        value = s.getvalue()
        s.close()
    return value, scale


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def change_image_path(base_path, image_name, id):
    check_dir(os.path.join(base_path, id))
    abs_image_dir_old = os.path.join(base_path, image_name)
    abs_image_dir_new = os.path.join(base_path, id, image_name)
    os.renames(abs_image_dir_old, abs_image_dir_new)
    return abs_image_dir_new
