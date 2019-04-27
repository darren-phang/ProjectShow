/*
    三个参数
    file：一个是文件(类型是图片格式)，
    w：一个是文件压缩的后宽度，宽度越小，字节越小
    objDiv：一个是容器或者回调函数
    photoCompress()
     */
function photoCompress(file, w, objDiv) {
    var ready = new FileReader();
    /*开始读取指定的Blob对象或File对象中的内容. 当读取操作完成时,readyState属性的值会成为DONE,如果设置了onloadend事件处理程序,则调用之.同时,result属性中将包含一个data: URL格式的字符串以表示所读取文件的内容.*/
    ready.readAsDataURL(file);
    ready.onload = function () {
        var re = this.result;
        canvasDataURL(re, w, objDiv)
    }
}

function canvasDataURL(path, obj, callback) {
    var img = new Image();
    img.src = path;
    img.onload = function () {
        var that = this;
        // 默认按比例压缩
        var w = that.width,
            h = that.height,
            scale = w / h;
        w = obj.width || w;
        h = obj.height || (w / scale);
        var quality = 0.7;  // 默认图片质量为0.7
        //生成canvas
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        // 创建属性节点
        var anw = document.createAttribute("width");
        anw.nodeValue = w;
        var anh = document.createAttribute("height");
        anh.nodeValue = h;
        canvas.setAttributeNode(anw);
        canvas.setAttributeNode(anh);
        ctx.drawImage(that, 0, 0, w, h);
        // 图像质量
        if (obj.quality && obj.quality <= 1 && obj.quality > 0) {
            quality = obj.quality;
        }
        // quality值越小，所绘制出的图像越模糊
        var base64 = canvas.toDataURL('image/jpeg', quality);
        // 回调函数返回base64的值
        callback(base64);
    }
}

/**
 * 将以base64的图片url数据转换为Blob
 * @param urlData
 *            用url方式表示的base64图片数据
 */

function convertBase64UrlToBlob(urlData) {
    var arr = urlData.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type: mime});
}


var xhr;

//上传文件方法
function UpladFile(type) {
    if (validate_required(document.getElementById("file"), "Please choose a picture at least!") == false) {
        return;
    }
    var fileObj = document.getElementById("file").files[0]; // js 获取文件对象
    //http://localhost:8000/project/project_show/1/classification/
    var url = "http://"; // 接收上传文件的后台地址
    var url_list = window.location.href.split('/');
    var id = url_list[url_list.length - 3];
    for (var i = 2; i < url_list.length - 4; i++) {
        url += url_list[i];
        url += "/";
    }
    if (type == 1) {
        url += ("classification/" + id + "/");
    }
    if (type == 2) {
        url += ("detection/" + id + "/");
    }
    var form = new FormData(); // FormData 对象

    var quality_set = 16 / (fileObj.size / 1024 / 1024);

    if (fileObj.size / 1024 > 1025) { //大于1M，进行压缩上传
        photoCompress(fileObj, {
            quality: 0.1 * quality_set
        }, function (base64Codes) {
            var bl = convertBase64UrlToBlob(base64Codes);
            form.append("img", bl, "img_" + Date.parse(new Date()) + ".jpg"); // 文件对象

            xhr = new XMLHttpRequest();  // XMLHttpRequest 对象
            xhr.open("post", url, true); //post方式，url为服务器请求地址，true 该参数规定请求是否异步处理。
            if (type == 1) {
                xhr.onload = uploadComplete_for_classification; //请求完成
            }
            if (type == 2) {
                xhr.onload = uploadComplete_for_detection;
            }
            xhr.onerror = uploadFailed; //请求失败

            xhr.upload.onprogress = progressFunction;//【上传进度调用方法实现】
            xhr.upload.onloadstart = function () {//上传开始执行方法
                ot = new Date().getTime();   //设置上传开始时间
                oloaded = 0;//设置上传开始时，以上传的文件大小为0
            };
            xhr.send(form); //开始上传，发送form数据
        });
    } else { //小于等于1M 原图上传
        form.append("img", fileObj, "img_" + Date.parse(new Date()) + ".jpg"); // 文件对象
        xhr = new XMLHttpRequest();  // XMLHttpRequest 对象
        xhr.open("post", url, true); //post方式，url为服务器请求地址，true 该参数规定请求是否异步处理。
        if (type == 1) {
            xhr.onload = uploadComplete_for_classification; //请求完成
        }
        if (type == 2) {
            xhr.onload = uploadComplete_for_detection;
        }

        xhr.onerror = uploadFailed; //请求失败

        xhr.upload.onprogress = progressFunction;//【上传进度调用方法实现】
        xhr.upload.onloadstart = function () {//上传开始执行方法
            ot = new Date().getTime();   //设置上传开始时间
            oloaded = 0;//设置上传开始时，以上传的文件大小为0
        };
        xhr.send(form); //开始上传，发送form数据
    }
}

