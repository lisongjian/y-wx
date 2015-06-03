window.WX = window.WX || function() {

    var WX = {
        init: function(callback) {
            document.addEventListener('WeixinJSBridgeReady', function() {
                callback();
            }, false);
        },

        // 初始化菜单选项栏
        showMenu: function() {
            function onBridgeReady(){
                 WeixinJSBridge.call('showOptionMenu');
            }

            if (typeof WeixinJSBridge == "undefined"){
                if( document.addEventListener ){
                    document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
                }else if (document.attachEvent){
                    document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
                    document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
                }
            }else{
                onBridgeReady();
            }
        },

        // 初始化菜单选项栏
        hideMenu: function() {
            function onBridgeReady(){
                 WeixinJSBridge.call('hideOptionMenu');
            }

            if (typeof WeixinJSBridge == "undefined"){
                if( document.addEventListener ){
                    document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
                }else if (document.attachEvent){
                    document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
                    document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
                }
            }else{
                onBridgeReady();
            }
        },

        // 分享给朋友
        shareFriend: function(appid, imgUrl, link, desc, title, endUrl) {
            WeixinJSBridge.on('menu:share:appmessage', function() {
                WeixinJSBridge.invoke("sendAppMessage", {
                    appid: appid,// 订阅号
                    img_url: imgUrl,// 分享预览图片
                    img_width: "200",
                    img_height: "200",
                    link: link,
                    desc: desc,
                    title: title
                },
                function(e) {
                    if(endUrl) {
                        document.location.href = endUrl;
                    }
                })
            });
        },

        // 分享到朋友圈
        shareTimeLine: function(imgUrl, link, desc, title, endUrl) {
            WeixinJSBridge.on('menu:share:timeline', function() {
                WeixinJSBridge.invoke("shareTimeline", {
                    img_url: imgUrl,
                    img_width: "200",
                    img_height: "200",
                    link: link,
                    desc: desc,
                    title: title
                },
                function(e) {
                    if(endUrl) {
                        document.location.href = endUrl;
                    }
                })
            });
        },

        // 分享到腾讯微薄
        shareWeibo: function(imgUrl, title, desc, link, endUrl) {
            WeixinJSBridge.invoke("menu:share:timeline", {
                img_url: imgUrl,
                content: title + " " + desc,
                url: link
            },
            function(e) {
                if(endUrl) {
                    document.location.href = endUrl;
                }
            })
        },

        // 提示分享
        showShare: function(img) {
            var shade = document.getElementById('share-wx-shade');
            if(shade) {
                shade.style.display = 'block';
            }
            else {
                var shade = document.createElement('div');
                shade.id = 'share-wx-shade';
                shade.style.cssText = 'width: 100%; height: 100%; background: black; opacity: 0.8; display: block; position: fixed; left: 0; top: 0; z-index: 69980';
                document.body.appendChild(shade);
                shade.onclick = function() {
                    this.style.display = 'none';
                }
                var content = document.createElement('div');
                content.style.cssText = 'position: absolute; right: 10px; top: 5px;width:100%;'
                if(img) {
                    content.innerHTML = '<img src="' + img +  '" style="float: right; width:240px;">';
                }
                else {
                    content.innerHTML = '点击菜单';

                }
                shade.appendChild(content);
                content.onclick = function(e) {
                    // console.log('hello');
                }
            }

        }

    };


    return WX;
}();
