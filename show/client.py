# -*- coding: utf-8 -*-
from grpc.beta import implementations
import numpy as np
import time
import tensorflow as tf
import tensorflow.contrib.util as util
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2
from PIL import Image
import matplotlib.pyplot as plt
from skimage import transform
import os


class RockApi(object):
    def __init__(self, host='39.108.183.209', port='9000'):
        self.host = host
        self.port = port

    def send_request(self, image_dir, restore=True):
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
        # image = image.resize((299, 299), Image.BILINEAR)
        # image_tf = tf.placeholder(tf.float32, [None, None, 3])
        # # image_out = tf.image.per_image_standardization(image_tf)
        # image_out = tf.image.resize_images(image_tf, [399, 399])
        # sess = tf.InteractiveSession()
        # image = sess.run(image_out, feed_dict={image_tf: image})
        # np.save('C:\\Users\pangd\Desktop/1.npy', image)
        # image = image.resize((399, 399), Image.BILINEAR)
        # plt.imshow(image)
        # plt.show()
        # center = [image.shape[0]//2, image.shape[1]//2]
        # image = image[center[0]-300:center[0]+300, center[1]-300:center[1]+300, :]
        # new_im = Image.fromarray(image.astype(np.float32))
        # new_im.save('C:\\Users\pangd\Desktop/1.jpg')
        print('send request')
        request = predict_pb2.PredictRequest()
        # 端口里面的名字什么的，设置的第一级为test，第二级为predict_images
        request.model_spec.name = 'inception'
        request.model_spec.signature_name = 'predict_images'
        # protobuf 序列化并发送请求和接受结果
        request.inputs['images'].CopyFrom(util.make_tensor_proto(image, dtype=tf.string))
        result = stub.Predict(request, 90.0)  # 时限
        # 处理返回的信息
        print(result)
        labels = result.outputs['classes'].string_val
        result = np.array(result.outputs['scores'].float_val)
        label_and_percentage = {}
        for i, label in enumerate(labels):
            label_and_percentage[str(label.decode())] = float(result[i])
            # print(label.decode(), result[i])
        # print(label_and_percentage)
        # time_all = time.time()-x
        # s = self.top_k(topk, result)
        # s += 'spend %fs\n' % time_all
        # print('spend %fs' % time_all)
        return label_and_percentage, abs_img_dir
        # return s


if __name__ == '__main__':
    api = RockApi()
    api.send_request('/Users/darrenpang/Documents/图片/goldfish.jpeg')
