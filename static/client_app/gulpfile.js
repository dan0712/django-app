var gulp = require('gulp');
var ts = require('gulp-typescript');
var merge = require('merge2');
var babel = require('gulp-babel');
var include  = require("gulp-include");
var insert = require('gulp-insert');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');
var stylus = require('gulp-stylus');
var nib = require('nib');



/*
 *  ======================================================================
 *   bundle  third party libraries https://github.com/wiledal/gulp-include
 *  ======================================================================
*/

var vendors_bundle="//=require utils/mixins.js\n\
//=require libs/jquery-2.1.4.js\n\
//=require libs/underscore.js\n\
//=require libs/angular-1.4.js\n\
//=require libs/angular-animate.js\n\
//=require libs/angular-aria.js\n\
//=require libs/angular-messages.js\n\
//=require libs/angular-ui-router.js\n\
//=require libs/angular-material.js\n\
//=require libs/ngMask.js\n\
//=require libs/restangular.js\n\
//=require libs/angular-modal-service.js\n"


var tsProject = ts.createProject('tsconfig.json');

/*
 * Compile betasmartz client app
 */
gulp.task('compile_js_dev', function() {
    var tsResult = gulp.src('src/application.ts').pipe(sourcemaps.init()).pipe(ts(tsProject));

    return merge([ // Merge the two output streams, so this task is finished when the IO of both operations are done.
        tsResult.dts.pipe(gulp.dest('public/definitions')),
        tsResult.js.pipe(babel({ presets: ['es2015']}))
            .pipe(insert.prepend(vendors_bundle))
            .pipe(include())
            .pipe(sourcemaps.write('../js'))
            .pipe(gulp.dest('public/js'))
    ]);
});


/*
 * Compile betasmartz client app (production ready)
 */
gulp.task('compile_js_prod', function() {
    var tsResult = gulp.src('src/application.ts').pipe(sourcemaps.init()).pipe(ts(tsProject));

    return merge([ // Merge the two output streams, so this task is finished when the IO of both operations are done.
        tsResult.dts.pipe(gulp.dest('public/definitions')),
        tsResult.js.pipe(babel({ presets: ['es2015']}))
            .pipe(insert.prepend(vendors_bundle))
            .pipe(include())
            .pipe(uglify())
            .pipe(sourcemaps.write('../js'))
            .pipe(gulp.dest('public/js'))
    ]);
});


/*
 * Publish html files
 */
gulp.task('publish_views', function() {
    gulp.src(["src/views/**/*"]).pipe(gulp.dest('public/views'));

});


// publish css files
gulp.task('compile_css_dev', function () {
    gulp.src('src/stylus/client_app.styl')
        .pipe(stylus({use:nib(), 'include css': true}))
        .pipe(gulp.dest('public/css'));
});


/*
 * Build app (dev)
 */
gulp.task('build_dev', ['publish_views', 'compile_js_dev', 'compile_css_dev']);



/*
 * Build app (production ready)
 */
gulp.task('build_prod', ['publish_views', 'compile_js_prod']);




gulp.task('watch', ['build_dev'], function() {
    gulp.watch('src/**/*', ['build_dev']);
});