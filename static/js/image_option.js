let ctx;
var image_url_now;
const canvas = document.getElementById("rect_canva");
ctx = canvas.getContext("2d");
function load_image_to_canvas(image_url, boxes, classes, scores, color, name){
    document.getElementById("result_show").innerHTML="";
    $(document).ready(function() {
      $("html, body").animate({
          scrollTop: $("#func").offset().top
      }, {duration: 500, easing: "swing"});
    });
    var progressBar = document.getElementById("progressBar");
    // event.total是需要传输的总字节，event.loaded是已经传输的字节。如果event.lengthComputable不为真，则event.total等于0
    progressBar.value = 0;
    const img = new Image();
    // 当图片加载完再动手
    image_url_now = image_url;
    img.onload = function () {
        // 画布大小和图片尺寸不一样算好比例
        const imgWidth = img.naturalWidth, imgHeight = img.naturalHeight;
        canvas.height = imgHeight;
        canvas.width = imgWidth;
        var x = Math.max(canvas.height, canvas.width);
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.style.width = '100%';
        ctx.lineWidth = x/200;
        for (var i=0;i<classes.length;i++)
        {
            var _class = classes[i];
            var _name = name[_class];
            ctx.strokeStyle = color[_name];
            var max_boxes = Math.max(boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]);
            if (max_boxes <= 1.5){
                ctx.strokeRect(
                Math.max(boxes[i][0] * imgWidth, ctx.lineWidth),
                Math.max(boxes[i][1] * imgHeight, ctx.lineWidth),
                (Math.min(boxes[i][2], 1-ctx.lineWidth/imgWidth) - Math.max(boxes[i][0], 0)) * imgWidth,
                (Math.min(boxes[i][3], 1-ctx.lineWidth/imgHeight) - Math.max(boxes[i][1], 0)) * imgHeight)
            }else{
                ctx.strokeRect(
                Math.max(boxes[i][0], ctx.lineWidth),
                Math.max(boxes[i][1], ctx.lineWidth),
                (Math.min(boxes[i][2], imgWidth-ctx.lineWidth) - Math.max(boxes[i][0], 0)),
                (Math.min(boxes[i][3], imgHeight-ctx.lineWidth) - Math.max(boxes[i][1], 0)))
            }
        }
    };
    img.src = image_url;

    // 假设左上角的point 29,24 这是针对原图的坐标系
    // 假设右下角的point 124,52 这是针对原图的坐标系
}


function previewHandle(fileDOM) {
    var file = fileDOM.files[0], // 获取文件
        imageType = /^image\//,
        reader = '';

    // 文件是否为图片
    if (!imageType.test(file.type)) {
        alert("请选择图片！");
        return;
    }
    // 判断是否支持FileReader    
    if (window.FileReader) {
        reader = new FileReader();
    }
    // IE9及以下不支持FileReader
    else {
        alert("您的浏览器不支持图片预览功能，如需该功能请升级您的浏览器！");
        return;
    }
    // 读取完成    
    reader.onload = function (event) {
        // 获取图片DOM
        var img = document.getElementById("rect_canva");
        // 图片路径设置为读取的图片
        load_image_to_canvas(event.target.result); 
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

load_image_to_canvas("../../../ProjectShow/media/image/default_image_for_inception.jpeg",
[], [], [], [], []);