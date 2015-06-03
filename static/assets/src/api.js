/** @preserve Copyright 2010-2014 Youmi.net. All Rights Reserved. */
/**
    通用方法api
    -----------
 */
// define(function(require, exports, module) {
window.API = (function() {

    // var $ = require('zepto'),
    var    win = window,

/** 私有属性
 -----------------------------------------------------------------*/

/** 公有属性&方法
 -----------------------------------------------------------------*/
    API = {
        timestamp  :  0,  // 时间戳
        isIpad: (/ipad/gi).test(navigator.appVersion),


        /**
         *  =effect   效果记录发送
         *
         *  @param    {number}  id    任务id
         *  @param    {number}  at    效果类型
         *  @param    {json}    c     全局参数
         *
        effect_: function(id, at, c) {
            API._ping( API.strFormat('http://ios.wall.youmi.net/v2/jseff?cid={0}&app={1}&rsd={2}&rt={3}&ad={4}&at={5}&prop=wall&e={6}&entc={7}',
                c.cid, c.aid, c.oil, API.timeGap(0) - _mi_hjml, id, at, c.ede, c.entc) );
        },


        /**
         *  =event  事件统计
         *
         *  @param    {number}  val
         *
        event_: function(ac, val, aid, cid, tsp, entc, ver) {
            API._ping( API.strFormat('http://t.youmi.net/v1/event?appid={0}&cid={1}&tsp={2}&ac={3}&pt=i_wall&lb={4}&val={5}&ver={6}', aid, cid, tsp, ac, entc, val, ver) );
        },


        /**
         *  =track  用户统计
         *
         *  @param    {string}  aid
         *  @param    {string}  cid
         *  @param    {string}  sdkv  sdk版本
         *  @param    {string}  pf    平台型号
         *
        track_: function(aid, cid, sdkv, pf) {
            var ft = API.getItem('_mi_ft_wall'),
                ts = 0, t0 = new Date;

            if (ft) {
                ts = API.getItem('_mi_ts_wall');
                // 一天只发一次
                if ( ts > parseInt(new Date(t0.getFullYear(), t0.getMonth(), t0.getDate(), 0, 0, 0) / 1000) ) return false;
            }
            else {
                ft = 0;
            }

            // 发送统计记录
            $.ajax({
                type       :  'GET',
                url        :  'http://t.youmi.net/v1/active',
                data       :  {
                    appid  :  aid,
                    cid    :  cid,
                    dv     :  pf,
                    ts     :  ts,
                    ft     :  ft,
                    pt     :  'i_wall',
                    ver    :  sdkv,
                    osv    :  API._getOSV()
                },
                dataType   :  'json',
                timeout    :  12000,
                success    :  function(d) {
                    if (!d.c) {
                        if (!ft) API.setItem('_mi_ft_wall', d.ft, 7776000); // 缓存3个月
                        API.setItem('_mi_ts_wall', d.ts, 7776000); // 缓存3个月
                    }
                }
            });
        },


        /**
         *  =fixJack  防止劫持
         *
        fixJack: function() {
            document.write = function(str) { return false; };
        },


        /**
         *  =timeGap 获取间隔时间
         *
         *  @param    {number}  when
         *
        timeGap: function(w) {
            if (w) {
                return (new Date).getTime() - this.timestamp;
            }
            else {
                this.timestamp = (new Date).getTime();
                return this.timestamp;
            }
        },


        /**
         *  =getStamp  获取间断时间戳
         *
         *  @param    {number}  w  间断分钟
         *  @return   {number}     时间戳
         *
        getStamp: function(w) {
            var t = new Date();
            t = new Date(t.getFullYear(), t.getMonth(),
                t.getDay(), t.getHours(),  Math.floor(t.getMinutes()/w)*w, 0, 0);
            return t.getTime();
        },


        /**
         *  =getRequest  获取url参数
         *
         *  @return  {object}   参数集合
         */
        getRequest: function()  {
            var url = win.location.search,  // 获取url中"?"后面的字符串
                i = 0,
                args, arg,
                back = {};

            if (url == '') return 0;

            if ( url.indexOf('?') != -1 ) {
                args = url.substr(1).split('&');

                for (; i < args.length; i++) {
                    arg = args[i].split('=');
                    back[ arg[0] ] = arg[1];
                }
            }

            return arguments[0] ? back[arguments[0]] : back;
        },


        /**
         *  =getItem  获取数据
         *
         *  @param    {string}  key  数据名称
         *  @param    {boolean} hl   是否处理数据
         *  @return   {string/json}
         */
        getItem: function(key, hl) {
            hl = hl || 0;
            var value = win.localStorage.getItem(key);
            if (value) {
                return hl ? JSON.parse(value) : value;
            }
            return null;
        },


        /**
         *  =setItem  获取数据
         *
         *  @param    {string}  key    数据名称
         *  @param    {boolean} value  数据
         */
        setItem: function(key, value) {
            if ($.isArray(value) || $.isPlainObject(value)) value = JSON.stringify(value);
            win.localStorage.setItem(key, value);
            return 1;
        },


        /**
         *  获取位置信息
         */
        //getScrollTop: function() { return window.scrollY; }, // 上滚动距离
        getWidth: function() { return screen.width || win.innerWidth; },
        getHeight: function() { return screen.height || win.innerHeight; },


        /**
         *  获取 maxScrollY
         *
         *  @param    {number}  orient   屏幕翻转
         *  @param    {number}  clientH  页面高度
         *
        getMaxScrollY: function(orient, clientH) {
            return orient ?
                (clientH - API.getWidth()) :
                    (clientH - API.getHeight());
        },


        /* 随机数 */
        random: function(n) { return parseInt(Math.random() * n); },


        /**
         *  =encode  字符串 encode
         *
         *  @param    {string}  s 需要 encode 的字符串
         *  @return   {string}
         */
        encode: function(s) { return encodeURIComponent(s); },


        /**
         *  编码decode
         *
         *  @param    {string}  s  需要decode的字符串
         *  @return   {string}
         */
        decode: function(s) { return decodeURIComponent(s); },


        /**
         *  =escape  (包含中文)数据容错处理
         *
         *  @param    {string}  s  需要处理的数据字符串
         *  @return   {json}    c  1，数据为空
         *                         2, 数据无法解析
         */
        escape: function(s) {
            var d = { c: 1 };

            if (!!s) {
                // 数据容错处理
                try {
                    d = s.replace(/(\r\n|\r|\n)/g, '\\n'); // 特殊字符处理
                    d = JSON.parse(d);
                }
                catch(e) {
                    // 输出数据错误信息
                    API._log('Data Error:'+ e);
                    d.c = 2;
                }
            }

            return d;
        },


        /**
         *  数字格式化
         *
         *  @param    {number}  num  需要格式化的string
         */
        numFormat: function(num) {
            // 保留 fixed 小数位数
            num = parseFloat(num).toFixed( (arguments[1] || 0) );

            // 加上逗号
            num += '';
            var x = num.split('.'),
                x1 = x[0],
                x2 = (x.length > 1) ? ('.' + x[1]) : '',
                rgx = /(\d+)(\d{3})/;

            while (rgx.test(x1)) x1 = x1.replace(rgx, '$1' + ',' + '$2');

            return x1 + x2;
        },


        /**
         *  string 格式化
         *
         *  @param    {string}  d    需要格式化的string
         *  @param    {all}     1~n  {n} 替换内容
         *  @return   {string}       格式化后的string
         */
        strFormat: function(s) {
            if (arguments.length == 0) return null;

            var args = Array.prototype.slice.call(arguments, 1);
            return s = s.replace(/\{(\d+)\}/g, function(m, i) {
                return args[i];
            });
        }
    };


    /**
        =template

        ** Usage **

        HTML:
        <script type="text/template" id="tpl-article"><h1>{{title}}</h1></script>

        JavaScript:
        $('#tpl-article').tmpl(data).appendTo($item);
     */
    (function($){
        $.fn.tmpl = function(d) {
            var s = $(this[0]).html().trim();
            if ($.isArray(d)) {
                var li = '',
                    tm = {}, i = 0, len = d.length;

                for (; i < len; i++) {
                    tm = d[i];
                    li += s.replace(/\{\=(\w+)\}/g, function(all, match) {
                        return tm[match];
                    });
                }
                s = li;
            }
            else {
                s = s.replace(/\{\=(\w+)\}/g, function(all, match) {
                    return d[match];
                });
            }

            return $(s);
        };
    })($);

    return API;
// });
    })()
