const gulp = require('gulp');
const pckg = require('./package.json');

// Process arguments
const args = require('minimist')(process.argv.slice(1));
const env = args.env || 'development';


// Lint tasks

gulp.task('lint:html', function() {
    const htmlhint = require('gulp-htmlhint');
    return gulp.src(['webpage/**/*.html', '!webpage/**/*.tpl.html', '!webpage/**/*.frame.html'])
        .pipe(htmlhint())
        .pipe(htmlhint.reporter('fail'));
});

gulp.task('lint:js', function() {
    const jshint = require('gulp-jshint');
    return gulp.src(['webpage/**/*.js'])
        .pipe(jshint({ newcap: false, sub: true }))
        .pipe(jshint.reporter('fail'));
});

gulp.task('lint:all', gulp.series('lint:html', 'lint:js'));


// Clean tasks

gulp.task('clean', function() {
    const del = require('del');
    return del(['public/*', 'dist']);
});


// Build tasks

gulp.task('build:css', function() {
    const cssmin = require('gulp-clean-css');
    const rename = require('gulp-rename');
    const mancha = require('gulp-mancha');

    const stream = gulp
        .src(['webpage/**/*.css'])
        .pipe(mancha({
            'theme-primary': pckg.vars.theme.primary,
            'theme-accent': pckg.vars.theme.accent,
            'theme-background': pckg.vars.theme.background,
            'theme-text-on-background': pckg.vars.theme['text-on-background']
        }));

    return stream
        .pipe(cssmin())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest('public'))
});

gulp.task('build:html', function() {
    const fs = require('fs')
    const mancha = require('gulp-mancha')

    const vars = Object.assign({},
        // Dynamically identify variables from package.json
        pckg.vars,

        // Add the name and description from the top-level package
        {name: pckg.displayName, description: pckg.description},

        // Add variables from context
        {env: env, year: new Date().getFullYear()},
    )

    // Perform rendering
    return gulp.src(['webpage/**/*.html', '!webpage/**/*.tpl.html'])
        .pipe(mancha(vars, {
            fs: fs,
            encodeHtmlAttrib: mancha.encodeHtmlAttrib,
            console: console,
            canonical: null
        }))
        .pipe(gulp.dest('public'));
});

gulp.task('build:logo', function() {
    const jimp = require('gulp-jimp');
    const imagesizes = [64, 128, 512];
    return gulp.src('webpage/static/logo.png')
    .pipe(jimp(
        imagesizes.reduce(function(acc, size) {
            acc['-' + size] = {resize: {width: size}};
            return acc;
        }, {})
    ))
    .pipe(gulp.dest('public/static'));
});

gulp.task('build:ts', function() {
    const ts = require('gulp-typescript');
    return gulp.src('webpage/**/*.ts')
        .pipe(ts({
            target: 'ES2015',
            module: 'commonjs',
            declaration: true,
            noImplicitAny: true,
         }))
        .pipe(gulp.dest('dist'));
});

gulp.task('build:all', gulp.series('build:css', 'build:logo', 'build:html', 'build:ts'));


// Copy tasks

gulp.task('copy:static', function() {
    return gulp.src(['webpage/**/*', '!webpage/**/*.ts', '!webpage/**/*.css', '!webpage/**/*.html'])
        .pipe(gulp.dest('public'));
});

gulp.task('copy:output', function() {
    return gulp.src(['output/**/*', '!output/**/*.csv'])
        .pipe(gulp.dest('public'));
});

gulp.task('copy:all', gulp.series('copy:static', 'copy:output'));


// Minification tasks

gulp.task('minify:js', function() {
    const uglify = require('gulp-uglify');
    return gulp.src(['public/**/*.js', '!public/node_modules/**/*'])
        .pipe(uglify())
        .pipe(gulp.dest('public'));
});

gulp.task('minify:html', function() {
    const minify = require('gulp-minify-inline');
    return gulp.src(['public/**/*.html', '!public/node_modules/**/*'])
        .pipe(minify({jsSelector: 'script[data-do-not-minify!=true]'}))
        .pipe(gulp.dest('public'));
});

gulp.task('minify:img', function() {
    const imagemin = require('gulp-imagemin');
    return gulp.src(['webpage/**/*.png', 'webpage/**/*.jpg', 'webpage/**/*.jpeg', 'webpage/**/*.gif'])
        .pipe(imagemin())
        .pipe(gulp.dest('public'));
});

gulp.task('minify:all', gulp.series('minify:js', 'minify:html', 'minify:img'));


// Deploy tasks

gulp.task('firebase', function(callback) {
    const client = require('firebase-tools');
    return client.deploy({
        project: pckg.name,
        token: process.env.FIREBASE_TOKEN
    }).then(function() {
        return callback();
    }).catch(function(err) {
        console.log(err);
        return process.exit(1);
    });
});

// Used to make sure the process ends
gulp.task('exit', function(callback) {
    callback();
    process.exit(0);
});


// High level tasks

gulp.task('build:debug', gulp.series('lint:all', 'build:all', 'copy:all'));
gulp.task('build:prod', gulp.series('build:debug', 'minify:all'));
gulp.task('build', gulp.series('build:prod'));
gulp.task('default', gulp.series('build'));
gulp.task('deploy', gulp.series('firebase', 'exit'));
