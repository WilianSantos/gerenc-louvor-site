const sass = require('sass')


module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        // Compilação de arquivos sass
        sass: {
            options: {
                implementation: sass, 
                sourceMap: true,
                outputStyle: 'expanded' // Preserva a estrutura legível       
            },
            dist: {
                files: {
                    './static/dist/css/main.css': './static/src/styles/main.scss' 
                }
            }
        },
        // Compilação de arquivos js
        uglify: {
            target: {
                files: {
                    './static/dist/scripts/main.min.js': './static/src/scripts/**/*.js'
                }
            }
        },
        // Compressão de imagens
        imagemin: {
            dynamic: {
                files: [{
                    expand: true,                   
                    cwd: './static/src/images/',           
                    src: ['**/*.{png,jpg,jpeg,gif,svg,ico}'], 
                    dest: './static/dist/images/'          
                }]
            }
        },
        // Observação de arquivos alterados na etapa de desenvolvimento
        watch: {
            sass: {
                files: ['./static/src/styles/**/*.scss'], 
                tasks: ['sass']              
            },
            uglify: {
                files: ['./static/src/scripts/**/*.js'],
                tasks: ['uglify']
            }
        },
        
    });

    // Carregar dependências
    grunt.loadNpmTasks('grunt-sass')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-uglify')
    grunt.loadNpmTasks('grunt-contrib-imagemin')

    // Tarefas registradas
    grunt.registerTask('default', ['watch'])
    grunt.registerTask('build', ['sass', 'imagemin', 'uglify'])
}