//上传成功响应
function uploadComplete_for_detection(evt) {
    //服务断接收完文件返回的结果
    var response = JSON.parse(evt.target.response);
    console.log(response);
    load_image_to_canvas(image_url_now,
        response.bboxes, response.classes, response.scores,
        response.colors, response.name);
    var _html = "";
    for (var _name in response.colors) {
        var _str = "<div class=\"con\">";
        _str += ("<i style=\"background: " + response.colors[_name] + ";\"></i>\n");
        _str += ("<p style=\"background: " + response.colors[_name] + ";\">" + _name + "</p>");
        _str += "</div>";
        _html += _str;
    }
    document.getElementById("result_show").innerHTML = _html;
    var _html = "<div class=\"row\">\n";
    for (var face in response.face_match) {
        var _str = "<div class=\"col-sm col-md-6 col-lg-4 ftco-animate fadeInUp ftco-animated\">\n";
        _str += "<div class=\"destination\">\n";
        _str += "<a href=\"#\" id=\"circle\" class=\"ec-circle\"\n style=\"cursor: pointer;\" " +
            "onmouseenter=\"addClass(this, 'ec-circle-hover');\"\n" +
            "onmouseleave=\"removeClass(this, 'ec-circle-hover');\">";
        _str += ("<img class=\"ec-circle\" src=\"../../../ProjectShow/media/image/" + response.face_match[face].image_url + "\"width=\"100\" height=\"100\">\n</a>");
        _str += ("<div class=\"text p-4\">\n \n<a>" + response.face_match[face].face_name + "</a>");
        _str += "</div>\n</div>\n</div>";
        _html += _str;
    }
    _html += "</div>\n";
    document.getElementById("face_image").innerHTML = _html;

}

function uploadComplete_for_classification(evt) {
    //服务断接收完文件返回的结果
    var response = JSON.parse(evt.target.response);
    // console.log(response);
    var _html = "";
    for (var _name in response) {
        var _str = "";
        _str += ("<li>" + _name + "-" + response[_name] + "</li>");
        _html += _str;
    }
    document.getElementById("result_show").innerHTML = _html;
}

//上传失败
function uploadFailed(evt) {
    alert("上传失败！");
}

//取消上传
function cancleUploadFile() {
    xhr.abort();
}

//上传进度实现方法，上传过程中会频繁调用该方法
function progressFunction(evt) {
    var progressBar = document.getElementById("progressBar");
    // event.total是需要传输的总字节，event.loaded是已经传输的字节。如果event.lengthComputable不为真，则event.total等于0
    if (evt.lengthComputable) {//
        progressBar.max = evt.total;
        progressBar.value = evt.loaded;
    }
    var time = document.getElementById("time");
    var nt = new Date().getTime();//获取当前时间
    var pertime = (nt - ot) / 1000; //计算出上次调用该方法时到现在的时间差，单位为s
    ot = new Date().getTime(); //重新赋值时间，用于下次计算
    var perload = evt.loaded - oloaded; //计算该分段上传的文件大小，单位b
    oloaded = evt.loaded;//重新赋值已上传文件大小，用以下次计算
    //上传速度计算
    var speed = perload / pertime;//单位b/s
    var bspeed = speed;

    //剩余时间
    // var resttime = ((evt.total-evt.loaded)/bspeed).toFixed(1);
    // time.innerHTML = '，速度：'+speed+units+'，剩余时间：'+resttime+'s';
    if (bspeed == 0) time.innerHTML = '上传已取消';
}


function validate_required(field, alerttxt) {
    with (field) {
        if (value == null || value == "") {
            alert(alerttxt);
            return false
        }
        else {
            return true
        }
    }
}
