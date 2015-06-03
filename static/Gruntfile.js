module.exports = function(grunt) {

    // 项目配置
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),


        // 合并压缩css文件
        cssmin: {
            wechat: {
                files: [
                    {
                        src: [
                            '<%= _src.wechat %>global.css',
                            '<%= _src.wechat %>main.css'
                        ],
                        dest: '<%= _dist.wechat %><%= pkg.vers.wechat %>/common.css'
                    }
                ]
            }
        },

        // js合并
        concat: {
            wechat: {
                files: [
                    {
                        src: [
                            '<%= _lib.wechat %>zepto/zepto.js',
                            '<%= _lib.wechat %>weixin.js',
                            '<%= _src.wechat %>api.js'
                        ],
                        dest: '<%= _build.wechat %><%= pkg.vers.wechat %>/global.js'
                    }
                ]
            }
        },

        // 压缩js文件
        uglify: {
            wechat: {
                files: [
                    {
                        expand: true,
                        cwd: '<%= _build.wechat %><%= pkg.vers.wechat %>',
                        src: ['*.js', '*-debug.js'],
                        dest: '<%= _dist.wechat %><%= pkg.vers.wechat %>/',
                        ext: '.js'
                    }
                ]
            }
        },



        // 线上文件部署
        copy: {
            wechat: {
                files: [
                    {
                        expand: true,
                        cwd: 'dist/wechat/dist/',
                        src: ['**'],
                        dest: 'sea-modules/wechat/<%= pkg.vers.wechat %>/'
                    }
                ]
            }
        },

        // 清理临时文件
        clean: {
            dist: ['assets/dist']
        },

        _src: {
            wechat: 'assets/src/'
        },
        _lib: {
            wechat: 'lib/'
        },
        _build: {
            wechat: 'assets/build/'
        },
        _dist: {
            wechat: 'dist/'
        }
    });


    // 加载 concat 合并依赖
    grunt.loadNpmTasks('grunt-contrib-concat');
    // 加载 uglify 压缩插件(Minify files with UglifyJS)
    grunt.loadNpmTasks('grunt-contrib-uglify');
    // 加载 cssmin 压缩css
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    // 加载 copy 文件复制
    grunt.loadNpmTasks('grunt-contrib-copy');
    // 加载 clean 临时文件清理
    grunt.loadNpmTasks('grunt-contrib-clean');


    // 注册 build
    grunt.registerTask('deploy', ['cssmin:wechat', 'concat:wechat', 'uglify:wechat']);


    grunt.registerTask('css', ['cssmin:wechat']);
    grunt.registerTask('js', ['concat:wechat']);
    grunt.registerTask('jsug', ['uglify:wechat']);

    // 注册 default task(s)别名，代理执行
    grunt.registerTask('default', ['cssmin:wechat', 'concat:wechat', 'uglify:wechat']);
};
